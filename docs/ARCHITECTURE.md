# Arquitetura da Plataforma RAG Agent Solution

## Visão Geral

A plataforma RAG Agent Solution é uma solução completa de **Retrieval-Augmented Generation (RAG)** com orquestração de agentes inteligentes, projetada para responder perguntas contextualizadas baseadas em múltiplas fontes de dados.

## Componentes Principais

### 1. Pipeline RAG

O pipeline RAG implementa um fluxo completo de processamento de documentos:

```
Documentos (PDF/TXT/LOG/SQL)
    ↓
[Document Processor] - Extração de conteúdo
    ↓
[Chunking Strategy] - Divisão em chunks
    ↓
[Embeddings Generator] - Geração de vetores
    ↓
[PgVector Store] - Armazenamento vetorial
    ↓
[Hybrid Search] - Busca semântica + palavra-chave
    ↓
[Re-ranking] - Ordenação inteligente
    ↓
Resultados Relevantes
```

#### 1.1 Document Processor
- **Suporte a formatos**: PDF, TXT, LOG, CSV, JSON
- **Extração SQL**: Consultas a bancos relacionais
- **Normalização**: Tratamento de encoding e formatação

#### 1.2 Chunking Strategies
- **Fixed Size**: Chunks de tamanho fixo com sobreposição
- **Sentence**: Chunking baseado em sentenças
- **Semantic**: Chunking inteligente por semântica
- **Hybrid**: Combinação de estratégias

#### 1.3 Embeddings Generator
- **Modelo**: Sentence Transformers (all-MiniLM-L6-v2)
- **Dimensão**: 384 (configurável)
- **Processamento**: Batch e individual
- **Similaridade**: Cálculo cosseno

#### 1.4 Hybrid Search
- **Busca Semântica**: Via PgVector + HNSW
- **Busca Keyword**: BM25 simplificado
- **Re-ranking**: Cross-Encoder (ms-marco-MiniLM-L-12-v2)
- **Ponderação**: Configurável (0.7 semântica, 0.3 keyword)

### 2. Hub de Agentes Agno

Orquestração de múltiplos agentes especializados:

```
Query do Usuário
    ↓
[Agent Manager]
    ├─→ [RAG Agent] - Busca e síntese
    ├─→ [QA Agent] - Resposta a perguntas
    ├─→ [Summarizer Agent] - Sumarização
    └─→ [Extractor Agent] - Extração de informações
    ↓
Resposta Contextualizada
```

#### 2.1 Agentes Disponíveis
- **RAG Agent**: Retrieval-Augmented Generation
- **QA Agent**: Question Answering
- **Summarizer Agent**: Sumarização de documentos
- **Extractor Agent**: Extração de informações estruturadas

#### 2.2 Orquestração Multi-Agente
- Execução sequencial de agentes
- Passagem de contexto entre agentes
- Memória persistente (futuro)

### 3. LLM - Google Gemini Flash

Integração com API gratuita do Google:

```
Prompt + Contexto
    ↓
[Gemini Flash API]
    ├─ Temperatura: 0.3 (determinístico)
    ├─ Max Tokens: 2048
    └─ Free Tier: 15 RPM
    ↓
Resposta Gerada
```

**Características**:
- Free Tier com limite de 15 requisições por minuto
- Janela de contexto: 1M tokens
- Suporte a streaming
- Custo: $0 (Free Tier)

### 4. Armazenamento

#### 4.1 MinIO (Armazenamento Local)
- Compatível com S3
- Suporte a uploads/downloads
- URLs pré-assinadas
- Gestão de buckets

#### 4.2 Google Drive (Backup)
- Sincronização automática
- Backup de documentos
- Compartilhamento

#### 4.3 PostgreSQL + PgVector
- Banco relacional principal
- Extensão PgVector para vetores
- Índice HNSW para busca rápida
- Metadados e histórico

### 5. Interface Chainlit

Frontend moderno para chat:

```
Usuário
    ↓
[Chainlit Interface]
    ├─ Chat com streaming
    ├─ Autenticação JWT
    ├─ Histórico de conversas
    └─ Exibição de fontes
    ↓
[Backend FastAPI]
    ↓
Resposta Processada
```

**Funcionalidades**:
- Chat em tempo real
- Streaming de respostas
- Exibição de fontes consultadas
- Autenticação com login/senha
- Área administrativa

### 6. Autenticação

#### 6.1 JWT (JSON Web Tokens)
- Tokens com expiração
- Refresh tokens
- Claims customizados
- Algoritmo: HS256

#### 6.2 Controle de Acesso
- Admin vs Usuário
- Permissões por recurso
- Auditoria de ações

## Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    USUÁRIO FINAL                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Chainlit Interface       │
        │  - Chat com Streaming      │
        │  - Autenticação JWT        │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   FastAPI Backend          │
        │  - Rotas HTTP              │
        │  - Validação               │
        └────────────┬───────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
    ┌─────────────┐        ┌──────────────┐
    │Agent Manager│        │ RAG Pipeline │
    │  - Agentes  │        │ - Busca      │
    │  - LLM      │        │ - Ranking    │
    └──────┬──────┘        └──────┬───────┘
           │                      │
           └──────────┬───────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
    ┌──────────────┐         ┌─────────────┐
    │ PostgreSQL   │         │   MinIO     │
    │  + PgVector  │         │  + GDrive   │
    │ - Vetores    │         │ - Docs      │
    │ - Metadata   │         │ - Backup    │
    └──────────────┘         └─────────────┘
```

## Padrões de Design

### 1. Factory Pattern
- `ChunkingFactory`: Criação de estratégias de chunking
- `AgentFactory`: Criação de agentes

### 2. Strategy Pattern
- `ChunkingStrategy`: Múltiplas estratégias de chunking
- `SearchStrategy`: Busca semântica vs keyword

### 3. Manager Pattern
- `AgentManager`: Orquestração de agentes
- `StorageManager`: Gestão de armazenamento

### 4. Service Layer
- Separação entre lógica de negócio e API
- Reutilização de código

## Segurança

### 1. Autenticação
- JWT com expiração
- Refresh tokens
- Proteção CSRF

### 2. Autorização
- Controle de acesso por role
- Validação de permissões

### 3. Criptografia
- Senhas com bcrypt
- Secrets gerenciados via Kubernetes

### 4. Validação
- Pydantic schemas
- Sanitização de entrada

## Performance

### 1. Otimizações de Busca
- Índice HNSW no PgVector (O(log n))
- Caching de embeddings
- Hybrid search com ponderação

### 2. Escalabilidade
- Processamento em batch
- Múltiplas réplicas backend
- Load balancing

### 3. Monitoramento
- Logging estruturado
- Health checks
- Métricas de performance

## Deployment

### 1. Docker
- Multi-stage builds
- Imagens otimizadas
- Docker Compose para desenvolvimento

### 2. Kubernetes
- Deployments com replicação
- Services para descoberta
- ConfigMaps e Secrets
- PersistentVolumes

### 3. Ambientes
- Development (Docker Compose)
- Production (Kubernetes)

## Próximas Melhorias

1. **Memória Persistente**: Histórico de conversas entre sessões
2. **Feedback Loop**: Aprendizado com feedback do usuário
3. **Multi-Idioma**: Suporte a múltiplos idiomas
4. **Fine-tuning**: Modelos customizados por domínio
5. **Monitoring**: Dashboards de performance
6. **Cache Distribuído**: Redis para cache
