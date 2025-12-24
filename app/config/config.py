import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # -------------------- DATABASE CONFIG --------------------
    MONGO_URI: str = os.getenv("MONGO_URI")
    DB_NAME: str = os.getenv("DB_NAME")

    # -------------------- JWT CONFIG --------------------
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", 60))


# Global instance
settings = Settings()
