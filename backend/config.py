import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


@dataclass
class AppConfig:
    jwt_secret: str
    gemini_api_key: Optional[str]
    port: int
    model_name: str
    firebase_project_id: Optional[str]
    firebase_credentials_file: Optional[str]

    @staticmethod
    def from_env() -> "AppConfig":
        return AppConfig(
            jwt_secret=os.getenv("JWT_SECRET", "change-me"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            port=int(os.getenv("PORT", "8080")),
            model_name=os.getenv("MODEL_NAME", "gemini-1.5-flash"),
            firebase_project_id=os.getenv("FIREBASE_PROJECT_ID"),
            firebase_credentials_file=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        )