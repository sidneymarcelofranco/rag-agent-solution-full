"""
Busca híbrida (semântica + palavra-chave) com re-ranking.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sentence_transformers import CrossEncoder
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado de busca."""

    chunk_id: int
    document_id: int
    content: str
    score: float
    search_type: str
    metadata: Dict[str, Any]


class KeywordSearch:
    """Busca por palavra-chave (BM25 ou regex)."""

    def __init__(self):
        """Inicializa busca por palavra-chave."""
        self.weight = settings.hybrid_search_weight_keyword

    async def search(
        self, query: str, documents: List[Dict[str, Any]], top_k: int = 10
    ) -> List[SearchResult]:
        """
        Busca por palavras-chave.

        Args:
            query: Query de busca
            documents: Lista de documentos
            top_k: Número de resultados

        Returns:
            Lista de resultados
        """
        try:
            # Normalizar query
            query_terms = self._normalize_query(query)

            if not query_terms:
                logger.warning("Query vazia após normalização")
                return []

            logger.info(f"Buscando por palavras-chave: {query_terms}")

            results = []

            for doc in documents:
                content = doc.get("content", "").lower()
                score = self._calculate_score(query_terms, content)

                if score > 0:
                    results.append(
                        SearchResult(
                            chunk_id=doc.get("id"),
                            document_id=doc.get("document_id"),
                            content=doc.get("content", ""),
                            score=score * self.weight,
                            search_type="keyword",
                            metadata=doc.get("metadata", {}),
                        )
                    )

            # Ordenar por score
            results.sort(key=lambda x: x.score, reverse=True)

            return results[:top_k]

        except Exception as e:
            logger.error(f"Erro em busca por palavra-chave: {e}")
            return []

    def _normalize_query(self, query: str) -> List[str]:
        """Normaliza query em termos."""
        # Remover pontuação e converter para minúsculas
        query = re.sub(r"[^\w\s]", " ", query.lower())
        terms = query.split()

        # Remover stopwords comuns
        stopwords = {"o", "a", "de", "em", "para", "com", "por", "e", "ou", "é", "que"}
        terms = [t for t in terms if t not in stopwords and len(t) > 2]

        return terms

    def _calculate_score(self, query_terms: List[str], content: str) -> float:
        """Calcula score BM25 simplificado."""
        score = 0.0
        content_lower = content.lower()

        for term in query_terms:
            # Contar ocorrências
            count = content_lower.count(term)

            if count > 0:
                # BM25 simplificado
                score += count / (1 + count * 0.1)

        return score


class SemanticSearch:
    """Busca semântica usando embeddings."""

    def __init__(self):
        """Inicializa busca semântica."""
        self.weight = settings.hybrid_search_weight_semantic

    async def search(
        self,
        query_embedding: List[float],
        vector_store,
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[SearchResult]:
        """
        Busca semântica usando embeddings.

        Args:
            query_embedding: Embedding da query
            vector_store: Store vetorial
            top_k: Número de resultados
            threshold: Limiar de similaridade

        Returns:
            Lista de resultados
        """
        try:
            logger.info(f"Buscando semanticamente (top_k={top_k})")

            results_raw = await vector_store.search_similar(
                query_embedding=query_embedding, top_k=top_k, threshold=threshold
            )

            results = []

            for result in results_raw:
                results.append(
                    SearchResult(
                        chunk_id=result.get("id"),
                        document_id=result.get("document_id"),
                        content=result.get("content", ""),
                        score=result.get("similarity", 0.0) * self.weight,
                        search_type="semantic",
                        metadata=result.get("metadata", {}),
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Erro em busca semântica: {e}")
            return []


class HybridSearch:
    """Combina busca semântica e por palavra-chave."""

    def __init__(self):
        """Inicializa busca híbrida."""
        self.keyword_search = KeywordSearch()
        self.semantic_search = SemanticSearch()
        self.reranker = None

        # Carregar modelo de re-ranking
        try:
            logger.info(f"Carregando modelo de re-ranking: {settings.rerank_model}")
            self.reranker = CrossEncoder(settings.rerank_model)
            logger.info("Modelo de re-ranking carregado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao carregar re-ranker: {e}. Continuando sem re-ranking.")

    async def search(
        self,
        query: str,
        query_embedding: List[float],
        vector_store,
        keyword_documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        Busca híbrida combinando semântica e palavra-chave.

        Args:
            query: Query de busca
            query_embedding: Embedding da query
            vector_store: Store vetorial
            keyword_documents: Documentos para busca por palavra-chave
            top_k: Número de resultados finais

        Returns:
            Lista de resultados ordenados
        """
        try:
            logger.info("Iniciando busca híbrida")

            # Busca semântica
            semantic_results = await self.semantic_search.search(
                query_embedding=query_embedding,
                vector_store=vector_store,
                top_k=top_k * 2,
            )

            # Busca por palavra-chave
            keyword_results = await self.keyword_search.search(
                query=query, documents=keyword_documents, top_k=top_k * 2
            )

            # Combinar resultados
            combined_results = self._combine_results(semantic_results, keyword_results)

            # Re-ranking
            if self.reranker and combined_results:
                combined_results = await self._rerank_results(query, combined_results)

            # Ordenar e retornar top_k
            combined_results.sort(key=lambda x: x.score, reverse=True)

            logger.info(f"Busca híbrida retornou {len(combined_results[:top_k])} resultados")

            return combined_results[:top_k]

        except Exception as e:
            logger.error(f"Erro em busca híbrida: {e}")
            return []

    def _combine_results(
        self, semantic_results: List[SearchResult], keyword_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Combina resultados de ambas as buscas."""
        # Usar dicionário para evitar duplicatas
        combined = {}

        for result in semantic_results:
            key = (result.chunk_id, result.document_id)
            if key not in combined:
                combined[key] = result
            else:
                # Somar scores se duplicado
                combined[key].score += result.score

        for result in keyword_results:
            key = (result.chunk_id, result.document_id)
            if key not in combined:
                combined[key] = result
            else:
                combined[key].score += result.score

        return list(combined.values())

    async def _rerank_results(
        self, query: str, results: List[SearchResult]
    ) -> List[SearchResult]:
        """Re-ranking usando cross-encoder."""
        try:
            if not self.reranker or not results:
                return results

            logger.info(f"Re-ranking {len(results)} resultados")

            # Preparar pares query-documento
            pairs = [(query, result.content) for result in results]

            # Calcular scores
            scores = self.reranker.predict(pairs)

            # Atualizar scores dos resultados
            for result, score in zip(results, scores):
                result.score = float(score)

            logger.info("Re-ranking concluído")

            return results

        except Exception as e:
            logger.error(f"Erro ao re-rankear resultados: {e}")
            return results
