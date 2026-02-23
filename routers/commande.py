from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from database import get_db
from models.model import Commande, Client, LigneCommande, Lot, Stock
from schema.commande import CommandeCreate, CommandeRead
from schema.enums import RoleEnum, StatutCommandeEnum
from security.dependencies import get_current_user
from services.fefo_service import FEFOService
from services.pdf_service import PDFService

router = APIRouter(
    prefix="/commandes",
    tags=["Commandes"]
)

@router.post("/", response_model=CommandeRead)
def create_commande(
    data: CommandeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Créer une commande (statut: EN_ATTENTE par défaut)
    
    **Permissions**: CLIENT, ADMIN
    
    Note: Le client de la commande doit correspondre à l'utilisateur connecté
    (ou ADMIN peut créer pour n'importe quel client)
    """
    if current_user.role not in [RoleEnum.CLIENT, RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    if current_user.role != RoleEnum.ADMIN:
        client = db.get(Client, data.id_client)
        if not client or client.id_utilisateur != current_user.id_utilisateur:
            raise HTTPException(
                status_code=403,
                detail="Vous ne pouvez pas passer une commande pour un autre client"
            )

    client = db.get(Client, data.id_client)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")

    commande = Commande(**data.model_dump())
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return commande

@router.get("/", response_model=list[CommandeRead])
def get_commandes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lister toutes les commandes
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    """
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    return db.query(Commande).all()


@router.get("/{id_commande}", response_model=CommandeRead)
def get_commande(id_commande: int, db: Session = Depends(get_db)):
    """Consulter une commande spécifique"""
    commande = db.get(Commande, id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return commande


# =====================================================
# 🎯 VALIDATION & FEFO - Accepter une commande
# =====================================================
@router.post("/{id_commande}/valider")
def valider_commande_fefo(
    id_commande: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    ✅ Valider une commande EN_ATTENTE → ACCEPTEE
    
    **Permissions**: GEST_COMMERCIAL, ADMIN
    
    **Processus**:
    1. Vérifier que commande est EN_ATTENTE
    2. Pour chaque ligne de commande:
       - Appliquer logique FEFO (First Expired First Out)
       - Déduit des lots ayant la date expiration la plus proche
       - Bloquer si quantité insuffisante
       - Bloquer si stock EXPIRÉ
    3. Enregistrer id_lot dans chaque LigneCommande
    4. Passer commande à ACCEPTEE
    5. Créer VENTE associée
    
    **Retourne**: Commande validée + détails FEFO utilisés
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    commande = db.get(Commande, id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Vérifier statut = EN_ATTENTE
    if commande.statut != StatutCommandeEnum.EN_ATTENTE:
        raise HTTPException(
            status_code=400,
            detail=f"Commande est en statut '{commande.statut}'. Impossible de valider."
        )
    
    # Vérifier qu'il y a des lignes de commande
    if not commande.lignes:
        raise HTTPException(
            status_code=400,
            detail="Commande sans lignes. Impossible de valider."
        )
    
    # Traiter chaque ligne de commande avec FEFO
    fefo_details = []
    
    try:
        for ligne in commande.lignes:
            produit_id = ligne.id_produit
            quantite = ligne.quantite
            
            # Allocation FEFO
            allocations, success, error = FEFOService.allocate_fefo(
                db, produit_id, quantite
            )
            
            if not success:
                # Si une ligne échoue, abort tout
                db.rollback()
                raise HTTPException(status_code=400, detail=error)
            
            # Enregistrer l'allocation
            fefo_details.append({
                "id_ligne": ligne.id_ligne_commande,
                "id_produit": produit_id,
                "quantite_demandee": quantite,
                "lots_utilises": allocations
            })
            
            # Assigner le premier lot à la ligne si une seule allocation
            # Sinon la première (pour lot tracking)
            if allocations:
                ligne.id_lot = allocations[0]["id_lot"]
        
        # Si tout est OK, appliquer les déductions
        all_allocations = []
        for detail in fefo_details:
            all_allocations.extend(detail["lots_utilises"])
        
        if not FEFOService.deduct_lots(db, all_allocations):
            db.rollback()
            raise HTTPException(status_code=400, detail="Erreur déduction stocks")
        
        # Mettre à jour statut commande
        commande.statut = StatutCommandeEnum.ACCEPTEE
        
        db.commit()
        db.refresh(commande)
        
        return {
            "message": "✅ Commande validée avec succès (FEFO appliqué)",
            "id_commande": commande.id_commande,
            "nouveau_statut": commande.statut,
            "fefo_details": fefo_details,
            "total_lots_utilises": len(all_allocations)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur validation: {str(e)}")

@router.delete("/{id_commande}", status_code=204)
def delete_commande(
    id_commande: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    🗑️ Supprimer une commande
    
    **Permissions**: ADMIN, GEST_COMMERCIAL
    
    **Garde-fou**:
    - Impossible si statut = ACCEPTEE
    - Impossible si vente associée existe
    """
    
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    commande = db.get(Commande, id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Garde-fou: Bloquer si commande acceptée
    if commande.statut == StatutCommandeEnum.ACCEPTEE:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer une commande acceptée"
        )
    
    # Garde-fou: Bloquer si vente associée existe
    if commande.vente:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer une commande avec vente associée"
        )
    
    try:
        db.delete(commande)
        db.commit()
        return {"message": "Commande supprimée avec succès"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer la commande (contraintes de base de données)"
        )


@router.get("/{id_commande}/bon-pdf")
def download_bon_commande(
    id_commande: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Télécharger le bon de commande en PDF
    
    **Permissions**: CLIENT (sa propre commande), ADMIN, GEST_COMMERCIAL
    
    Génère un PDF professionnel avec:
    - Informations de commande
    - Détails client
    - Liste des articles
    - Montant total
    """
    if current_user.role not in [RoleEnum.CLIENT, RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    commande = db.get(Commande, id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    
    # Vérification: CLIENT ne peut accéder qu'à ses propres commandes
    if current_user.role == RoleEnum.CLIENT:
        if commande.id_client != current_user.id_utilisateur:
            raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette commande")
    
    try:
        pdf_buffer = PDFService.generate_bon_commande(id_commande)
        return FileResponse(
            pdf_buffer,
            media_type="application/pdf",
            filename=f"bon-commande-{id_commande:06d}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {str(e)}")
