"""
Processamento de documentos: PDF, TXT, LOG e extração de dados SQL.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

import PyPDF2
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processa diferentes tipos de documentos."""

    SUPPORTED_FORMATS = {".pdf", ".txt", ".log", ".csv", ".json"}

    def __init__(self):
        """Inicializa o processador de documentos."""
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Processa um arquivo e extrai seu conteúdo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com metadados e conteúdo
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato não suportado: {file_ext}")

        logger.info(f"Processando arquivo: {file_path}")

        if file_ext == ".pdf":
            content = await self._process_pdf(file_path)
        elif file_ext == ".txt":
            content = await self._process_text(file_path)
        elif file_ext == ".log":
            content = await self._process_log(file_path)
        elif file_ext == ".csv":
            content = await self._process_csv(file_path)
        elif file_ext == ".json":
            content = await self._process_json(file_path)
        else:
            raise ValueError(f"Tipo de arquivo não tratado: {file_ext}")

        return {
            "file_path": file_path,
            "file_type": file_ext,
            "file_size": os.path.getsize(file_path),
            "content": content,
            "metadata": {
                "processed_at": str(Path(file_path).stat().st_mtime),
                "format": file_ext,
            },
        }

    async def _process_pdf(self, file_path: str) -> str:
        """Extrai texto de PDF."""
        try:
            text_content = []

            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)

                logger.info(f"PDF com {num_pages} páginas")

                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Página {page_num + 1} ---\n{text}")

            return "\n".join(text_content)

        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")
            raise

    async def _process_text(self, file_path: str) -> str:
        """Lê arquivo de texto simples."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentar com encoding diferente
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    async def _process_log(self, file_path: str) -> str:
        """Processa arquivo de log."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Estruturar logs com metadados
            structured_logs = []
            for line in lines:
                line = line.strip()
                if line:
                    # Tentar extrair timestamp e nível
                    structured_logs.append(line)

            return "\n".join(structured_logs)

        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    async def _process_csv(self, file_path: str) -> str:
        """Processa arquivo CSV."""
        try:
            import csv

            content = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    content.append(json.dumps(row, ensure_ascii=False))

            return "\n".join(content)

        except Exception as e:
            logger.error(f"Erro ao processar CSV: {e}")
            raise

    async def _process_json(self, file_path: str) -> str:
        """Processa arquivo JSON."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Converter para string formatada
            return json.dumps(data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Erro ao processar JSON: {e}")
            raise

    async def extract_sql_data(
        self, connection_string: str, query: str
    ) -> List[Dict[str, Any]]:
        """
        Extrai dados de um banco relacional via SQL.

        Args:
            connection_string: String de conexão do banco
            query: Query SQL

        Returns:
            Lista de registros
        """
        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(connection_string)

            with engine.connect() as connection:
                result = connection.execute(text(query))
                rows = result.fetchall()

                # Converter para dicionários
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]

            logger.info(f"Extraídos {len(data)} registros do banco")
            return data

        except Exception as e:
            logger.error(f"Erro ao extrair dados SQL: {e}")
            raise

    async def extract_text_from_sql(
        self, connection_string: str, query: str
    ) -> str:
        """
        Extrai dados SQL e converte para texto estruturado.

        Args:
            connection_string: String de conexão
            query: Query SQL

        Returns:
            Texto estruturado
        """
        data = await self.extract_sql_data(connection_string, query)

        # Converter para formato legível
        text_lines = []
        for idx, record in enumerate(data, 1):
            text_lines.append(f"Registro {idx}:")
            for key, value in record.items():
                text_lines.append(f"  {key}: {value}")
            text_lines.append("")

        return "\n".join(text_lines)

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Obtém informações sobre um arquivo."""
        path = Path(file_path)

        return {
            "name": path.name,
            "size": path.stat().st_size,
            "type": path.suffix,
            "created": str(path.stat().st_ctime),
            "modified": str(path.stat().st_mtime),
        }
