"""
Manipulação de tokens JWT para autenticação.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from app.config import settings

logger = logging.getLogger(__name__)


class JWTHandler:
    """Manipula criação e validação de tokens JWT."""

    def __init__(self):
        """Inicializa manipulador JWT."""
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expiration_hours = settings.jwt_expiration_hours

    def create_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria um token JWT.

        Args:
            data: Dados para incluir no token
            expires_delta: Tempo de expiração customizado

        Returns:
            Token JWT
        """
        try:
            to_encode = data.copy()

            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(hours=self.expiration_hours)

            to_encode.update({"exp": expire})

            encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

            logger.info(f"Token criado para usuário: {data.get('user_id')}")

            return encoded_jwt

        except Exception as e:
            logger.error(f"Erro ao criar token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica e decodifica um token JWT.

        Args:
            token: Token JWT

        Returns:
            Dados do token ou None se inválido
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])

            logger.debug(f"Token verificado para usuário: {payload.get('user_id')}")

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None

        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {e}")
            return None

        except Exception as e:
            logger.error(f"Erro ao verificar token: {e}")
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """
        Renova um token JWT.

        Args:
            token: Token atual

        Returns:
            Novo token ou None se inválido
        """
        try:
            payload = self.verify_token(token)

            if not payload:
                return None

            # Remover campo exp para criar novo
            payload.pop("exp", None)

            new_token = self.create_token(payload)

            logger.info(f"Token renovado para usuário: {payload.get('user_id')}")

            return new_token

        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            return None

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Obtém data de expiração do token.

        Args:
            token: Token JWT

        Returns:
            Data de expiração ou None
        """
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm], options={"verify_exp": False}
            )

            exp_timestamp = payload.get("exp")

            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)

            return None

        except Exception as e:
            logger.error(f"Erro ao obter expiração do token: {e}")
            return None
