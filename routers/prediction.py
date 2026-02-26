from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.prediction_service import PredictionService
from security.access_control import RoleChecker
from schema.enums import RoleEnum

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)

@router.get(
    "/sales",
    dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))]
)
async def get_sales_prediction(db: Session = Depends(get_db)):
    """
    Prédictions de ventes combinant:
    1. Modèle ML (RandomForest) pour les quantités
    2. Gemini pour les recommandations intelligentes
    """
    service = PredictionService(db)
    prediction = await service.predict_sales()
    if "error" in prediction:
        raise HTTPException(status_code=500, detail=prediction["error"])
    return prediction

@router.get(
    "/sales/ml-only",
    dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))]
)
def get_ml_predictions_only(db: Session = Depends(get_db)):
    """
    Prédictions ML pures (RandomForest uniquement)
    Retourne les prédictions de ventes par produit pour les 7 jours
    """
    service = PredictionService(db)
    predictions = service.predict_sales_by_product()
    
    if "error" in predictions:
        raise HTTPException(status_code=500, detail=predictions["error"])
    
    return {
        "predictions": predictions,
        "total_predicted_sales_7_days": round(sum(p['predicted_sales_7_days'] for p in predictions), 2),
        "model_type": "RandomForestRegressor",
        "features_used": 15
    }

@router.get(
    "/historical-data",
    dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))]
)
def get_historical_data(days: int = 90, db: Session = Depends(get_db)):
    """
    Données historiques de ventes pour analyse
    """
    service = PredictionService(db)
    return service.get_historical_sales_data(days=days)
