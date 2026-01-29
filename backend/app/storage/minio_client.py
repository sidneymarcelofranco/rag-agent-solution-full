"""
Cliente MinIO para armazenamento de documentos.
"""

import logging
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error

from app.config import settings

logger = logging.getLogger(__name__)


class MinIOClient:
    """Cliente para interagir com MinIO."""

    def __init__(self):
        """Inicializa cliente MinIO."""
        logger.info(f"Conectando ao MinIO: {settings.minio_endpoint}")

        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )

        self.bucket_name = settings.minio_bucket_name

        # Criar bucket se não existir
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Garante que o bucket existe."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                logger.info(f"Criando bucket: {self.bucket_name}")
                self.client.make_bucket(self.bucket_name)
            else:
                logger.info(f"Bucket já existe: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Erro ao criar bucket: {e}")
            raise

    async def upload_file(
        self, file_path: str, object_name: str, content_type: str = "application/octet-stream"
    ) -> str:
        """
        Faz upload de arquivo para MinIO.

        Args:
            file_path: Caminho local do arquivo
            object_name: Nome do objeto no MinIO
            content_type: Tipo MIME do arquivo

        Returns:
            URL do arquivo
        """
        try:
            logger.info(f"Fazendo upload: {file_path} -> {object_name}")

            self.client.fput_object(
                self.bucket_name, object_name, file_path, content_type=content_type
            )

            # Construir URL
            url = f"minio://{self.bucket_name}/{object_name}"

            logger.info(f"Upload bem-sucedido: {url}")
            return url

        except S3Error as e:
            logger.error(f"Erro ao fazer upload: {e}")
            raise

    async def upload_bytes(
        self, data: bytes, object_name: str, content_type: str = "application/octet-stream"
    ) -> str:
        """
        Faz upload de bytes para MinIO.

        Args:
            data: Dados em bytes
            object_name: Nome do objeto
            content_type: Tipo MIME

        Returns:
            URL do arquivo
        """
        try:
            logger.info(f"Fazendo upload de bytes: {object_name}")

            self.client.put_object(
                self.bucket_name,
                object_name,
                data=data,
                length=len(data),
                content_type=content_type,
            )

            url = f"minio://{self.bucket_name}/{object_name}"

            logger.info(f"Upload bem-sucedido: {url}")
            return url

        except S3Error as e:
            logger.error(f"Erro ao fazer upload de bytes: {e}")
            raise

    async def download_file(self, object_name: str, file_path: str) -> bool:
        """
        Baixa arquivo do MinIO.

        Args:
            object_name: Nome do objeto
            file_path: Caminho local para salvar

        Returns:
            True se bem-sucedido
        """
        try:
            logger.info(f"Baixando arquivo: {object_name} -> {file_path}")

            self.client.fget_object(self.bucket_name, object_name, file_path)

            logger.info(f"Download bem-sucedido")
            return True

        except S3Error as e:
            logger.error(f"Erro ao baixar arquivo: {e}")
            raise

    async def delete_file(self, object_name: str) -> bool:
        """
        Deleta arquivo do MinIO.

        Args:
            object_name: Nome do objeto

        Returns:
            True se bem-sucedido
        """
        try:
            logger.info(f"Deletando arquivo: {object_name}")

            self.client.remove_object(self.bucket_name, object_name)

            logger.info(f"Arquivo deletado com sucesso")
            return True

        except S3Error as e:
            logger.error(f"Erro ao deletar arquivo: {e}")
            raise

    async def list_objects(self, prefix: str = "") -> list:
        """
        Lista objetos no bucket.

        Args:
            prefix: Prefixo para filtrar

        Returns:
            Lista de objetos
        """
        try:
            logger.info(f"Listando objetos com prefixo: {prefix}")

            objects = self.client.list_objects(self.bucket_name, prefix=prefix)

            object_list = []
            for obj in objects:
                object_list.append(
                    {
                        "name": obj.object_name,
                        "size": obj.size,
                        "modified": obj.last_modified,
                    }
                )

            logger.info(f"Encontrados {len(object_list)} objetos")
            return object_list

        except S3Error as e:
            logger.error(f"Erro ao listar objetos: {e}")
            raise

    async def get_object_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Gera URL pré-assinada para objeto.

        Args:
            object_name: Nome do objeto
            expires: Tempo de expiração em segundos

        Returns:
            URL pré-assinada
        """
        try:
            logger.info(f"Gerando URL para: {object_name}")

            url = self.client.get_presigned_download_url(
                self.bucket_name, object_name, expires=expires
            )

            logger.info(f"URL gerada com sucesso")
            return url

        except S3Error as e:
            logger.error(f"Erro ao gerar URL: {e}")
            raise

    async def get_stats(self) -> dict:
        """Retorna estatísticas do bucket."""
        try:
            objects = await self.list_objects()

            total_size = sum(obj["size"] for obj in objects)

            return {
                "bucket": self.bucket_name,
                "object_count": len(objects),
                "total_size": total_size,
                "total_size_mb": total_size / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
