"""
Aplicação Chainlit principal - Interface de chat RAG.
"""

import os
import logging
from typing import Optional, Dict, Any
import httpx
import asyncio

import chainlit as cl
from chainlit.input_widget import Select, TextInput, Slider
from chainlit.auth import User

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", f"{BACKEND_URL}/api")

# Cliente HTTP
http_client = httpx.AsyncClient(base_url=BACKEND_API_URL, timeout=30.0)


# ===== AUTENTICAÇÃO =====


@cl.password_auth_callback
async def password_auth(username: str, password: str) -> Optional[cl.User]:
    """
    Autentica usuário com username e password.

    Args:
        username: Nome de usuário
        password: Senha

    Returns:
        Usuário autenticado ou None
    """
    try:
        logger.info(f"Autenticando usuário: {username}")

        # Chamar backend para autenticar
        response = await http_client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Usuário autenticado: {username}")

            return cl.User(
                identifier=data.get("user_id"),
                metadata={
                    "username": username,
                    "token": data.get("token"),
                    "is_admin": data.get("is_admin", False),
                },
            )
        else:
            logger.warning(f"Falha na autenticação: {username}")
            return None

    except Exception as e:
        logger.error(f"Erro ao autenticar: {e}")
        return None


# ===== CONFIGURAÇÃO DA SESSÃO =====


@cl.on_chat_start
async def on_chat_start():
    """Executado ao iniciar nova sessão de chat."""
    logger.info("Nova sessão de chat iniciada")

    # Obter usuário autenticado
    user = cl.user_session.get("user")

    # Inicializar estado da sessão
    cl.user_session.set(
        "session_data",
        {
            "user_id": user.identifier if user else None,
            "username": user.metadata.get("username") if user else "Anonymous",
            "token": user.metadata.get("token") if user else None,
            "is_admin": user.metadata.get("is_admin", False) if user else False,
            "messages": [],
            "agent_type": "rag_agent",
        },
    )

    # Mensagem de boas-vindas
    welcome_message = """
# 🤖 Bem-vindo ao RAG Agent Solution

Olá! Sou um assistente inteligente alimentado por **Retrieval-Augmented Generation**.

## Como funciono:
- 📚 Busco informações em documentos relevantes
- 🧠 Uso IA para gerar respostas contextualizadas
- 📌 Cito as fontes consultadas

## Disponível para:
- ❓ Responder perguntas
- 📝 Sumarizar documentos
- 🔍 Extrair informações
- 💬 Conversar sobre qualquer tópico

**Comece fazendo uma pergunta!**
"""

    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):
    """
    Processa mensagens do usuário.

    Args:
        message: Mensagem recebida
    """
    try:
        logger.info(f"Mensagem recebida: {message.content[:100]}")

        # Obter dados da sessão
        session_data = cl.user_session.get("session_data")

        # Mostrar indicador de digitação
        async with cl.Step(name="Processando...") as step:
            step.status = "Processando sua pergunta..."

            # Chamar backend
            response_data = await query_backend(
                query=message.content,
                agent_type=session_data.get("agent_type", "rag_agent"),
                token=session_data.get("token"),
            )

            step.status = "Gerando resposta..."

        # Preparar resposta
        response_content = response_data.get("response", "Desculpe, não consegui gerar uma resposta.")

        # Adicionar informações de fontes
        sources = response_data.get("sources", [])

        if sources:
            sources_text = "\n\n### 📚 Fontes Consultadas:\n"
            for idx, source in enumerate(sources, 1):
                sources_text += f"\n**Fonte {idx}** (Score: {source.get('score', 0):.2f})\n"
                sources_text += f"> {source.get('content', '')[:200]}...\n"

            response_content += sources_text

        # Enviar resposta
        await cl.Message(content=response_content).send()

        # Atualizar histórico
        session_data["messages"].append(
            {"role": "user", "content": message.content}
        )
        session_data["messages"].append(
            {"role": "assistant", "content": response_content}
        )

        cl.user_session.set("session_data", session_data)

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await cl.Message(
            content=f"❌ Erro ao processar sua mensagem: {str(e)}"
        ).send()


# ===== FUNÇÕES AUXILIARES =====


async def query_backend(
    query: str, agent_type: str = "rag_agent", token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consulta backend para processar query.

    Args:
        query: Query do usuário
        agent_type: Tipo de agente
        token: Token JWT

    Returns:
        Resposta do backend
    """
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = await http_client.post(
            "/chat/query",
            json={"query": query, "agent_type": agent_type},
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro no backend: {response.status_code}")
            return {
                "response": "Erro ao processar no backend",
                "sources": [],
            }

    except Exception as e:
        logger.error(f"Erro ao consultar backend: {e}")
        return {
            "response": f"Erro de conexão: {str(e)}",
            "sources": [],
        }


# ===== AÇÕES CUSTOMIZADAS =====


@cl.action_callback("upload_document")
async def upload_document(action):
    """Callback para upload de documento."""
    logger.info("Upload de documento iniciado")
    await cl.Message(
        content="📁 Funcionalidade de upload será implementada em breve!"
    ).send()


@cl.action_callback("change_agent")
async def change_agent(action):
    """Callback para mudar agente."""
    logger.info("Mudança de agente")
    session_data = cl.user_session.get("session_data")
    session_data["agent_type"] = action.value
    cl.user_session.set("session_data", session_data)

    await cl.Message(
        content=f"✅ Agente alterado para: {action.value}"
    ).send()


# ===== CONFIGURAÇÃO CHAINLIT =====


settings = {
    "ui": {
        "name": "RAG Agent Solution",
        "description": "Plataforma de Retrieval-Augmented Generation",
        "theme": "light",
        "show_readme_as_default": False,
    },
}
