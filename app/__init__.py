import os
from flask import Flask, render_template
from config import get_config
from app.extensions import db, login_manager, migrate, mail, csrf, scheduler

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.food import food_bp
    from app.routes.diary import diary_bp
    from app.routes.ai import ai_bp
    from app.routes.goals import goals_bp
    from app.routes.trivia import trivia_bp
    from app.routes.billing import billing_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(food_bp, url_prefix='/food')
    app.register_blueprint(diary_bp, url_prefix='/diary')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(goals_bp, url_prefix='/goals')
    app.register_blueprint(trivia_bp, url_prefix='/trivia')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

    # Setup database creation
    with app.app_context():
        db.create_all()

    # Configure background jobs
    from app.services.scheduler import send_daily_reminders_job
    
    # Check if we are running in the main process (to avoid duplicate schedulers with reloader)
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        if not scheduler.running:
            scheduler.start()
            # Add reminder job to run every minute
            # Use 'app' context inside job by passing the app instance
            scheduler.add_job(
                func=send_daily_reminders_job,
                trigger="interval",
                minutes=1,
                id="daily_reminders_job",
                replace_existing=True,
                args=[app]
            )

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Page Not Found", error_desc="We couldn't find the page you are looking for."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="500 - Internal Server Error", error_desc="An unexpected error occurred. Please try again later."), 500

    return app
