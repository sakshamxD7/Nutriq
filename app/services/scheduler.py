from datetime import datetime, date, time
from flask_mail import Message
from app.extensions import db, mail
from app.models.user import User
from app.models.food import FoodLog
import logging

logger = logging.getLogger(__name__)

def send_daily_reminders_job(app):
    """
    Background job that runs every minute to send email reminders to users
    who have set their reminder time to the current hour/minute.
    """
    with app.app_context():
        try:
            # Get current system time formatted as HH:MM
            current_time_str = datetime.now().strftime("%H:%M")
            
            # Query users who have reminders enabled and match the current time
            users_to_remind = User.query.filter_by(
                email_reminders=True,
                reminder_time=current_time_str
            ).all()
            
            if not users_to_remind:
                return

            today = date.today()
            start_of_today = datetime.combine(today, time.min)
            
            for user in users_to_remind:
                # Calculate total calories logged today
                today_logs = FoodLog.query.filter(
                    FoodLog.user_id == user.id,
                    FoodLog.logged_at >= start_of_today
                ).all()
                
                calories_today = sum(log.calories for log in today_logs)
                
                try:
                    # Prepare and send the email
                    msg = Message(
                        subject="Nutriq — Daily Nutrition Log Reminder",
                        recipients=[user.email],
                        body=f"Hey {user.name},\n\nDon't forget to log your meals today! You've logged {int(calories_today)} calories so far.\n\nKeep tracking and stay healthy!\n\nBest,\nTeam Nutriq"
                    )
                    mail.send(msg)
                    logger.info(f"Successfully sent daily reminder email to {user.email}")
                except Exception as e:
                    # Log error and continue so we don't break other emails
                    logger.error(f"Failed to send email to {user.email}: {str(e)}")
        except Exception as outer_e:
            logger.error(f"Error executing daily reminders job: {str(outer_e)}")
