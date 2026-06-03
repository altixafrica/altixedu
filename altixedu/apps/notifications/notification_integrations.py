"""
Notification Integration with Django Models
Sends emails for announcements, messages, alerts, etc.
Email-only implementation (no SMS at this time).
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.notifications.models import Message, Announcement
from apps.notifications.notification_service import email_service
from apps.notifications.email_templates import (
    send_welcome_email,
    send_announcement_email,
    send_payment_receipt_email,
    send_grade_notification_email
)
from apps.accounts.models import User
from apps.accounts.role_models import ParentStudentLink

logger = logging.getLogger(__name__)


def send_announcement_notification(announcement):
    """
    Send announcement to all recipients via email.
    
    Respects user notification preferences.
    """
    # Get recipients based on target role
    if announcement.target_role == 'all':
        recipients = User.objects.filter(school=announcement.school)
    elif announcement.target_role == 'student':
        recipients = User.objects.filter(school=announcement.school, role='student')
    elif announcement.target_role == 'teacher':
        recipients = User.objects.filter(school=announcement.school, role='teacher')
    elif announcement.target_role == 'parent':
        recipients = User.objects.filter(school=announcement.school, role='parent')
    elif announcement.target_role == 'admin':
        recipients = User.objects.filter(school=announcement.school, role='admin')
    else:
        recipients = []
    
    email_count = 0
    
    for user in recipients:
        # Check notification preferences
        if not user.notification_preferences.email_enabled:
            continue
        if not user.notification_preferences.announcements_enabled:
            continue
        
        # Send email
        if user.email:
            success = send_announcement_email(user.email, announcement)
            if success:
                email_count += 1
    
    logger.info(
        f"Announcement {announcement.id} sent to {email_count} email(s)"
    )
    
    return {'emails': email_count}


def send_message_notification(message):
    """Send notification for direct messages via email"""
    recipient = message.recipient
    
    # Check preferences
    if not recipient.notification_preferences.email_enabled:
        return False
    if not recipient.notification_preferences.messages_enabled:
        return False
    
    if not recipient.email:
        return False
    
    success = email_service.send_email(
        to_email=recipient.email,
        subject=f"💬 New message from {message.sender.get_full_name()}",
        body=f"You have a new message from {message.sender.get_full_name()}: {message.content}",
        html_body=f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Message</h2>
                <p><strong>From:</strong> {message.sender.get_full_name()}</p>
                <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #006699;">
                    {message.content}
                </div>
                <p><a href="https://altixedu.com/app/messages/">Reply to this message</a></p>
            </body>
        </html>
        """
    )
    
    return success


def send_grade_notification(exam_result):
    """Send notification to student and parents about grade via email"""
    student = exam_result.student
    
    # Notify student
    if student.user and student.user.email:
        if student.user.notification_preferences.email_enabled and student.user.notification_preferences.grades_enabled:
            send_grade_notification_email(
                recipient_email=student.user.email,
                student_name=student.get_full_name() or student.first_name,
                subject_name=exam_result.subject.name,
                score=exam_result.score,
                grade=exam_result.get_grade() if hasattr(exam_result, 'get_grade') else 'N/A'
            )
    
    # Notify parents
    parent_links = ParentStudentLink.objects.filter(
        student=student,
        receives_progress_reports=True,
        is_active=True
    )
    
    for parent_link in parent_links:
        parent = parent_link.parent
        if parent.email:
            if parent.notification_preferences.email_enabled and parent.notification_preferences.grades_enabled:
                send_grade_notification_email(
                    recipient_email=parent.email,
                    student_name=f"{student.first_name}'s",
                    subject_name=exam_result.subject.name,
                    score=exam_result.score,
                    grade=exam_result.get_grade() if hasattr(exam_result, 'get_grade') else 'N/A'
                )


def send_payment_receipt_notification(payment_receipt):
    """Send payment receipt email to payer and parents"""
    student = payment_receipt.student
    
    # Send to student
    if student.user and student.user.email:
        if student.user.notification_preferences.email_enabled:
            send_payment_receipt_email(student.user.email, payment_receipt)
    
    # Send to primary parent
    primary_parent_link = ParentStudentLink.objects.filter(
        student=student,
        is_primary=True,
        is_active=True
    ).first()
    
    if primary_parent_link and primary_parent_link.parent.email:
        if primary_parent_link.parent.notification_preferences.email_enabled:
            send_payment_receipt_email(primary_parent_link.parent.email, payment_receipt)


def send_fee_reminder(student):
    """Send fee payment reminder via email"""
    from apps.finance.models import StudentFee
    
    # Calculate total due
    fees_due = StudentFee.objects.filter(
        student=student,
        paid=False
    ).values_list('fee__amount', flat=True)
    
    total_due = sum(fees_due) if fees_due else 0
    
    if total_due > 0:
        # Notify student
        if student.user and student.user.email:
            if student.user.notification_preferences.email_enabled and student.user.notification_preferences.fees_enabled:
                email_service.send_email(
                    to_email=student.user.email,
                    subject="💰 Outstanding Fee Balance",
                    body=f"You have ₦{total_due:,.0f} in outstanding school fees. Please make payment to avoid suspension.",
                    html_body=f"""
                    <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2>Outstanding Fee Balance</h2>
                            <p>Hi {student.first_name},</p>
                            <p>You have an outstanding balance of <strong>₦{total_due:,.0f}</strong> for school fees.</p>
                            <p>Please make payment at your earliest convenience to avoid suspension of services.</p>
                            <p style="color: #666; font-size: 12px;">© 2026 AltixEdu</p>
                        </body>
                    </html>
                    """
                )
        
        # Notify primary parent
        parent_link = ParentStudentLink.objects.filter(
            student=student,
            is_primary=True,
            is_active=True
        ).first()
        
        if parent_link and parent_link.parent.email:
            if parent_link.parent.notification_preferences.email_enabled and parent_link.parent.notification_preferences.fees_enabled:
                email_service.send_email(
                    to_email=parent_link.parent.email,
                    subject=f"💰 Your child's outstanding fee balance",
                    body=f"{student.first_name} has ₦{total_due:,.0f} in outstanding school fees.",
                    html_body=f"""
                    <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2>Outstanding Fee Balance</h2>
                            <p>Your child {student.first_name} has an outstanding balance of <strong>₦{total_due:,.0f}</strong> for school fees.</p>
                            <p>Please make payment at your earliest convenience.</p>
                            <p style="color: #666; font-size: 12px;">© 2026 AltixEdu</p>
                        </body>
                    </html>
                    """
                )


def send_attendance_alert(attendance):
    """Send alert for poor attendance via email"""
    from apps.attendance.models import Attendance
    
    student = attendance.student
    
    # Calculate recent absence percentage (last 10 days)
    ten_days_ago = timezone.now() - timedelta(days=10)
    recent_attendances = Attendance.objects.filter(
        student=student,
        date__gte=ten_days_ago.date()
    )
    
    if recent_attendances.exists():
        absent_count = recent_attendances.filter(status='absent').count()
        total_count = recent_attendances.count()
        attendance_rate = (total_count - absent_count) / total_count * 100 if total_count > 0 else 100
        
        # Alert if below 80%
        if attendance_rate < 80:
            # Notify parent
            parent_link = ParentStudentLink.objects.filter(
                student=student,
                is_primary=True,
                is_active=True
            ).first()
            
            if parent_link and parent_link.parent.email:
                if parent_link.parent.notification_preferences.email_enabled and parent_link.parent.notification_preferences.attendance_enabled:
                    email_service.send_email(
                        to_email=parent_link.parent.email,
                        subject=f"⚠️ {student.first_name}'s Low Attendance Alert",
                        body=f"{student.first_name}'s attendance is at {attendance_rate:.0f}%. Please contact the school.",
                        html_body=f"""
                        <html>
                            <body style="font-family: Arial, sans-serif;">
                                <h2>⚠️ Attendance Alert</h2>
                                <p>{student.first_name}'s attendance rate is currently <strong>{attendance_rate:.0f}%</strong>.</p>
                                <p>This is below the school's expected threshold of 80%.</p>
                                <p>Please contact the school to discuss this matter.</p>
                                <p style="color: #666; font-size: 12px;">© 2026 AltixEdu</p>
                            </body>
                        </html>
                        """
                    )


# Signal handlers (optional - auto-send on creation)
@receiver(post_save, sender=Announcement)
def announcement_created(sender, instance, created, **kwargs):
    """Automatically send announcement when created"""
    if created and getattr(settings, 'AUTO_SEND_ANNOUNCEMENTS', True):
        send_announcement_notification(instance)


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """Automatically send message notification when created"""
    if created and getattr(settings, 'AUTO_SEND_MESSAGE_NOTIFICATIONS', True):
        send_message_notification(instance)
