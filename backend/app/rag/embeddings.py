"""
Geração de embeddings e integração com PgVector.
"""

import logging
from typing import List, Optional
import numpy as np

from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Gera embeddings para textos usando modelos pré-treinados."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Inicializa gerador de embeddings.

        Args:
            model_name: Nome do modelo (padrão: all-MiniLM-L6-v2)
        """
        self.model_name = model_name or settings.embedding_model
        self.vector_dimension = settings.vector_dimension

        logger.info(f"Carregando modelo de embeddings: {self.model_name}")

        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Modelo carregado com sucesso. Dimensão: {self.vector_dimension}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto.

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats representando o embedding
        """
        try:
            # Normalizar texto
            text = text.strip()
            if not text:
                logger.warning("Texto vazio para embedding")
                return [0.0] * self.vector_dimension

            # Gerar embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Converter para lista
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para múltiplos textos.

        Args:
            texts: Lista de textos

        Returns:
            Lista de embeddings
        """
        try:
            # Normalizar textos
            texts = [t.strip() for t in texts if t.strip()]

            if not texts:
                logger.warning("Nenhum texto válido para embeddings")
                return []

            logger.info(f"Gerando embeddings para {len(texts)} textos")

            # Gerar embeddings em batch
            embeddings = self.model.encode(texts, convert_to_numpy=True)

            # Converter para lista de listas
            return embeddings.tolist()

        except Exception as e:
            logger.error(f"Erro ao gerar embeddings em batch: {e}")
            raise

    async def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos.

        Args:
            text1: Primeiro texto
            text2: Segundo texto

        Returns:
            Similaridade (0-1)
        """
        try:
            embeddings = await self.generate_embeddings_batch([text1, text2])

            if len(embeddings) < 2:
                return 0.0

            # Calcular similaridade cosseno
            emb1 = np.array(embeddings[0])
            emb2 = np.array(embeddings[1])

            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

            return float(similarity)

        except Exception as e:
            logger.error(f"Erro ao calcular similaridade: {e}")
            return 0.0

    def get_dimension(self) -> int:
        """Retorna dimensão dos embeddings."""
        return self.vector_dimension


class VectorStore:
    """Interface para armazenamento vetorial no PgVector."""

    def __init__(self, db_connection):
        """
        Inicializa store vetorial.

        Args:
            db_connection: Conexão com banco de dados
        """
        self.db = db_connection
        self.embeddings_gen = EmbeddingsGenerator()

    async def add_vectors(
        self,
        document_id: int,
        chunks: List[dict],
        embeddings: List[List[float]],
    ) -> bool:
        """
        Adiciona vetores ao banco.

        Args:
            document_id: ID do documento
            chunks: Lista de chunks
            embeddings: Lista de embeddings

        Returns:
            True se bem-sucedido
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Número de chunks diferente de embeddings")

            logger.info(f"Adicionando {len(chunks)} vetores para documento {document_id}")

            # Inserir chunks com embeddings
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                await self.db.add_chunk(
                    document_id=document_id,
                    chunk_index=idx,
                    content=chunk["content"],
                    embedding=embedding,
                    metadata=chunk.get("metadata", {}),
                )

            logger.info(f"Vetores adicionados com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao adicionar vetores: {e}")
            raise

    async def search_similar(
        self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.7
    ) -> List[dict]:
        """
        Busca vetores similares.

        Args:
            query_embedding: Embedding da query
            top_k: Número de resultados
            threshold: Limiar de similaridade

        Returns:
            Lista de resultados similares
        """
        try:
            logger.info(f"Buscando {top_k} vetores similares")

            results = await self.db.search_similar_vectors(
                embedding=query_embedding, top_k=top_k, threshold=threshold
            )

            logger.info(f"Encontrados {len(results)} resultados similares")
            return results

        except Exception as e:
            logger.error(f"Erro ao buscar vetores similares: {e}")
            raise

    async def delete_vectors(self, document_id: int) -> bool:
        """
        Deleta vetores de um documento.

        Args:
            document_id: ID do documento

        Returns:
            True se bem-sucedido
        """
        try:
            logger.info(f"Deletando vetores do documento {document_id}")

            await self.db.delete_chunks(document_id)

            logger.info(f"Vetores deletados com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao deletar vetores: {e}")
            raise

    async def get_stats(self) -> dict:
        """Retorna estatísticas do store vetorial."""
        try:
            stats = await self.db.get_vector_stats()
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
