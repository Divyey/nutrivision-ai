from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://nutrivision-ai-green.vercel.app,"
        "https://nutrivision-ai-divyeys-projects.vercel.app,"
        "https://dev-nutrivision-ai.vercel.app,"
        "https://prod-nutrivision-ai.vercel.app"
    )

    # Optional FOOD_* overrides. Unset → these defaults (exported ONNX at imgsz 800).
    food_model_path: str = str(ROOT_DIR / "ml" / "models" / "food" / "best.onnx")
    food_max_image_bytes: int = 8 * 1024 * 1024
    food_max_pixels: int = 20_000_000
    food_confidence_min: float = 0.4
    food_imgsz: int = 800
    # auto: load ONNX. fake: CI stub. unavailable: force 503 without a model file.
    food_detector: str = "auto"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def resolved_food_model_path(self) -> Path:
        model_path = Path(self.food_model_path)
        if model_path.is_absolute():
            return model_path
        return ROOT_DIR / model_path


settings = Settings()
