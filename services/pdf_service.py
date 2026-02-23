"""
Service de génération PDF pour bons de commande et bons de livraison
Utilise ReportLab pour créer des PDFs professionnels
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from database import SessionLocal
from models.model import Commande, Livraison, LigneCommande, Client, Utilisateur


class PDFService:
    """Service pour générer les documents PDF"""
    
    PAGE_SIZE = A4
    MARGIN = 0.5 * inch
    
    @staticmethod
    def _create_header(doc_title: str, farm_name: str = "FERME MOKPOKPO") -> list:
        """Crée l'en-tête du document"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Titre de la ferme
        farm_style = ParagraphStyle(
            'FarmName',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2C5F2D'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(farm_name, farm_style))
        
        # Type de document
        doc_style = ParagraphStyle(
            'DocType',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(doc_title, doc_style))
        elements.append(Spacer(1, 0.3*inch))
        
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
            
            client = db.query(Client).filter(Client.id_utilisateur == commande.id_client).first()
            utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == commande.id_client).first()
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
            elements.extend(PDFService._create_header("BON DE COMMANDE"))
            
            # Informations principales
            info_data = [
                ["Numéro de commande:", f"CMD-{commande_id:06d}"],
                ["Date de commande:", commande.date_commande.strftime("%d/%m/%Y")],
                ["Statut:", f"🟡 {commande.statut}"],
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
                ["Nom:", f"{utilisateur.prenom} {utilisateur.nom}"],
                ["Email:", utilisateur.email],
                ["Téléphone:", client.telephone or "N/A"],
                ["Adresse:", client.adresse or "N/A"],
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
                ligne_data.append([
                    ligne.id_produit and f"Produit {ligne.id_produit}" or "N/A",
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
            client = db.query(Client).filter(Client.id_utilisateur == commande.id_client).first()
            utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == commande.id_client).first()
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
            elements.extend(PDFService._create_header("BON DE LIVRAISON"))
            
            # Informations principales
            statut_emoji = {
                "EN_PREPARATION": "🟡",
                "PRETE": "🟠",
                "EN_LIVRAISON": "🔵",
                "LIVRÉE": "🟢"
            }.get(livraison.statut, "⚪")
            
            info_data = [
                ["N° Livraison:", livraison.numero_livraison],
                ["N° Commande:", f"CMD-{commande.id_commande:06d}"],
                ["Date création:", livraison.date_creation.strftime("%d/%m/%Y")],
                ["Statut:", f"{statut_emoji} {livraison.statut}"],
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
            elements.append(Paragraph(livraison.adresse_livraison, styles['Normal']))
            
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
            
            produit_data = [["Produit", "Quantité", "Montant unitaire"]]
            total_montant = 0
            for ligne in lignes:
                produit_data.append([
                    f"Produit {ligne.id_produit}" if ligne.id_produit else "N/A",
                    str(ligne.quantite),
                    f"{ligne.montant_ligne:.2f} €"
                ])
                total_montant += ligne.montant_ligne
            
            produit_data.append(["", "<b>MONTANT TOTAL:</b>", f"<b>{total_montant:.2f} €</b>"])
            
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
                ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
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
