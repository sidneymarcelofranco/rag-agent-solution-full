"""
Configuração centralizada da aplicação RAG.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""

    # ===== DATABASE =====
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://rag_user:rag_password@localhost:5432/rag_db"
    )
    sqlalchemy_echo: bool = False

    # ===== LLM - GEMINI FLASH =====
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))

    # ===== MINIO STORAGE =====
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket_name: str = os.getenv("MINIO_BUCKET_NAME", "rag-documents")
    minio_use_ssl: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

    # ===== GOOGLE DRIVE =====
    google_drive_enabled: bool = os.getenv("GOOGLE_DRIVE_ENABLED", "true").lower() == "true"
    google_drive_credentials_path: str = os.getenv(
        "GOOGLE_DRIVE_CREDENTIALS_PATH", "/app/secrets/google_drive_credentials.json"
    )
    google_drive_folder_id: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

    # ===== AUTHENTICATION =====
    jwt_secret: str = os.getenv("JWT_SECRET", "your_jwt_secret_key_change_this_in_production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change_this_password")

    # ===== RAG CONFIGURATION =====
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1024"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "128"))
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_dimension: int = int(os.getenv("VECTOR_DIMENSION", "384"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    hybrid_search_weight_semantic: float = float(
        os.getenv("HYBRID_SEARCH_WEIGHT_SEMANTIC", "0.7")
    )
    hybrid_search_weight_keyword: float = float(
        os.getenv("HYBRID_SEARCH_WEIGHT_KEYWORD", "0.3")
    )
    rerank_model: str = os.getenv(
        "RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-12-v2"
    )
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # ===== AGNO CONFIGURATION =====
    agno_log_level: str = os.getenv("AGNO_LOG_LEVEL", "INFO")
    agno_enable_memory: bool = os.getenv("AGNO_ENABLE_MEMORY", "true").lower() == "true"
    agno_enable_tools: bool = os.getenv("AGNO_ENABLE_TOOLS", "true").lower() == "true"

    # ===== API CONFIGURATION =====
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # ===== CORS =====
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://chainlit:8501",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # ===== ENVIRONMENT =====
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
