"""
Payment Receipt Generator
Generates PDF receipts for student fee payments using reportlab.
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import PaymentReceipt


def generate_payment_receipt_pdf(payment_receipt):
    """
    Generate PDF receipt for a payment.
    
    Args:
        payment_receipt: PaymentReceipt instance
    
    Returns:
        BytesIO object with PDF content
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    
    # Container for PDF elements
    elements = []
    
    # Setup styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066CC'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    
    # 1. Header with school name
    school = payment_receipt.school
    elements.append(Paragraph(school.name, title_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    # 2. Receipt title
    elements.append(Paragraph("PAYMENT RECEIPT", heading_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # 3. Receipt details table
    receipt_details = [
        ['Receipt Number:', payment_receipt.receipt_number],
        ['Receipt Date:', payment_receipt.payment_date.strftime('%Y-%m-%d %H:%M:%S')],
        ['Payment Date:', payment_receipt.payment_date.strftime('%Y-%m-%d')],
    ]
    
    receipt_table = Table(receipt_details, colWidths=[2 * inch, 2.5 * inch])
    receipt_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # 4. Student information
    elements.append(Paragraph("Student Information", heading_style))
    student = payment_receipt.student
    student_details = [
        ['Student Name:', f"{student.first_name} {student.last_name}"],
        ['Admission Number:', student.admission_number],
        ['Class/Grade:', student.classroom_assignment.classroom.name if hasattr(student, 'classroom_assignment') else 'N/A'],
    ]
    
    student_table = Table(student_details, colWidths=[2 * inch, 2.5 * inch])
    student_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # 5. Payment information
    elements.append(Paragraph("Payment Details", heading_style))
    payment_details = [
        ['Fee Item:', payment_receipt.student_fee.fee.name],
        ['Amount Paid:', f"{school.ministry.currency_symbol if school.ministry else '₦'} {payment_receipt.amount:,.2f}"],
        ['Payment Method:', payment_receipt.get_payment_method_display()],
        ['Paid By:', payment_receipt.paid_by.get_full_name() if payment_receipt.paid_by else 'N/A'],
    ]
    
    if payment_receipt.description:
        payment_details.append(['Description:', payment_receipt.description])
    
    payment_table = Table(payment_details, colWidths=[2 * inch, 2.5 * inch])
    payment_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # 6. Amount summary
    summary_data = [
        ['', 'Amount'],
        ['Amount Paid:', f"{school.ministry.currency_symbol if school.ministry else '₦'} {payment_receipt.amount:,.2f}"],
        ['Balance:', f"{school.ministry.currency_symbol if school.ministry else '₦'} {max(0, payment_receipt.student_fee.fee.amount - payment_receipt.student_fee.amount_paid):,.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F0F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # 7. Footer
    footer_text = f"Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | This is an automated receipt"
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER
    )))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def save_receipt_pdf(payment_receipt):
    """
    Generate and save PDF receipt to PaymentReceipt model.
    
    Args:
        payment_receipt: PaymentReceipt instance
    
    Returns:
        Updated PaymentReceipt instance with pdf_file set
    """
    pdf_buffer = generate_payment_receipt_pdf(payment_receipt)
    
    # Create filename
    filename = f"receipt_{payment_receipt.receipt_number}.pdf"
    
    # Save to model
    payment_receipt.pdf_file.save(
        filename,
        ContentFile(pdf_buffer.read()),
        save=True
    )
    
    return payment_receipt
