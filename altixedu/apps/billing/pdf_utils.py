"""
PDF generation utilities for invoices and receipts.
Uses ReportLab to create professional PDF documents.
"""

import logging
from io import BytesIO
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_invoice_pdf(invoice):
    """
    Generate a professional invoice PDF.
    
    Args:
        invoice: Invoice instance
        
    Returns:
        BytesIO object containing the PDF
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555')
        )
        
        # Title
        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Invoice metadata
        subscription = invoice.subscription
        school = subscription.school
        
        metadata = [
            [Paragraph("<b>Invoice Number:</b>", normal_style), Paragraph(invoice.invoice_number, normal_style)],
            [Paragraph("<b>Invoice Date:</b>", normal_style), Paragraph(invoice.issued_at.strftime("%B %d, %Y"), normal_style)],
            [Paragraph("<b>Due Date:</b>", normal_style), Paragraph(invoice.due_at.strftime("%B %d, %Y"), normal_style)],
            [Paragraph("<b>Status:</b>", normal_style), Paragraph(invoice.get_status_display(), normal_style)],
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 2*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white]),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Bill To section
        elements.append(Paragraph("BILL TO", heading_style))
        
        bill_to = [
            [Paragraph(f"<b>{school.name}</b>", normal_style)],
            [Paragraph(school.email, normal_style)],
            [Paragraph(school.phone, normal_style)],
            [Paragraph(f"{school.address}, {school.city}, {school.state or ''} {school.postal_code or ''}, {school.country}", normal_style)],
        ]
        
        bill_table = Table(bill_to, colWidths=[4*inch])
        bill_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(bill_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Line items table
        elements.append(Paragraph("INVOICE DETAILS", heading_style))
        
        line_items = [
            ['Description', 'Quantity', 'Unit Price', 'Amount'],
            ['Subscription - ' + subscription.tier.display_name, '1', f"₦{subscription.monthly_price:,.2f}", f"₦{invoice.amount:,.2f}"],
        ]
        
        line_table = Table(line_items, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        line_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('LEFTPADDING', (0, 1), (-1, -1), 5),
            ('RIGHTPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ]))
        
        elements.append(line_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Totals section
        totals = [
            ['', '', 'Subtotal:', f"₦{invoice.amount:,.2f}"],
            ['', '', 'Tax (0%):', '₦0.00'],
            ['', '', 'Discount (0%):', '₦0.00'],
            ['', '', 'TOTAL:', f"₦{invoice.amount:,.2f}"],
        ]
        
        totals_table = Table(totals, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#0066CC')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Terms and conditions
        elements.append(Paragraph("TERMS AND CONDITIONS", heading_style))
        elements.append(Paragraph(
            "Payment is due by the date specified above. Please reference the invoice number with your payment. "
            "Service may be suspended if payment is not received by the due date. "
            "For questions or payment arrangements, please contact support@altixedu.com",
            normal_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')} | AltixEdu Billing System"
        elements.append(Paragraph(
            f"<i>{footer_text}</i>",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#999999'),
                alignment=1
            )
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        logger.info(f"Invoice PDF generated for invoice {invoice.invoice_number}")
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to generate invoice PDF: {str(e)}")
        raise


def generate_receipt_pdf(payment_transaction, invoice=None):
    """
    Generate a payment receipt PDF.
    
    Args:
        payment_transaction: PaymentTransaction instance
        invoice: Invoice instance (optional)
        
    Returns:
        BytesIO object containing the PDF
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#27ae60'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555')
        )
        
        # Title
        elements.append(Paragraph("PAYMENT RECEIPT", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Status indicator
        status_color = "#27ae60" if payment_transaction.status == "completed" else "#e74c3c"
        elements.append(Paragraph(
            f"<b style='color: {status_color}; font-size: 14px;'>Status: {payment_transaction.get_status_display().upper()}</b>",
            heading_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Receipt metadata
        subscription = payment_transaction.subscription
        school = subscription.school
        
        metadata = [
            [Paragraph("<b>Receipt Number:</b>", normal_style), Paragraph(payment_transaction.transaction_id, normal_style)],
            [Paragraph("<b>Date:</b>", normal_style), Paragraph(payment_transaction.completed_at.strftime("%B %d, %Y %H:%M:%S") if payment_transaction.completed_at else "Pending", normal_style)],
            [Paragraph("<b>School:</b>", normal_style), Paragraph(school.name, normal_style)],
            [Paragraph("<b>Payment Method:</b>", normal_style), Paragraph(payment_transaction.get_payment_method_display(), normal_style)],
        ]
        
        metadata_table = Table(metadata, colWidths=[2.5*inch, 2.5*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Payment details
        elements.append(Paragraph("PAYMENT DETAILS", heading_style))
        
        payment_details = [
            [Paragraph("<b>Amount Paid:</b>", normal_style), Paragraph(f"₦{payment_transaction.amount:,.2f}", normal_style)],
            [Paragraph("<b>Currency:</b>", normal_style), Paragraph(payment_transaction.currency, normal_style)],
            [Paragraph("<b>Subscription Tier:</b>", normal_style), Paragraph(subscription.tier.display_name if subscription.tier else "N/A", normal_style)],
            [Paragraph("<b>Payment Frequency:</b>", normal_style), Paragraph(subscription.get_payment_frequency_display(), normal_style)],
        ]
        
        payment_table = Table(payment_details, colWidths=[2.5*inch, 2.5*inch])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(payment_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Invoice reference if exists
        if invoice:
            elements.append(Paragraph("RELATED INVOICE", heading_style))
            invoice_ref = [
                [Paragraph("<b>Invoice Number:</b>", normal_style), Paragraph(invoice.invoice_number, normal_style)],
                [Paragraph("<b>Invoice Date:</b>", normal_style), Paragraph(invoice.issued_at.strftime("%B %d, %Y"), normal_style)],
            ]
            invoice_table = Table(invoice_ref, colWidths=[2.5*inch, 2.5*inch])
            invoice_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white]),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(invoice_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Thank you message
        if payment_transaction.status == "completed":
            elements.append(Paragraph(
                "<b style='font-size: 12px; color: #27ae60;'>Thank you for your payment!</b><br/>"
                "Your subscription is now active and your school can access all features.",
                ParagraphStyle(
                    'ThankYou',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#27ae60'),
                    alignment=1
                )
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')} | AltixEdu Billing System"
        elements.append(Paragraph(
            f"<i>{footer_text}</i>",
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#999999'),
                alignment=1
            )
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        logger.info(f"Receipt PDF generated for transaction {payment_transaction.transaction_id}")
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to generate receipt PDF: {str(e)}")
        raise
