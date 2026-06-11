"""
API entrypoint for backend API using MongoDB.
"""
from dotenv import load_dotenv
import os
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_mail import Mail
from services.scheduler_main import NotificationScheduler
from models.subscription import db as sub_db  # If models are needed elsewhere
from services.db.agent_facts import load_agent_facts_to_db
from config.config import Config
from routes import register_blueprints
from utils.update_agent_facts import update_agent_facts_in_db

# Load environment variables
load_dotenv()

# Initialize PyMongo
mongo = PyMongo()

def setup_sub_db(app):
    """
    Initialize and set up the MongoDB database.
    """
    # MongoDB connection URI
    app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
    mongo.init_app(app)

    with app.app_context():
        # Example: Creating a collection and inserting initial data if not present
        db = mongo.db
        if "subscriptions" not in db.list_collection_names():
            db.subscriptions.insert_one({"example_field": "Initial Data"})
        print("MongoDB setup complete. Available collections:", db.list_collection_names())


def run_app():
    """
    Main application setup.
    """
    # Update agent facts in the database
    update_agent_facts_in_db()

    # Set up Flask app
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000"])
    app.config.from_object(Config)

    # Debugging statements
    print("SECRET_KEY:", app.config['SECRET_KEY'])
    print("SECURITY_PASSWORD_SALT:", app.config['SECURITY_PASSWORD_SALT'])
    print("Loaded SECURITY_PASSWORD_SALT:", os.getenv("SECURITY_PASSWORD_SALT"))

    # Initialize extensions
    mail = Mail(app)
    jwt = JWTManager(app)

    # Configure CORS
    cors_config = {
        r"*": {
            "origins": [os.getenv("BASE_URL")],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-CSRF-Token"
            ]
        }
    }
    CORS(app, resources=cors_config)

    # Register routes
    register_blueprints(app)

    # Base endpoint
    @app.get("/")
    def root():
        """
        Health probe endpoint.
        """
        return {"status": "ready"}

    # Create and start the notification scheduler
    scheduler = NotificationScheduler(app)
    notification_thread = Thread(target=scheduler.run_scheduler)
    notification_thread.start()

    @app.route("/test-notification")
    def test_notification():
        """
        Test endpoint for sending a notification.
        """
        # Use actual values or test values for user_id and check_in_id
        user_id = "66d7b0c05a0e718dd3ea783d"
        check_in_id = "66d901c021a63476598fe1c1"
        message = "This is a test notification."
        scheduler.send_notification(user_id, check_in_id, message)
        return jsonify({"message": "Test notification sent"})

    return app, jwt, mail


if __name__ == "__main__":
    # Run the app
    app, jwt, mail = run_app()
    
    # Set up the MongoDB database
    setup_sub_db(app)

    # Pre-load agent facts into the database
    load_agent_facts_to_db()

    # Start the Flask app
    HOST = os.getenv("FLASK_RUN_HOST") or "0.0.0.0"
    PORT = os.getenv("FLASK_RUN_PORT") or 8000
    app.run(debug=True, host=HOST, port=PORT)
