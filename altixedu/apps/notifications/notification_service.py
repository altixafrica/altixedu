"""
Email and SMS Notification Service
Uses free/cheap providers for African markets:
- Email: Mailgun (1000 free/month)
- SMS: Africa's Talking (generous free tier)
"""

import logging
import os
from typing import List, Dict, Optional
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service with multiple provider support.
    Primary: Mailgun (1000 free emails/month)
    Fallback: Django SMTP (Gmail, SendGrid, etc.)
    """
    
    PROVIDERS = {
        'mailgun': 'MailgunEmailProvider',
        'smtp': 'SMTPEmailProvider',
        'resend': 'ResendEmailProvider',
    }
    
    def __init__(self):
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Get configured email provider"""
        provider_name = getattr(settings, 'EMAIL_PROVIDER', 'mailgun').lower()
        
        if provider_name == 'mailgun':
            return MailgunEmailProvider()
        elif provider_name == 'resend':
            return ResendEmailProvider()
        else:
            return SMTPEmailProvider()
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: List[Dict] = None) -> bool:
        """
        Send email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML email body (optional)
            attachments: List of dicts with 'filename' and 'content' keys
        
        Returns:
            bool: Success status
        """
        try:
            return self.provider.send(
                to_email=to_email,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments
            )
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_bulk_email(self, recipients: List[str], subject: str, body: str,
                       html_body: Optional[str] = None) -> Dict[str, bool]:
        """
        Send email to multiple recipients.
        
        Returns:
            Dict mapping emails to success status
        """
        results = {}
        for email in recipients:
            results[email] = self.send_email(email, subject, body, html_body)
        return results
    
    def send_template_email(self, to_email: str, template_name: str, 
                           context: Dict, subject: str) -> bool:
        """
        Send email using Django template.
        
        Args:
            to_email: Recipient email
            template_name: Path to template (e.g., 'emails/welcome.html')
            context: Template context variables
            subject: Email subject
        """
        try:
            html_body = render_to_string(template_name, context)
            return self.send_email(
                to_email=to_email,
                subject=subject,
                body=subject,  # Fallback plain text
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            return False


class MailgunEmailProvider:
    """
    Mailgun provider - FREE: 1000 emails/month
    Perfect for 10 schools (~100 emails/school/month)
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'MAILGUN_API_KEY', None)
        self.domain = getattr(settings, 'MAILGUN_DOMAIN', None)
        self.sender = getattr(settings, 'MAILGUN_SENDER_EMAIL', 'noreply@altixedu.com')
        
        if not self.api_key or not self.domain:
            raise ValueError("MAILGUN_API_KEY and MAILGUN_DOMAIN must be set")
    
    def send(self, to_email: str, subject: str, body: str, 
             html_body: Optional[str] = None, attachments: List[Dict] = None) -> bool:
        """Send via Mailgun API"""
        try:
            import requests
            
            url = f"https://api.mailgun.net/v3/{self.domain}/messages"
            
            data = {
                "from": self.sender,
                "to": to_email,
                "subject": subject,
                "text": body,
            }
            
            if html_body:
                data["html"] = html_body
            
            auth = ("api", self.api_key)
            
            response = requests.post(url, auth=auth, data=data)
            
            if response.status_code == 200:
                logger.info(f"Email sent to {to_email} via Mailgun")
                return True
            else:
                logger.error(f"Mailgun error {response.status_code}: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Mailgun send failed: {str(e)}")
            return False


class ResendEmailProvider:
    """
    Resend provider - FREE: 50 emails/day + paid after
    Good alternative: resend.com
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        self.sender = getattr(settings, 'RESEND_SENDER_EMAIL', 'noreply@altixedu.com')
        
        if not self.api_key:
            raise ValueError("RESEND_API_KEY must be set")
    
    def send(self, to_email: str, subject: str, body: str,
             html_body: Optional[str] = None, attachments: List[Dict] = None) -> bool:
        """Send via Resend API"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from": self.sender,
                "to": to_email,
                "subject": subject,
                "text": body,
            }
            
            if html_body:
                payload["html"] = html_body
            
            response = requests.post(
                "https://api.resend.com/emails",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent to {to_email} via Resend")
                return True
            else:
                logger.error(f"Resend error: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Resend send failed: {str(e)}")
            return False


class SMTPEmailProvider:
    """
    Standard Django SMTP provider
    Use with Gmail, SendGrid, or any SMTP server
    """
    
    def send(self, to_email: str, subject: str, body: str,
             html_body: Optional[str] = None, attachments: List[Dict] = None) -> bool:
        """Send via Django email backend"""
        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@altixedu.com'),
                to=[to_email]
            )
            
            if html_body:
                email.attach_alternative(html_body, "text/html")
            
            if attachments:
                for attachment in attachments:
                    email.attach(attachment['filename'], attachment['content'])
            
            email.send()
            logger.info(f"Email sent to {to_email} via SMTP")
            return True
        
        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            return False


class SMSService:
    """
    SMS service with multiple provider support.
    Primary: Africa's Talking (popular in Africa, generous free tier)
    Fallback: Termii (Nigerian SMS service)
    """
    
    PROVIDERS = {
        'africas_talking': 'AfricasTalkingSMSProvider',
        'termii': 'TermiiSMSProvider',
        'aws_sns': 'AWSSNSSMSProvider',
    }
    
    def __init__(self):
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Get configured SMS provider"""
        provider_name = getattr(settings, 'SMS_PROVIDER', 'africas_talking').lower()
        
        if provider_name == 'africas_talking':
            return AfricasTalkingSMSProvider()
        elif provider_name == 'termii':
            return TermiiSMSProvider()
        elif provider_name == 'aws_sns':
            return AWSSNSSMSProvider()
        else:
            # Default to Africa's Talking
            return AfricasTalkingSMSProvider()
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS.
        
        Args:
            phone_number: Phone number with country code (e.g., +234801234567)
            message: SMS message text (max 160 chars recommended)
        
        Returns:
            bool: Success status
        """
        try:
            return self.provider.send(phone_number, message)
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return False
    
    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> Dict[str, bool]:
        """
        Send SMS to multiple recipients.
        
        Returns:
            Dict mapping phone numbers to success status
        """
        results = {}
        for phone in phone_numbers:
            results[phone] = self.send_sms(phone, message)
        return results


class AfricasTalkingSMSProvider:
    """
    Africa's Talking SMS provider
    FREE: Test credits available, then ~$0.02-0.05 per SMS
    Perfect for Africa (operates in 150+ countries)
    
    Signup: https://africastalking.com/
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'AFRICAS_TALKING_API_KEY', None)
        self.username = getattr(settings, 'AFRICAS_TALKING_USERNAME', 'sandbox')
        self.sender_id = getattr(settings, 'AFRICAS_TALKING_SENDER_ID', 'AltixEdu')
        
        if not self.api_key:
            raise ValueError("AFRICAS_TALKING_API_KEY must be set")
    
    def send(self, phone_number: str, message: str) -> bool:
        """Send SMS via Africa's Talking"""
        try:
            import requests
            
            headers = {
                "Accept": "application/json",
                "Content-type": "application/x-www-form-urlencoded",
                "apiKey": self.api_key,
            }
            
            data = {
                "username": self.username,
                "to": phone_number,
                "message": message,
                "from": self.sender_id,
            }
            
            response = requests.post(
                "https://api.sandbox.africastalking.com/version1/messaging",
                headers=headers,
                data=data
            )
            
            if response.status_code == 201:
                logger.info(f"SMS sent to {phone_number} via Africa's Talking")
                return True
            else:
                logger.error(f"Africa's Talking error: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Africa's Talking send failed: {str(e)}")
            return False


class TermiiSMSProvider:
    """
    Termii SMS provider
    Popular in Nigeria/Africa
    Very cheap SMS rates
    
    Signup: https://termii.com/
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'TERMII_API_KEY', None)
        self.sender_id = getattr(settings, 'TERMII_SENDER_ID', 'AltixEdu')
        
        if not self.api_key:
            raise ValueError("TERMII_API_KEY must be set")
    
    def send(self, phone_number: str, message: str) -> bool:
        """Send SMS via Termii"""
        try:
            import requests
            
            payload = {
                "to": phone_number,
                "from": self.sender_id,
                "sms": message,
                "type": "plain",
                "api_key": self.api_key,
            }
            
            response = requests.post(
                "https://api.ng.termii.com/api/sms/send",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"SMS sent to {phone_number} via Termii")
                return True
            else:
                logger.error(f"Termii error: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Termii send failed: {str(e)}")
            return False


class AWSSNSSMSProvider:
    """
    AWS SNS SMS provider
    CHEAP: ~$0.00645 per SMS (Africa rates vary)
    Reliable and scalable
    """
    
    def __init__(self):
        import boto3
        self.sns_client = boto3.client(
            'sns',
            region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
        )
    
    def send(self, phone_number: str, message: str) -> bool:
        """Send SMS via AWS SNS"""
        try:
            response = self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': getattr(settings, 'AWS_SNS_SENDER_ID', 'AltixEdu')
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(f"SMS sent to {phone_number} via AWS SNS")
            return True
        
        except Exception as e:
            logger.error(f"AWS SNS send failed: {str(e)}")
            return False


# Convenience functions
email_service = EmailService()
sms_service = SMSService()


def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
    """Quick email send"""
    return email_service.send_email(to_email, subject, body, html_body)


def send_sms(phone_number: str, message: str) -> bool:
    """Quick SMS send"""
    return sms_service.send_sms(phone_number, message)
