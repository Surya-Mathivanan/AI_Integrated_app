from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt

from .config import AppConfig
from .db import Database
from .services.gemini_client import GeminiClient
from .routes.auth import auth_bp
from .routes.pathway import pathway_bp
from .routes.chat import chat_bp
from .routes.motivation import motivation_bp
from .utils.firebase_auth import FirebaseVerifier


jwt = JWTManager()


def create_app(config: AppConfig | None = None) -> Flask:
    app = Flask(__name__)

    cfg = config or AppConfig.from_env()
    app.config["JWT_SECRET_KEY"] = cfg.jwt_secret

    # CORS for all routes (adjust origins as needed)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    jwt.init_app(app)

    # Initialize services
    db = Database(cfg)
    gemini = GeminiClient(cfg)
    firebase = FirebaseVerifier(cfg)

    @app.before_request
    def inject_services() -> None:  # type: ignore[override]
        # Attach per-request references
        setattr(request, "app_ctx_db", db)
        setattr(request, "app_ctx_gemini", gemini)
        setattr(request, "app_ctx_firebase", firebase)

        # If an Authorization header contains a Firebase ID token, accept it and mint a short-lived JWT for internal usage
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and not request.path.startswith("/api/auth/"):
            token = auth_header.split(" ", 1)[1]
            # Attempt to detect Firebase token by structure (contains '.') and 'kid' header, but here we optimistically verify
            try:
                if firebase.enabled:
                    payload = firebase.verify(token)
                    # Put derived identity into flask-jwt-extended context via custom claims
                    request.firebase_user = {
                        "uid": payload.get("user_id"),
                        "email": payload.get("email"),
                        "name": payload.get("name"),
                    }
            except Exception:
                # Ignore; normal JWT may still validate in route decorators
                pass

    @app.get("/health")
    def health():
        return jsonify({
            "ok": True,
            "geminiEnabled": gemini.enabled,
            "firebaseEnabled": firebase.enabled,
        }), 200

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(pathway_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(motivation_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", "8080"))
    application.run(host="0.0.0.0", port=port)