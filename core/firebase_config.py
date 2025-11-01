import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# Build paths inside the project
# BASE_DIR will be 'D:\SARM'
BASE_DIR = Path(__file__).resolve().parent.parent

# --- THIS IS THE FIX ---
# We change KEY_PATH to look for "serviceAccountKey.json"
# in your main project folder (D:\SARM), not in your Downloads.
KEY_PATH = BASE_DIR / "serviceAccountKey.json"

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if app is already initialized
        firebase_admin.get_app()
    except ValueError:
        # App not initialized, so initialize it
        try:
            cred = credentials.Certificate(KEY_PATH)
            firebase_admin.initialize_app(cred)
        except FileNotFoundError:
            print(f"CRITICAL ERROR: 'serviceAccountKey.json' not found.")
            print(f"Please place your key file at: {KEY_PATH}")
            # Raise the error again so Django stops
            raise
        except Exception as e:
            print(f"An error occurred during Firebase initialization: {e}")
            raise
    
    return firestore.client()

# Initialize Firebase
db = initialize_firebase()

