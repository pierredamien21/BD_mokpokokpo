"""
Scheduler pour tâches automatiques (scanning alertes expiration, nettoyage, etc.)
Utilise APScheduler pour exécuter des jobs planifiés
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from services.alerte_expiration_service import AlerteExpirationService

# Charger variables d'environnement
load_dotenv()

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Créer la session database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def job_scanner_alertes_expiration():
    """
    🔍 Job: Scanner les alertes d'expiration tous les jours à 06:00
    """
    db = SessionLocal()
    try:
        logger.info("🚀 Démarrage du scan des alertes d'expiration...")
        stats = AlerteExpirationService.scanner_lots_expiration(db)
        
        logger.info(f"✅ Scan complété:")
        logger.info(f"   - Alertes JAUNE (J-90): {stats['jaune']}")
        logger.info(f"   - Alertes ORANGE (J-60): {stats['orange']}")
        logger.info(f"   - Alertes ROUGE (J-30): {stats['rouge']}")
        logger.info(f"   - Alertes EXPIRÉ: {stats['expire']}")
        logger.info(f"   - Mises à jour: {stats['updated']}")
        logger.info(f"   - Supprimées: {stats['deleted']}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du scan: {str(e)}")
    finally:
        db.close()


def job_nettoyer_alertes_obsoletes():
    """
    🧹 Job: Nettoyer les alertes obsolètes (expirant > J+90) tous les 7 jours
    """
    db = SessionLocal()
    try:
        logger.info("🧹 Nettoyage des alertes obsolètes...")
        count = AlerteExpirationService.nettoyer_alertes_obsolètes(db)
        logger.info(f"✅ {count} alertes obsolètes supprimées")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """
    Démarrer le scheduler avec tous les jobs planifiés
    """
    scheduler = BackgroundScheduler()
    
    # Job 1: Scanner les alertes tous les jours à 06:00 UTC
    scheduler.add_job(
        job_scanner_alertes_expiration,
        trigger=CronTrigger(hour=6, minute=0),
        id='scanner_alertes_expiration',
        name='Scanner alertes expiration',
        replace_existing=True
    )
    
    # Job 2: Nettoyer les alertes obsolètes chaque lundi à 02:00 UTC
    scheduler.add_job(
        job_nettoyer_alertes_obsoletes,
        trigger=CronTrigger(day_of_week=0, hour=2, minute=0),  # Lundi = 0
        id='nettoyer_alertes_obsoletes',
        name='Nettoyer alertes obsolètes',
        replace_existing=True
    )
    
    scheduler.start()
    
    logger.info("=" * 70)
    logger.info("📅 SCHEDULER DÉMARRÉ")
    logger.info("=" * 70)
    logger.info(f"✅ Jobs planifiés:")
    logger.info(f"   1️⃣ Scanner alertes: Quotidien à 06:00 UTC")
    logger.info(f"   2️⃣ Nettoyage: Chaque lundi à 02:00 UTC")
    logger.info("=" * 70)
    
    return scheduler


def stop_scheduler(scheduler):
    """
    Arrêter proprement le scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Scheduler arrêté")
