from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.resetToken.model import ResetToken
from app.db.database import SessionLocal
from app.db.user import model as user_model

def delete_expired_tokens():
    db: Session = SessionLocal()
    try:
        # Query for expired tokens
        expired_tokens = db.query(ResetToken).filter(ResetToken.expires < datetime.now()).all()
        for token in expired_tokens:
            db.delete(token)
        db.commit()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_expired_tokens, 'interval', hours=1)  # Adjust the interval as needed
    scheduler.start()

async def store_reset_token(db: Session, user_id: int, token: str):
    expire_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    db_token = ResetToken(user_id=user_id, token=token, expires=expire_at)
    db.add(db_token)
    db.commit()

def verify_reset_token(db: Session, token: str):
    db_token = db.query(ResetToken).filter(ResetToken.token == token, ResetToken.expires > datetime.now()).first()
    if db_token:
        return db.query(user_model.User).filter(user_model.User.id == db_token.user_id).first()
    return None


# Call start_scheduler() when your application starts