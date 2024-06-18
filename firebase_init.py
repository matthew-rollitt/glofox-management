import firebase_admin
from firebase_admin import credentials, firestore
import json

def initialize_firebase(app):
    cred = credentials.Certificate('path_to_your_firebase_admin_sdk_json_file')
    firebase_admin.initialize_app(cred)
    app.db = firestore.client()
