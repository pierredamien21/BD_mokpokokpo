"""
Service de génération PDF pour bons de commande et bons de livraison
Utilise ReportLab pour créer des PDFs professionnels
"""

import base64
import os
import urllib.request
from functools import lru_cache
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from svglib.svglib import svg2rlg

from database import SessionLocal
from models.model import Commande, Livraison, LigneCommande


class PDFService:
    """Service pour générer les documents PDF"""
    
    PAGE_SIZE = A4
    MARGIN = 0.5 * inch
    LOGO_URL_ENV = "PDF_LOGO_URL"
    LOGO_PATH_ENV = "PDF_LOGO_PATH"
    LOGO_BASE64_ENV = "PDF_LOGO_BASE64"
    LOGO_SVG_BASE64_ENV = "PDF_LOGO_SVG_BASE64"
    LOGO_MAX_WIDTH = 1.2 * inch
    LOGO_MAX_HEIGHT = 1.0 * inch
    QR_SIZE = 1.1 * inch

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_logo_flowable():
        svg_b64 = os.getenv(PDFService.LOGO_SVG_BASE64_ENV)
        if svg_b64:
            try:
                svg_bytes = base64.b64decode(svg_b64)
                drawing = svg2rlg(BytesIO(svg_bytes))
                if drawing and drawing.width and drawing.height:
                    scale = min(
                        PDFService.LOGO_MAX_WIDTH / drawing.width,
                        PDFService.LOGO_MAX_HEIGHT / drawing.height
                    )
                    drawing.scale(scale, scale)
                    drawing.width *= scale
                    drawing.height *= scale
                    return drawing
            except Exception:
                pass

        png_b64 = os.getenv(PDFService.LOGO_BASE64_ENV)
        if png_b64:
            try:
                png_bytes = base64.b64decode(png_b64)
                logo_image = Image(BytesIO(png_bytes))
                logo_image._restrictSize(PDFService.LOGO_MAX_WIDTH, PDFService.LOGO_MAX_HEIGHT)
                return logo_image
            except Exception:
                pass

        logo_path = os.getenv(PDFService.LOGO_PATH_ENV)
        if logo_path and os.path.exists(logo_path):
            try:
                logo_image = Image(logo_path)
                logo_image._restrictSize(PDFService.LOGO_MAX_WIDTH, PDFService.LOGO_MAX_HEIGHT)
                return logo_image
            except Exception:
                pass

        logo_url = os.getenv(PDFService.LOGO_URL_ENV)
        if logo_url:
            try:
                with urllib.request.urlopen(logo_url, timeout=5) as response:
                    logo_bytes = response.read()
                logo_image = Image(BytesIO(logo_bytes))
                logo_image._restrictSize(PDFService.LOGO_MAX_WIDTH, PDFService.LOGO_MAX_HEIGHT)
                return logo_image
            except Exception:
                pass

        return None

    @staticmethod
    def _make_qr_flowable(data: str) -> Drawing:
        widget = qr.QrCodeWidget(data)
        bounds = widget.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        scale_x = PDFService.QR_SIZE / width
        scale_y = PDFService.QR_SIZE / height
        drawing = Drawing(PDFService.QR_SIZE, PDFService.QR_SIZE, transform=[scale_x, 0, 0, scale_y, 0, 0])
        drawing.add(widget)
        return drawing
    
    @staticmethod
    def _create_header(
        doc_title: str,
        doc_ref: str | None = None,
        qr_data: str | None = None,
        farm_name: str = "FERME MOKPOKPO"
    ) -> list:
        """Crée l'en-tête du document avec logo et QR code si disponibles"""
        styles = getSampleStyleSheet()
        elements = []

        farm_style = ParagraphStyle(
            'FarmName',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2C5F2D'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        doc_style = ParagraphStyle(
            'DocType',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        ref_style = ParagraphStyle(
            'DocRef',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#444444'),
            alignment=TA_CENTER
        )

        center_block = [
            Paragraph(farm_name, farm_style),
            Paragraph(doc_title, doc_style)
        ]
        if doc_ref:
            center_block.append(Paragraph(doc_ref, ref_style))

        logo_cell = ""
        logo_flowable = PDFService._load_logo_flowable()
        if logo_flowable:
            logo_cell = logo_flowable

        qr_cell = ""
        if qr_data:
            qr_cell = PDFService._make_qr_flowable(qr_data)

        header_table = Table(
            [[logo_cell, center_block, qr_cell]],
            colWidths=[PDFService.LOGO_MAX_WIDTH, 4.2 * inch, PDFService.QR_SIZE]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.25 * inch))
        return elements
    
    @staticmethod
    def _create_footer(doc_date: datetime) -> list:
        """Crée le pied de page"""
        styles = getSampleStyleSheet()
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        return [
            Spacer(1, 0.3*inch),
            Paragraph(
                f"Généré le {doc_date.strftime('%d/%m/%Y à %H:%M:%S')} | "
                f"Ferme Mokpokpo | Tous droits réservés",
                footer_style
            )
        ]
    
    @staticmethod
    def generate_bon_commande(commande_id: int) -> BytesIO:
        """
        Génère un bon de commande en PDF
        
        Args:
            commande_id: ID de la commande
            
        Returns:
            BytesIO: Document PDF en mémoire
        """
        db = SessionLocal()
        try:
            # Récupérer les données
            commande = db.query(Commande).filter(Commande.id_commande == commande_id).first()
            if not commande:
                raise ValueError(f"Commande {commande_id} non trouvée")
            
            client = commande.client
            utilisateur = client.utilisateur if client else None
            lignes = db.query(LigneCommande).filter(LigneCommande.id_commande == commande_id).all()
            
            # Créer le PDF en mémoire
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=PDFService.PAGE_SIZE,
                rightMargin=PDFService.MARGIN,
                leftMargin=PDFService.MARGIN,
                topMargin=PDFService.MARGIN,
                bottomMargin=PDFService.MARGIN
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # En-tête
            qr_data = "\n".join([
                "TYPE: BON_COMMANDE",
                f"COMMANDE: CMD-{commande_id:06d}",
                f"DATE: {commande.date_commande.strftime('%d/%m/%Y')}",
                f"CLIENT: {utilisateur.prenom} {utilisateur.nom}" if utilisateur else "CLIENT: N/A",
                f"EMAIL: {utilisateur.email}" if utilisateur else "EMAIL: N/A",
                f"TOTAL: {commande.montant_total:.2f}"
            ])
            elements.extend(PDFService._create_header(
                "BON DE COMMANDE",
                doc_ref=f"CMD-{commande_id:06d}",
                qr_data=qr_data
            ))
            
            # Informations principales
            info_data = [
                ["Numéro de commande:", f"CMD-{commande_id:06d}"],
                ["Date de commande:", commande.date_commande.strftime("%d/%m/%Y")],
                ["Statut:", f"{commande.statut}"],
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Infos client
            elements.append(Paragraph("<b>Informations client:</b>", styles['Heading3']))
            client_data = [
                ["Nom:", f"{utilisateur.prenom} {utilisateur.nom}" if utilisateur else "N/A"],
                ["Email:", utilisateur.email if utilisateur else "N/A"],
                ["Téléphone:", client.telephone if client and client.telephone else "N/A"],
                ["Adresse:", client.adresse if client and client.adresse else "N/A"],
            ]
            
            client_table = Table(client_data, colWidths=[1.5*inch, 4*inch])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))
            elements.append(client_table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Détail des lignes
            elements.append(Paragraph("<b>Articles commandés:</b>", styles['Heading3']))
            
            ligne_data = [["Produit", "Quantité", "Prix unitaire", "Montant"]]
            for ligne in lignes:
                produit_nom = ligne.produit.nom_produit if ligne.produit else f"Produit {ligne.id_produit}"
                ligne_data.append([
                    produit_nom or "N/A",
                    str(ligne.quantite),
                    f"{ligne.prix_unitaire:.2f} €",
                    f"{ligne.montant_ligne:.2f} €"
                ])
            
            # Ajouter la ligne totale
            ligne_data.append([
                "",
                "",
                "<b>TOTAL:</b>",
                f"<b>{commande.montant_total:.2f} €</b>"
            ])
            
            ligne_table = Table(ligne_data)
            ligne_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5F2D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0F0F0')),
                ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(ligne_table)
            
            # Pied de page
            elements.extend(PDFService._create_footer(datetime.now()))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        finally:
            db.close()
    
    @staticmethod
    def generate_bon_livraison(livraison_id: int) -> BytesIO:
        """
        Génère un bon de livraison en PDF
        
        Args:
            livraison_id: ID de la livraison
            
        Returns:
            BytesIO: Document PDF en mémoire
        """
        db = SessionLocal()
        try:
            # Récupérer les données
            livraison = db.query(Livraison).filter(Livraison.id_livraison == livraison_id).first()
            if not livraison:
                raise ValueError(f"Livraison {livraison_id} non trouvée")
            
            commande = livraison.commande
            client = commande.client
            utilisateur = client.utilisateur if client else None
            lignes = db.query(LigneCommande).filter(LigneCommande.id_commande == commande.id_commande).all()
            
            # Créer le PDF en mémoire
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=PDFService.PAGE_SIZE,
                rightMargin=PDFService.MARGIN,
                leftMargin=PDFService.MARGIN,
                topMargin=PDFService.MARGIN,
                bottomMargin=PDFService.MARGIN
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # En-tête
            qr_data = "\n".join([
                "TYPE: BON_LIVRAISON",
                f"LIVRAISON: {livraison.numero_livraison}",
                f"COMMANDE: CMD-{commande.id_commande:06d}",
                f"STATUT: {livraison.statut}",
                f"CLIENT: {utilisateur.prenom} {utilisateur.nom}" if utilisateur else "CLIENT: N/A",
                f"SUIVI: {livraison.numero_suivi or 'N/A'}"
            ])
            elements.extend(PDFService._create_header(
                "BON DE LIVRAISON",
                doc_ref=livraison.numero_livraison,
                qr_data=qr_data
            ))
            
            # Informations principales
            info_data = [
                ["N° Livraison:", livraison.numero_livraison],
                ["N° Commande:", f"CMD-{commande.id_commande:06d}"],
                ["Date création:", livraison.date_creation.strftime("%d/%m/%Y")],
                ["Statut:", f"{livraison.statut}"],
            ]
            
            if livraison.date_livraison:
                info_data.append(["Date livraison:", livraison.date_livraison.strftime("%d/%m/%Y")])
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Infos de livraison
            elements.append(Paragraph("<b>Adresse de livraison:</b>", styles['Heading3']))
            elements.append(Paragraph(livraison.adresse_livraison or "N/A", styles['Normal']))
            
            if livraison.transporteur:
                elements.append(Spacer(1, 0.15*inch))
                elements.append(Paragraph("<b>Transporteur:</b>", styles['Heading3']))
                transport_data = [
                    ["Prestataire:", livraison.transporteur],
                ]
                if livraison.numero_suivi:
                    transport_data.append(["Numéro suivi:", livraison.numero_suivi])
                
                transport_table = Table(transport_data, colWidths=[1.5*inch, 3.5*inch])
                transport_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                ]))
                elements.append(transport_table)
            
            elements.append(Spacer(1, 0.2*inch))
            
            # Détail des produits
            elements.append(Paragraph("<b>Produits livrés:</b>", styles['Heading3']))
            
            produit_data = [["Produit", "Quantité", "Prix unitaire", "Montant"]]
            total_montant = 0
            for ligne in lignes:
                produit_nom = ligne.produit.nom_produit if ligne.produit else f"Produit {ligne.id_produit}"
                produit_data.append([
                    produit_nom or "N/A",
                    str(ligne.quantite),
                    f"{ligne.prix_unitaire:.2f} €",
                    f"{ligne.montant_ligne:.2f} €"
                ])
                total_montant += ligne.montant_ligne
            
            produit_data.append(["", "", "<b>MONTANT TOTAL:</b>", f"<b>{total_montant:.2f} €</b>"])
            
            produit_table = Table(produit_data)
            produit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5F2D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0F0F0')),
                ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(produit_table)
            
            if livraison.notes:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("<b>Remarques:</b>", styles['Heading3']))
                elements.append(Paragraph(livraison.notes, styles['Normal']))
            
            # Pied de page
            elements.extend(PDFService._create_footer(datetime.now()))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        finally:
            db.close()
