import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.collector import CollectorService
from app.services.analyzer import AnalyzerService
from app.alerters.alerter import AlerterService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_collect():
    logger.info("Starting scheduled collection...")
    db = SessionLocal()
    try:
        service = CollectorService(db)
        count = service.collect_all()
        logger.info(f"Collected {count} new intelligences")
    except Exception as e:
        logger.error(f"Collection error: {e}")
    finally:
        db.close()


def run_analyze():
    logger.info("Starting scheduled analysis...")
    db = SessionLocal()
    try:
        service = AnalyzerService(db)
        count = service.analyze_unanalyzed(limit=settings.ANALYSIS_BATCH_SIZE)
        logger.info(f"Analyzed {count} intelligences")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
    finally:
        db.close()


def run_alerts():
    logger.info("Starting alert check...")
    db = SessionLocal()
    try:
        service = AlerterService(db)
        service.check_recent_unchecked()
    except Exception as e:
        logger.error(f"Alert check error: {e}")
    finally:
        db.close()


def start_scheduler():
    interval = settings.COLLECT_INTERVAL_MINUTES
    scheduler.add_job(run_collect, "interval", minutes=interval, id="collect")
    scheduler.add_job(run_analyze, "interval", minutes=interval, id="analyze", jitter=60)
    scheduler.add_job(run_alerts, "interval", minutes=interval, id="alerts", jitter=120)
    scheduler.start()
    logger.info(f"Scheduler started with {interval}min interval")
