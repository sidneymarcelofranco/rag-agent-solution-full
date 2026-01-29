"""
Configuração e integração com Google Gemini Flash API.
"""

import logging
from typing import Optional, List, Dict, Any

import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiFlashConfig:
    """Configuração do Gemini Flash para uso com Agno."""

    def __init__(self):
        """Inicializa configuração do Gemini Flash."""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

        logger.info("Configurando Google Gemini Flash API")

        # Configurar API key
        genai.configure(api_key=settings.gemini_api_key)

        self.model_name = settings.gemini_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

        logger.info(f"Modelo: {self.model_name}")
        logger.info(f"Temperatura: {self.temperature}")
        logger.info(f"Max tokens: {self.max_tokens}")

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Gera resposta usando Gemini Flash.

        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens

        Returns:
            Resposta gerada
        """
        try:
            temp = temperature or self.temperature
            max_tok = max_tokens or self.max_tokens

            # Combinar prompts
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            logger.info(f"Gerando resposta com Gemini Flash")

            # Criar modelo
            model = genai.GenerativeModel(self.model_name)

            # Gerar conteúdo
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temp,
                    max_output_tokens=max_tok,
                ),
            )

            if not response.text:
                logger.warning("Resposta vazia do Gemini")
                return ""

            logger.info(f"Resposta gerada com sucesso ({len(response.text)} caracteres)")

            return response.text

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            raise

    async def generate_response_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Gera resposta com streaming usando Gemini Flash.

        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema
            temperature: Temperatura
            max_tokens: Máximo de tokens

        Yields:
            Chunks de texto
        """
        try:
            temp = temperature or self.temperature
            max_tok = max_tokens or self.max_tokens

            # Combinar prompts
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt

            logger.info(f"Gerando resposta com streaming")

            # Criar modelo
            model = genai.GenerativeModel(self.model_name)

            # Gerar conteúdo com streaming
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temp,
                    max_output_tokens=max_tok,
                ),
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

            logger.info("Streaming concluído")

        except Exception as e:
            logger.error(f"Erro ao gerar resposta com streaming: {e}")
            raise

    async def extract_info(
        self, text: str, instructions: str, format_spec: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extrai informações estruturadas de texto.

        Args:
            text: Texto para extrair
            instructions: Instruções de extração
            format_spec: Especificação de formato (JSON schema)

        Returns:
            Informações extraídas
        """
        try:
            prompt = f"""Extraia informações do seguinte texto:

Texto:
{text}

Instruções:
{instructions}

{f"Formato esperado: {format_spec}" if format_spec else ""}

Retorne as informações extraídas."""

            response = await self.generate_response(prompt)

            # Tentar parsear como JSON se format_spec for JSON
            if format_spec and "json" in format_spec.lower():
                import json

                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logger.warning("Não foi possível parsear resposta como JSON")
                    return {"raw": response}

            return {"raw": response}

        except Exception as e:
            logger.error(f"Erro ao extrair informações: {e}")
            raise

    async def summarize(self, text: str, max_length: int = 500) -> str:
        """
        Sumariza um texto.

        Args:
            text: Texto para sumarizar
            max_length: Comprimento máximo do sumário

        Returns:
            Sumário
        """
        try:
            prompt = f"""Sumarize o seguinte texto em no máximo {max_length} caracteres:

{text}

Sumário:"""

            summary = await self.generate_response(
                prompt, max_tokens=int(max_length / 4)  # Aproximação
            )

            return summary.strip()

        except Exception as e:
            logger.error(f"Erro ao sumarizar: {e}")
            raise

    async def answer_question(
        self, context: str, question: str, system_prompt: Optional[str] = None
    ) -> str:
        """
        Responde pergunta baseada em contexto.

        Args:
            context: Contexto/documentos
            question: Pergunta
            system_prompt: Prompt do sistema customizado

        Returns:
            Resposta
        """
        try:
            default_system = """Você é um assistente útil que responde perguntas baseado no contexto fornecido.
Sempre cite as fontes do contexto quando aplicável.
Se a resposta não estiver no contexto, diga claramente que não tem informação suficiente."""

            system = system_prompt or default_system

            prompt = f"""Contexto:
{context}

Pergunta: {question}

Resposta:"""

            answer = await self.generate_response(prompt, system_prompt=system)

            return answer.strip()

        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api": "Google Gemini Flash",
            "cost": "Free Tier (15 RPM)",
        }
