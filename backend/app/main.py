"""
Aplicação FastAPI principal - RAG Agent Solution.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# Configurar logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="RAG Agent Solution",
    description="Plataforma de Retrieval-Augmented Generation com orquestração de agentes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Rotas básicas
@app.get("/health")
async def health_check():
    """Verifica saúde da aplicação."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.get("/")
async def root():
    """Rota raiz."""
    return {
        "message": "RAG Agent Solution API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/config")
async def get_config():
    """Retorna configurações públicas."""
    return {
        "embedding_model": settings.embedding_model,
        "vector_dimension": settings.vector_dimension,
        "chunk_size": settings.chunk_size,
        "top_k_results": settings.top_k_results,
        "environment": settings.environment,
    }


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler geral de exceções."""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "Um erro ocorreu no servidor",
        },
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação."""
    logger.info("=" * 50)
    logger.info("RAG Agent Solution iniciando...")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Modelo de embeddings: {settings.embedding_model}")
    logger.info(f"Modelo de re-ranking: {settings.rerank_model}")
    logger.info("=" * 50)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação."""
    logger.info("RAG Agent Solution desligando...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
    )
