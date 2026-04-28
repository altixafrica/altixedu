"""
Email notification utilities for billing system.
Handles sending payment receipts, invoices, and billing alerts via email.
"""

import logging
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal

logger = logging.getLogger(__name__)


class EmailNotificationError(Exception):
    """Raised when email notification fails."""
    pass


def send_payment_receipt(payment_transaction, invoice=None):
    """
    Send payment receipt email to school admin.
    
    Args:
        payment_transaction: PaymentTransaction instance
        invoice: Invoice instance (optional)
    """
    try:
        subscription = payment_transaction.subscription
        school = subscription.school
        user = school.admin  # Assuming school has an admin relationship
        
        if not user or not user.email:
            logger.warning(f"No email found for school {school.id}")
            return False
        
        subject = f"Payment Receipt - {school.name} - ₦{payment_transaction.amount:,.0f}"
        
        context = {
            'school_name': school.name,
            'amount': float(payment_transaction.amount),
            'currency': payment_transaction.currency,
            'transaction_id': payment_transaction.transaction_id,
            'payment_method': payment_transaction.get_payment_method_display(),
            'date': payment_transaction.completed_at,
            'invoice_number': invoice.invoice_number if invoice else None,
            'status': payment_transaction.get_status_display(),
        }
        
        # Create email content
        html_message = f"""
        <h2>Payment Receipt</h2>
        <p>Dear {school.name},</p>
        <p>Thank you for your payment. Here are the receipt details:</p>
        
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Transaction ID:</strong></td>
                <td style="padding: 10px;">{context['transaction_id']}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Amount:</strong></td>
                <td style="padding: 10px;">₦{context['amount']:,.2f}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Payment Method:</strong></td>
                <td style="padding: 10px;">{context['payment_method']}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Date:</strong></td>
                <td style="padding: 10px;">{context['date']}</td>
            </tr>
            <tr>
                <td style="padding: 10px;"><strong>Status:</strong></td>
                <td style="padding: 10px;"><strong>{context['status']}</strong></td>
            </tr>
        </table>
        
        <p style="margin-top: 20px;">If you have any questions, please contact our support team.</p>
        <p>Best regards,<br>AltixEdu Team</p>
        """
        
        plain_message = strip_tags(html_message)
        
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            html_message=html_message,
        )
        
        email.send()
        logger.info(f"Payment receipt sent to {user.email} for transaction {payment_transaction.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment receipt: {str(e)}")
        raise EmailNotificationError(f"Failed to send payment receipt: {str(e)}")


def send_invoice_email(invoice):
    """
    Send invoice email with PDF attachment.
    
    Args:
        invoice: Invoice instance
    """
    try:
        from .pdf_utils import generate_invoice_pdf
        
        subscription = invoice.subscription
        school = subscription.school
        user = school.admin
        
        if not user or not user.email:
            logger.warning(f"No email found for school {school.id}")
            return False
        
        subject = f"Invoice #{invoice.invoice_number} - {school.name}"
        
        html_message = f"""
        <h2>Invoice #{invoice.invoice_number}</h2>
        <p>Dear {school.name},</p>
        <p>Please find attached your invoice for the billing period.</p>
        
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Invoice Number:</strong></td>
                <td style="padding: 10px;">{invoice.invoice_number}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Amount:</strong></td>
                <td style="padding: 10px;">₦{invoice.amount:,.2f}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Issued:</strong></td>
                <td style="padding: 10px;">{invoice.issued_at}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Due Date:</strong></td>
                <td style="padding: 10px;">{invoice.due_at}</td>
            </tr>
            <tr>
                <td style="padding: 10px;"><strong>Status:</strong></td>
                <td style="padding: 10px;"><strong>{invoice.get_status_display()}</strong></td>
            </tr>
        </table>
        
        <p style="margin-top: 20px;">Please make payment by the due date to avoid service interruption.</p>
        <p>Best regards,<br>AltixEdu Team</p>
        """
        
        plain_message = strip_tags(html_message)
        
        # Generate PDF
        pdf_bytes = generate_invoice_pdf(invoice)
        
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            html_message=html_message,
        )
        
        # Attach PDF
        email.attach(
            f"Invoice_{invoice.invoice_number}.pdf",
            pdf_bytes,
            "application/pdf"
        )
        
        email.send()
        
        # Mark as email sent
        invoice.email_sent = True
        invoice.save(update_fields=['email_sent'])
        
        logger.info(f"Invoice email sent to {user.email} for invoice {invoice.invoice_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send invoice email: {str(e)}")
        raise EmailNotificationError(f"Failed to send invoice email: {str(e)}")


def send_payment_failure_notification(payment_transaction, failure_reason):
    """
    Send payment failure notification email.
    
    Args:
        payment_transaction: PaymentTransaction instance
        failure_reason: Reason for payment failure
    """
    try:
        subscription = payment_transaction.subscription
        school = subscription.school
        user = school.admin
        
        if not user or not user.email:
            logger.warning(f"No email found for school {school.id}")
            return False
        
        subject = f"Payment Failed - Action Required - {school.name}"
        
        html_message = f"""
        <h2 style="color: #d9534f;">Payment Failed</h2>
        <p>Dear {school.name},</p>
        <p>Your recent payment attempt has failed. Please review the details below and retry.</p>
        
        <table style="border-collapse: collapse; width: 100%; background-color: #fff3cd;">
            <tr>
                <td style="padding: 15px;">
                    <strong>Reason:</strong> {failure_reason}
                </td>
            </tr>
        </table>
        
        <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Transaction ID:</strong></td>
                <td style="padding: 10px;">{payment_transaction.transaction_id}</td>
            </tr>
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><strong>Amount:</strong></td>
                <td style="padding: 10px;">₦{payment_transaction.amount:,.2f}</td>
            </tr>
            <tr>
                <td style="padding: 10px;"><strong>Date Attempted:</strong></td>
                <td style="padding: 10px;">{payment_transaction.created_at}</td>
            </tr>
        </table>
        
        <p style="margin-top: 20px; color: #d9534f;"><strong>Action Required:</strong> Please update your payment method and retry immediately to avoid service interruption.</p>
        <p>Best regards,<br>AltixEdu Team</p>
        """
        
        plain_message = strip_tags(html_message)
        
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            html_message=html_message,
        )
        
        email.send()
        logger.info(f"Payment failure notification sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment failure notification: {str(e)}")
        raise EmailNotificationError(f"Failed to send payment failure notification: {str(e)}")


def send_billing_alert(alert):
    """
    Send billing alert email.
    
    Args:
        alert: BillingAlert instance
    """
    try:
        subscription = alert.subscription
        school = subscription.school
        user = school.admin
        
        if not user or not user.email:
            logger.warning(f"No email found for school {school.id}")
            return False
        
        alert_color = "#d9534f" if alert.alert_type == "payment_failed" else "#f0ad4e"
        subject = f"Billing Alert - {school.name}"
        
        html_message = f"""
        <h2 style="color: {alert_color};">Billing Alert</h2>
        <p>Dear {school.name},</p>
        <p>{alert.message}</p>
        
        <p style="margin-top: 20px;">Please take action as soon as possible to avoid service disruption.</p>
        <p>Best regards,<br>AltixEdu Team</p>
        """
        
        plain_message = strip_tags(html_message)
        
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            html_message=html_message,
        )
        
        email.send()
        
        # Mark as email sent
        alert.email_sent = True
        alert.save(update_fields=['email_sent'])
        
        logger.info(f"Billing alert sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send billing alert: {str(e)}")
        raise EmailNotificationError(f"Failed to send billing alert: {str(e)}")
