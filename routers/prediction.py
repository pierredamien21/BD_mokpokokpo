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

@router.get("/sales", dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))])
async def get_sales_prediction(db: Session = Depends(get_db)):
    service = PredictionService(db)
    prediction = await service.predict_sales()
    if "error" in prediction:
        raise HTTPException(status_code=500, detail=prediction["error"])
    return prediction

@router.get("/historical-data", dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))])
def get_historical_data(db: Session = Depends(get_db)):
    service = PredictionService(db)
    return service.get_historical_sales_data()
