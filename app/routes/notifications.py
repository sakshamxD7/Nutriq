from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
import re

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        reminder_time = request.form.get('reminder_time', '08:00')
        email_reminders = request.form.get('email_reminders') == 'on'
        
        # Validate HH:MM time format
        if not re.match(r'^\d{2}:\d{2}$', reminder_time):
            flash("Invalid time format. Please use HH:MM.", "danger")
            return redirect(url_for('notifications.settings'))
            
        try:
            hour, minute = map(int, reminder_time.split(':'))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError()
        except ValueError:
            flash("Invalid hour or minute values.", "danger")
            return redirect(url_for('notifications.settings'))

        try:
            current_user.reminder_time = reminder_time
            current_user.email_reminders = email_reminders
            db.session.commit()
            flash("Notification preferences updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update preferences: {str(e)}", "danger")

        return redirect(url_for('notifications.settings'))

    return render_template('notifications/settings.html')
