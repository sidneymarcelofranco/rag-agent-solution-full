# Estrutura do Projeto RAG Agent Solution

## Visão Geral

Plataforma RAG completa com orquestração de agentes Agno, interface Chainlit, autenticação e área administrativa.

## Arquitetura de Diretórios

```
rag-agent-solution-full/
├── backend/                          # Backend Python com Agno e RAG
│   ├── app/
│   │   ├── main.py                  # Aplicação FastAPI principal
│   │   ├── config.py                # Configurações e variáveis de ambiente
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py # Processamento de PDF/TXT/LOG
│   │   │   ├── chunking.py          # Estratégias de chunking inteligente
│   │   │   ├── embeddings.py        # Geração de embeddings
│   │   │   ├── vector_store.py      # Integração PgVector
│   │   │   ├── hybrid_search.py     # Busca híbrida + re-ranking
│   │   │   └── sql_connector.py     # Integração com bancos relacionais
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── agent_manager.py     # Orquestração Agno
│   │   │   ├── specialized_agents.py # Agentes especializados
│   │   │   └── llm_config.py        # Configuração Gemini Flash
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── minio_client.py      # Cliente MinIO
│   │   │   ├── gdrive_client.py     # Cliente Google Drive
│   │   │   └── storage_manager.py   # Gerenciador de armazenamento
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # Modelos de autenticação
│   │   │   ├── jwt_handler.py       # Manipulação JWT
│   │   │   └── auth_service.py      # Serviço de autenticação
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # Rotas FastAPI
│   │   │   ├── admin_routes.py      # Rotas administrativas
│   │   │   └── schemas.py           # Schemas Pydantic
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── database.py          # Conexão PostgreSQL
│   │       └── models.py            # Modelos SQLAlchemy
│   ├── requirements.txt             # Dependências Python
│   ├── Dockerfile                   # Dockerfile backend
│   └── .env.example                 # Exemplo de variáveis de ambiente
│
├── frontend/                         # Frontend Chainlit
│   ├── chainlit_app.py              # Aplicação Chainlit principal
│   ├── auth_handler.py              # Manipulação de autenticação
│   ├── admin_interface.py           # Interface administrativa
│   ├── chat_interface.py            # Interface de chat
│   ├── requirements.txt             # Dependências Python
│   ├── Dockerfile                   # Dockerfile frontend
│   ├── .chainlit/
│   │   └── config.toml              # Configuração Chainlit
│   └── .env.example                 # Exemplo de variáveis de ambiente
│
├── docker/
│   ├── docker-compose.yml           # Orquestração local
│   ├── docker-compose.prod.yml      # Orquestração produção
│   ├── minio/
│   │   ├── Dockerfile               # Dockerfile MinIO (opcional)
│   │   └── init-minio.sh            # Script de inicialização
│   └── postgres/
│       ├── init-db.sql              # Script de inicialização PostgreSQL
│       └── pgvector-init.sql        # Inicialização PgVector
│
├── k8s/                             # Manifestos Kubernetes
│   ├── namespace.yaml               # Namespace da aplicação
│   ├── backend/
│   │   ├── deployment.yaml          # Deployment backend
│   │   ├── service.yaml             # Service backend
│   │   ├── configmap.yaml           # ConfigMap
│   │   └── secret.yaml              # Secret (template)
│   ├── frontend/
│   │   ├── deployment.yaml          # Deployment Chainlit
│   │   ├── service.yaml             # Service Chainlit
│   │   └── configmap.yaml           # ConfigMap
│   ├── postgres/
│   │   ├── deployment.yaml          # Deployment PostgreSQL
│   │   ├── service.yaml             # Service PostgreSQL
│   │   ├── pvc.yaml                 # PersistentVolumeClaim
│   │   └── configmap.yaml           # ConfigMap
│   ├── minio/
│   │   ├── deployment.yaml          # Deployment MinIO
│   │   ├── service.yaml             # Service MinIO
│   │   └── pvc.yaml                 # PersistentVolumeClaim
│   └── ingress.yaml                 # Ingress (opcional)
│
├── docs/
│   ├── ARCHITECTURE.md              # Documentação de arquitetura
│   ├── SETUP.md                     # Guia de configuração
│   ├── DEPLOYMENT.md                # Guia de deploy Kubernetes
│   ├── API.md                       # Documentação API
│   ├── RAG_PIPELINE.md              # Documentação pipeline RAG
│   └── TROUBLESHOOTING.md           # Guia de troubleshooting
│
├── .gitignore
├── README.md                        # README principal
└── PROJECT_STRUCTURE.md             # Este arquivo
```

## Stack Tecnológico

| Componente | Tecnologia | Versão | Propósito |
| :--- | :--- | :--- | :--- |
| **Backend** | Python + FastAPI | 3.11+ | API e orquestração |
| **Agentes** | Agno (Phidata) | Latest | Hub de agentes |
| **LLM** | Google Gemini Flash | Free Tier | Inferência |
| **Banco Vetorial** | PostgreSQL + PgVector | 15+ | Armazenamento embeddings |
| **Frontend** | Chainlit | Latest | Interface de chat |
| **Armazenamento** | MinIO + Google Drive | Latest | Persistência de documentos |
| **Container** | Docker | 24+ | Containerização |
| **Orquestração** | Kubernetes | 1.27+ | Produção |

## Variáveis de Ambiente

### Backend
- `DATABASE_URL`: Conexão PostgreSQL
- `GEMINI_API_KEY`: Chave API Gemini Flash
- `MINIO_ENDPOINT`: Endpoint MinIO
- `MINIO_ACCESS_KEY`: Chave de acesso MinIO
- `MINIO_SECRET_KEY`: Chave secreta MinIO
- `GOOGLE_DRIVE_CREDENTIALS`: Credenciais Google Drive (JSON)
- `JWT_SECRET`: Chave secreta JWT
- `ADMIN_USERNAME`: Usuário admin
- `ADMIN_PASSWORD`: Senha admin

### Frontend (Chainlit)
- `BACKEND_URL`: URL do backend
- `CHAINLIT_AUTH_SECRET`: Chave secreta Chainlit
- `CHAINLIT_API_KEY`: Chave API Chainlit

## Próximas Etapas

1. Implementar backend Python com pipeline RAG
2. Configurar Agno com agentes especializados
3. Desenvolver interface Chainlit
4. Criar Dockerfiles
5. Gerar manifestos Kubernetes
6. Documentar e testar
