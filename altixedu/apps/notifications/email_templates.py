"""
Email notification templates and utilities.
Only using email for now (no SMS).
"""

import logging
from django.conf import settings
from apps.notifications.notification_service import email_service

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Base class for email templates"""
    
    subject = ""
    
    @staticmethod
    def render_html(context):
        """Override in subclass to render HTML"""
        return ""
    
    @staticmethod
    def render_text(context):
        """Override in subclass to render plain text"""
        return ""


class WelcomeEmailTemplate(EmailTemplate):
    """Welcome email for new users"""
    
    subject = "Welcome to AltixEdu"
    
    @staticmethod
    def render_html(context):
        name = context.get('name', 'User')
        email = context.get('email', '')
        password = context.get('password', 'your-password')
        login_url = context.get('login_url', 'https://altixedu.com/login')
        
        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Inter, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #003366 0%, #006699 100%); color: white; padding: 20px; border-radius: 8px; }}
                    .content {{ margin: 20px 0; line-height: 1.6; }}
                    .button {{ display: inline-block; background: #006699; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin: 20px 0; }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to AltixEdu! 🎓</h1>
                    </div>
                    
                    <div class="content">
                        <p>Hi {name},</p>
                        
                        <p>Your account has been created successfully on AltixEdu, the all-in-one school management platform.</p>
                        
                        <p><strong>Your Login Details:</strong></p>
                        <ul>
                            <li><strong>Email:</strong> {email}</li>
                            <li><strong>Temporary Password:</strong> {password}</li>
                        </ul>
                        
                        <p>Please change your password on first login for security.</p>
                        
                        <a href="{login_url}" class="button">Login to AltixEdu</a>
                        
                        <p><strong>Features Available:</strong></p>
                        <ul>
                            <li>📊 Student Performance Dashboard</li>
                            <li>📝 Assignment Management</li>
                            <li>💬 Messaging & Communication</li>
                            <li>📞 Real-time Notifications</li>
                            <li>💰 Fee Management & Tracking</li>
                            <li>📅 Attendance Tracking</li>
                        </ul>
                        
                        <p>If you have any questions, contact your school administrator.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2026 AltixEdu. All rights reserved.</p>
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
    
    @staticmethod
    def render_text(context):
        name = context.get('name', 'User')
        email = context.get('email', '')
        password = context.get('password', 'your-password')
        
        return f"""
Welcome to AltixEdu!

Hi {name},

Your account has been created successfully.

Login Details:
Email: {email}
Temporary Password: {password}

Please change your password on first login.

Login here: https://altixedu.com/login

If you have any questions, contact your school administrator.

© 2026 AltixEdu
        """


class AnnouncementEmailTemplate(EmailTemplate):
    """Announcement notification email"""
    
    subject = "📢 New Announcement"
    
    @staticmethod
    def render_html(context):
        title = context.get('title', 'New Announcement')
        content = context.get('content', '')
        sender = context.get('sender', 'Admin')
        date = context.get('date', '')
        
        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Inter, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #006699; color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-left: 4px solid #006699; margin: 20px 0; }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>📢 {title}</h2>
                    </div>
                    
                    <div class="content">
                        {content}
                    </div>
                    
                    <p><strong>From:</strong> {sender}</p>
                    <p><strong>Date:</strong> {date}</p>
                    
                    <div class="footer">
                        <p>© 2026 AltixEdu</p>
                    </div>
                </div>
            </body>
        </html>
        """


class PaymentReceiptEmailTemplate(EmailTemplate):
    """Payment receipt email"""
    
    subject = "💳 Payment Receipt"
    
    @staticmethod
    def render_html(context):
        receipt_number = context.get('receipt_number', 'RCP-00000')
        student_name = context.get('student_name', 'Student')
        amount = context.get('amount', 0)
        date = context.get('date', '')
        method = context.get('method', 'Cash')
        school_name = context.get('school_name', 'School')
        
        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Inter, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .receipt {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .receipt-header {{ text-align: center; border-bottom: 2px solid #006699; padding-bottom: 15px; margin-bottom: 20px; }}
                    .row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 10px 0; border-bottom: 1px solid #eee; }}
                    .label {{ font-weight: bold; }}
                    .amount {{ text-align: right; }}
                    .total {{ background: #f0f7ff; padding: 15px; border-radius: 6px; font-size: 18px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="receipt">
                        <div class="receipt-header">
                            <h2>{school_name}</h2>
                            <p>Payment Receipt</p>
                        </div>
                        
                        <div class="row">
                            <span class="label">Receipt #:</span>
                            <span>{receipt_number}</span>
                        </div>
                        
                        <div class="row">
                            <span class="label">Student:</span>
                            <span>{student_name}</span>
                        </div>
                        
                        <div class="row">
                            <span class="label">Payment Method:</span>
                            <span>{method}</span>
                        </div>
                        
                        <div class="row">
                            <span class="label">Date:</span>
                            <span>{date}</span>
                        </div>
                        
                        <div class="total">
                            <div class="row">
                                <span>Amount Paid:</span>
                                <span class="amount">₦{amount:,.0f}</span>
                            </div>
                        </div>
                        
                        <p style="color: #666; font-size: 14px;">Thank you for your payment. Please keep this receipt for your records.</p>
                    </div>
                    
                    <div class="footer">
                        <p>© 2026 AltixEdu - School Management Platform</p>
                        <p>This is an automated receipt. Do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """


class GradeNotificationEmailTemplate(EmailTemplate):
    """Grade update notification email"""
    
    subject = "📊 Grade Posted"
    
    @staticmethod
    def render_html(context):
        student_name = context.get('student_name', 'Student')
        subject_name = context.get('subject_name', 'Subject')
        score = context.get('score', 0)
        grade = context.get('grade', 'N/A')
        
        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Inter, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #28a745; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                    .score {{ font-size: 48px; font-weight: bold; }}
                    .content {{ margin: 20px 0; line-height: 1.6; }}
                    .badge {{ display: inline-block; background: #e7f3ff; color: #006699; padding: 8px 16px; border-radius: 20px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Your Grade is Ready!</h2>
                    </div>
                    
                    <div class="content">
                        <p>Hi {student_name},</p>
                        
                        <p>Your grade for <strong>{subject_name}</strong> has been posted.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <div class="score">{score}</div>
                            <div class="badge">{grade}</div>
                        </div>
                        
                        <p>View more details in your AltixEdu dashboard.</p>
                    </div>
                    
                    <div style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                        <p>© 2026 AltixEdu</p>
                    </div>
                </div>
            </body>
        </html>
        """


def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        context = {
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'login_url': f"{settings.FRONTEND_APP_URL}/login" if hasattr(settings, 'FRONTEND_APP_URL') else 'https://altixedu.com/login',
        }
        
        success = email_service.send_email(
            to_email=user.email,
            subject=WelcomeEmailTemplate.subject,
            body=WelcomeEmailTemplate.render_text(context),
            html_body=WelcomeEmailTemplate.render_html(context)
        )
        
        if success:
            logger.info(f"Welcome email sent to {user.email}")
        else:
            logger.error(f"Failed to send welcome email to {user.email}")
        
        return success
    except Exception as e:
        logger.error(f"Error sending welcome email to {user.email}: {str(e)}")
        return False


def send_announcement_email(recipient_email, announcement):
    """Send announcement email"""
    try:
        context = {
            'title': announcement.title,
            'content': announcement.content,
            'sender': announcement.created_by.get_full_name(),
            'date': announcement.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        
        success = email_service.send_email(
            to_email=recipient_email,
            subject=f"📢 {announcement.title}",
            body=AnnouncementEmailTemplate.render_text(context),
            html_body=AnnouncementEmailTemplate.render_html(context)
        )
        
        return success
    except Exception as e:
        logger.error(f"Error sending announcement email: {str(e)}")
        return False


def send_payment_receipt_email(recipient_email, payment_receipt):
    """Send payment receipt email"""
    try:
        context = {
            'receipt_number': payment_receipt.receipt_number,
            'student_name': f"{payment_receipt.student.first_name} {payment_receipt.student.last_name}",
            'amount': payment_receipt.amount,
            'date': payment_receipt.payment_date.strftime('%Y-%m-%d %H:%M'),
            'method': payment_receipt.get_payment_method_display(),
            'school_name': payment_receipt.school.name,
        }
        
        success = email_service.send_email(
            to_email=recipient_email,
            subject=f"💳 Payment Receipt - {payment_receipt.receipt_number}",
            body=PaymentReceiptEmailTemplate.render_text(context),
            html_body=PaymentReceiptEmailTemplate.render_html(context)
        )
        
        if success:
            logger.info(f"Payment receipt email sent to {recipient_email}")
        
        return success
    except Exception as e:
        logger.error(f"Error sending payment receipt email: {str(e)}")
        return False


def send_grade_notification_email(recipient_email, student_name, subject_name, score, grade):
    """Send grade notification email"""
    try:
        context = {
            'student_name': student_name,
            'subject_name': subject_name,
            'score': score,
            'grade': grade,
        }
        
        success = email_service.send_email(
            to_email=recipient_email,
            subject=f"📊 Grade Posted - {subject_name}",
            body=GradeNotificationEmailTemplate.render_text(context),
            html_body=GradeNotificationEmailTemplate.render_html(context)
        )
        
        return success
    except Exception as e:
        logger.error(f"Error sending grade notification email: {str(e)}")
        return False
