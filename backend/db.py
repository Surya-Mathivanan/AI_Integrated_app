from __future__ import annotations

from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from .config import AppConfig


class Database:
    def __init__(self, config: AppConfig) -> None:
        if not firebase_admin._apps:
            if config.firebase_credentials_file:
                cred = credentials.Certificate(config.firebase_credentials_file)
                firebase_admin.initialize_app(cred, {
                    'projectId': config.firebase_project_id,
                })
            else:
                # Uses GOOGLE_APPLICATION_CREDENTIALS or default cred if running on GCP
                firebase_admin.initialize_app()
        self._db = firestore.client()

    # Collections
    @property
    def users(self):
        return self._db.collection('users')

    @property
    def pathways(self):
        return self._db.collection('pathways')

    @property
    def chats(self):
        return self._db.collection('chats')

    @property
    def motivation(self):
        return self._db.collection('motivation')