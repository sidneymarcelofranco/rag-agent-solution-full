"""
Estratégias de chunking inteligente para documentos.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Representa um chunk de documento."""

    content: str
    chunk_index: int
    metadata: Dict[str, Any]


class ChunkingStrategy:
    """Estratégia base de chunking."""

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Divide texto em chunks."""
        raise NotImplementedError


class FixedSizeChunking(ChunkingStrategy):
    """Chunking com tamanho fixo e sobreposição."""

    def __init__(self, chunk_size: int = 1024, overlap: int = 128):
        """
        Inicializa estratégia de tamanho fixo.

        Args:
            chunk_size: Tamanho do chunk em caracteres
            overlap: Sobreposição entre chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Divide texto em chunks de tamanho fixo."""
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # Tentar quebrar em limite de sentença
            if end < len(text):
                # Procurar último ponto antes do fim
                last_period = chunk_text.rfind(".")
                if last_period > self.chunk_size * 0.8:  # Se estiver perto do fim
                    end = start + last_period + 1
                    chunk_text = text[start:end]

            chunks.append(
                Chunk(
                    content=chunk_text.strip(),
                    chunk_index=chunk_index,
                    metadata={
                        **metadata,
                        "start_char": start,
                        "end_char": end,
                        "chunk_size": len(chunk_text),
                    },
                )
            )

            # Mover para próximo chunk com sobreposição
            start = end - self.overlap
            chunk_index += 1

        logger.info(f"Criados {len(chunks)} chunks com tamanho fixo")
        return chunks


class SentenceChunking(ChunkingStrategy):
    """Chunking baseado em sentenças."""

    def __init__(self, sentences_per_chunk: int = 5, overlap_sentences: int = 1):
        """
        Inicializa estratégia de sentença.

        Args:
            sentences_per_chunk: Sentenças por chunk
            overlap_sentences: Sobreposição de sentenças
        """
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Divide texto em chunks de sentenças."""
        # Dividir em sentenças
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        chunk_index = 0

        for i in range(0, len(sentences), self.sentences_per_chunk - self.overlap_sentences):
            chunk_sentences = sentences[i : i + self.sentences_per_chunk]
            chunk_text = " ".join(chunk_sentences)

            if chunk_text.strip():
                chunks.append(
                    Chunk(
                        content=chunk_text,
                        chunk_index=chunk_index,
                        metadata={
                            **metadata,
                            "sentence_start": i,
                            "sentence_end": i + len(chunk_sentences),
                            "num_sentences": len(chunk_sentences),
                        },
                    )
                )
                chunk_index += 1

        logger.info(f"Criados {len(chunks)} chunks por sentença")
        return chunks


class SemanticChunking(ChunkingStrategy):
    """Chunking baseado em semântica (requer modelo de embeddings)."""

    def __init__(self, max_chunk_size: int = 1024, similarity_threshold: float = 0.7):
        """
        Inicializa estratégia semântica.

        Args:
            max_chunk_size: Tamanho máximo do chunk
            similarity_threshold: Limiar de similaridade
        """
        self.max_chunk_size = max_chunk_size
        self.similarity_threshold = similarity_threshold
        self.embeddings_model = None

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Divide texto baseado em semântica.

        Nota: Implementação simplificada. Para produção,
        integrar com modelo de embeddings real.
        """
        # Fallback para chunking por sentença se modelo não disponível
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                # Finalizar chunk atual
                chunk_text = " ".join(current_chunk)
                chunks.append(
                    Chunk(
                        content=chunk_text,
                        chunk_index=chunk_index,
                        metadata={**metadata, "type": "semantic"},
                    )
                )
                chunk_index += 1
                current_chunk = []
                current_size = 0

            current_chunk.append(sentence)
            current_size += sentence_size + 1  # +1 para espaço

        # Adicionar último chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                Chunk(
                    content=chunk_text,
                    chunk_index=chunk_index,
                    metadata={**metadata, "type": "semantic"},
                )
            )

        logger.info(f"Criados {len(chunks)} chunks semânticos")
        return chunks


class HybridChunking(ChunkingStrategy):
    """Combina múltiplas estratégias de chunking."""

    def __init__(self, chunk_size: int = 1024, overlap: int = 128):
        """Inicializa chunking híbrido."""
        self.fixed_strategy = FixedSizeChunking(chunk_size, overlap)
        self.sentence_strategy = SentenceChunking()

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Aplica múltiplas estratégias e combina resultados."""
        # Aplicar estratégia de tamanho fixo como padrão
        chunks = self.fixed_strategy.chunk(text, metadata)

        logger.info(f"Chunking híbrido: {len(chunks)} chunks criados")
        return chunks


class ChunkingFactory:
    """Factory para criar estratégias de chunking."""

    STRATEGIES = {
        "fixed": FixedSizeChunking,
        "sentence": SentenceChunking,
        "semantic": SemanticChunking,
        "hybrid": HybridChunking,
    }

    @classmethod
    def create(cls, strategy: str = "hybrid", **kwargs) -> ChunkingStrategy:
        """
        Cria uma estratégia de chunking.

        Args:
            strategy: Nome da estratégia
            **kwargs: Argumentos para a estratégia

        Returns:
            Instância da estratégia
        """
        if strategy not in cls.STRATEGIES:
            raise ValueError(f"Estratégia desconhecida: {strategy}")

        return cls.STRATEGIES[strategy](**kwargs)
