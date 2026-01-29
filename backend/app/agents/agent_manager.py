"""
Gerenciador de agentes Agno para orquestração inteligente.
"""

import logging
from typing import Optional, List, Dict, Any

from app.agents.llm_config import GeminiFlashConfig
from app.rag.hybrid_search import HybridSearch
from app.rag.embeddings import EmbeddingsGenerator

logger = logging.getLogger(__name__)


class AgentManager:
    \"\"\"Gerencia múltiplos agentes especializados usando Agno.\"\"\"

    def __init__(self):
        \"\"\"Inicializa gerenciador de agentes.\"\"\"
        logger.info(\"Inicializando AgentManager\")

        self.llm_config = GeminiFlashConfig()
        self.hybrid_search = HybridSearch()
        self.embeddings_gen = EmbeddingsGenerator()

        # Agentes especializados
        self.agents = {
            \"rag_agent\": self._create_rag_agent(),
            \"summarizer_agent\": self._create_summarizer_agent(),
            \"qa_agent\": self._create_qa_agent(),
            \"extractor_agent\": self._create_extractor_agent(),
        }

        logger.info(f\"AgentManager inicializado com {len(self.agents)} agentes\")

    def _create_rag_agent(self) -> Dict[str, Any]:
        \"\"\"Cria agente especializado em RAG.\"\"\"
        return {
            \"name\": \"RAG Agent\",
            \"description\": \"Agente especializado em Retrieval-Augmented Generation\",
            \"role\": \"Buscar documentos relevantes e gerar respostas contextualizadas\",
            \"system_prompt\": \"\"\"Você é um assistente especializado em Retrieval-Augmented Generation.
Sua tarefa é:
1. Buscar documentos relevantes
2. Analisar o contexto
3. Gerar respostas precisas baseadas nos documentos
4. Sempre citar as fontes\"\"\",
        }

    def _create_summarizer_agent(self) -> Dict[str, Any]:
        \"\"\"Cria agente especializado em sumarização.\"\"\"
        return {
            \"name\": \"Summarizer Agent\",
            \"description\": \"Agente especializado em sumarização de documentos\",
            \"role\": \"Sumarizar documentos longos em pontos-chave\",
            \"system_prompt\": \"\"\"Você é um especialista em sumarização.
Sua tarefa é:
1. Identificar informações principais
2. Remover redundâncias
3. Manter contexto importante
4. Gerar sumários concisos e informativos\"\"\",
        }

    def _create_qa_agent(self) -> Dict[str, Any]:
        \"\"\"Cria agente especializado em Q&A.\"\"\"
        return {
            \"name\": \"QA Agent\",
            \"description\": \"Agente especializado em responder perguntas\",
            \"role\": \"Responder perguntas específicas baseado em documentos\",
            \"system_prompt\": \"\"\"Você é um especialista em responder perguntas.
Sua tarefa é:
1. Entender a pergunta
2. Buscar informações relevantes
3. Formular respostas claras e diretas
4. Indicar incertezas quando apropriado\"\"\",
        }

    def _create_extractor_agent(self) -> Dict[str, Any]:
        \"\"\"Cria agente especializado em extração de informações.\"\"\"
        return {
            \"name\": \"Extractor Agent\",
            \"description\": \"Agente especializado em extração de informações estruturadas\",
            \"role\": \"Extrair informações estruturadas de documentos\",
            \"system_prompt\": \"\"\"Você é um especialista em extração de informações.
Sua tarefa é:
1. Identificar entidades relevantes
2. Extrair informações estruturadas
3. Validar dados extraídos
4. Retornar em formato estruturado\"\"\",
        }

    async def process_query(
        self,
        query: str,
        agent_type: str = \"rag_agent\",
        context: Optional[str] = None,
        vector_store=None,
        keyword_documents: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        \"\"\"
        Processa query usando agente apropriado.

        Args:
            query: Query do usuário
            agent_type: Tipo de agente
            context: Contexto adicional
            vector_store: Store vetorial
            keyword_documents: Documentos para busca por palavra-chave

        Returns:
            Resultado processado
        \"\"\"
        try:
            if agent_type not in self.agents:
                raise ValueError(f\"Agente desconhecido: {agent_type}\")

            agent = self.agents[agent_type]

            logger.info(f\"Processando query com {agent['name']}\")

            # Gerar embedding da query
            query_embedding = await self.embeddings_gen.generate_embedding(query)

            # Busca híbrida
            search_results = []
            if vector_store and keyword_documents:
                search_results = await self.hybrid_search.search(
                    query=query,
                    query_embedding=query_embedding,
                    vector_store=vector_store,
                    keyword_documents=keyword_documents,
                    top_k=5,
                )

            # Preparar contexto
            search_context = \"\\n\".join(
                [f\"- {result.content[:200]}...\" for result in search_results]
            )

            full_context = f\"\"\"{context or \"\"}

Documentos Relevantes:
{search_context}\"\"\"

            # Gerar resposta
            response = await self.llm_config.answer_question(
                context=full_context, question=query, system_prompt=agent[\"system_prompt\"]
            )

            result = {
                \"agent\": agent[\"name\"],
                \"query\": query,
                \"response\": response,
                \"sources\": [
                    {
                        \"chunk_id\": result.chunk_id,
                        \"document_id\": result.document_id,
                        \"score\": result.score,
                        \"content\": result.content[:200],
                    }
                    for result in search_results
                ],
                \"metadata\": {
                    \"search_type\": \"hybrid\",
                    \"num_sources\": len(search_results),
                },
            }

            logger.info(f\"Query processada com sucesso\")

            return result

        except Exception as e:
            logger.error(f\"Erro ao processar query: {e}\")
            raise

    async def orchestrate_multi_agent(
        self, query: str, agents_sequence: List[str], context: Optional[str] = None
    ) -> Dict[str, Any]:
        \"\"\"
        Orquestra múltiplos agentes em sequência.

        Args:
            query: Query inicial
            agents_sequence: Sequência de agentes
            context: Contexto

        Returns:
            Resultado final
        \"\"\"
        try:
            logger.info(f\"Orquestrando {len(agents_sequence)} agentes\")

            current_context = context or \"\"
            results = []

            for agent_type in agents_sequence:
                logger.info(f\"Executando {agent_type}\")

                result = await self.process_query(
                    query=query, agent_type=agent_type, context=current_context
                )

                results.append(result)

                # Usar resposta anterior como contexto
                current_context = result[\"response\"]

            return {
                \"query\": query,
                \"agents_executed\": agents_sequence,
                \"results\": results,
                \"final_response\": results[-1][\"response\"] if results else \"\",
            }

        except Exception as e:
            logger.error(f\"Erro ao orquestrar agentes: {e}\")
            raise

    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        \"\"\"Retorna informações sobre um agente.\"\"\"
        if agent_type not in self.agents:
            raise ValueError(f\"Agente desconhecido: {agent_type}\")

        return self.agents[agent_type]

    def list_agents(self) -> List[Dict[str, str]]:
        \"\"\"Lista todos os agentes disponíveis.\"\"\"
        return [
            {\"name\": agent[\"name\"], \"description\": agent[\"description\"]}
            for agent in self.agents.values()
        ]
