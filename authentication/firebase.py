import os

import firebase_admin
from firebase_admin import auth, credentials


def _initialize_firebase():
    if firebase_admin._apps:
        return

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip()
    if not cred_path:
        raise ValueError("FIREBASE_CREDENTIALS_PATH is not set.")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def verify_firebase_token(id_token: str) -> dict:
    _initialize_firebase()
    return auth.verify_id_token(id_token)
