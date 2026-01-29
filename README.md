# Plataforma RAG Agent Solution

Uma solução completa de **Retrieval-Augmented Generation (RAG)** com orquestração de agentes inteligentes, interface de chat moderna e suporte para múltiplas fontes de dados.

## 🎯 Visão Geral

Esta plataforma integra as melhores tecnologias de IA e engenharia de software para criar um sistema robusto de resposta a perguntas contextualizadas:

- **Agno (Phidata)**: Hub de agentes para orquestração inteligente
- **Google Gemini Flash**: LLM de baixo custo via API gratuita
- **PostgreSQL + PgVector**: Armazenamento vetorial nativo
- **Chainlit**: Interface de chat moderna com streaming
- **MinIO + Google Drive**: Armazenamento persistente de documentos
- **Kubernetes**: Orquestração em produção

## 🚀 Funcionalidades Principais

### 1. Pipeline RAG Completo
- Processamento de **PDFs, TXT, LOG e consultas SQL**
- Chunking inteligente com sobreposição configurável
- Armazenamento em **PgVector** para busca semântica rápida
- Suporte a **Hybrid Search** (semântica + palavra-chave)
- Re-ranking automático para reduzir alucinações

### 2. Hub de Agentes Agno
- Múltiplos agentes especializados
- Orquestração inteligente de tarefas
- Memória persistente entre sessões
- Integração com ferramentas externas

### 3. Interface de Chat Chainlit
- Chat em tempo real com streaming de respostas
- Exibição de fontes consultadas
- Autenticação com login/senha
- Histórico de conversas persistente

### 4. Área Administrativa
- Upload de PDFs e arquivos de texto
- Gestão de documentos
- Monitoramento de embeddings
- Controle de acesso por usuário

### 5. Armazenamento Flexível
- **MinIO**: Armazenamento local de objetos
- **Google Drive**: Backup e sincronização automática
- Suporte a múltiplos formatos de arquivo

## 📋 Pré-requisitos

### Desenvolvimento Local
- Docker 24+
- Docker Compose 2.20+
- Python 3.11+
- Chave API do Google Gemini Flash (gratuita)

### Produção (Kubernetes)
- Cluster Kubernetes 1.27+
- kubectl 1.27+
- Helm 3.12+ (opcional)
- Ingress Controller (nginx ou similar)

## 🔧 Configuração Rápida (Docker Compose)

### 1. Clonar e Preparar

```bash
cd rag-agent-solution-full
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Configurar Variáveis de Ambiente

Edite `backend/.env`:

```bash
# Obtenha em: https://ai.google.dev/
GEMINI_API_KEY=your_gemini_api_key_here

# Google Drive (opcional)
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_DRIVE_CREDENTIALS_PATH=/app/secrets/google_drive_credentials.json

# Segurança
JWT_SECRET=your_jwt_secret_key_change_this_in_production
ADMIN_PASSWORD=change_this_password
```

### 3. Iniciar Serviços

```bash
cd docker
docker-compose up -d
```

### 4. Acessar Aplicação

- **Chainlit (Chat)**: http://localhost:8501
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)
- **Backend API**: http://localhost:8000/docs (Swagger)

## 🐳 Estrutura Docker

```
rag-agent-solution-full/
├── backend/
│   └── Dockerfile          # Multi-stage Python 3.11
├── frontend/
│   └── Dockerfile          # Multi-stage Chainlit
└── docker/
    ├── docker-compose.yml  # Orquestração local
    └── postgres/
        └── init-db.sql     # Inicialização PostgreSQL
```

## ☸️ Deploy em Kubernetes

### 1. Preparar Secrets

```bash
# Criar namespace
kubectl apply -f k8s/namespace.yaml

# Criar secrets (edite com seus valores)
kubectl apply -f k8s/backend/secret.yaml
kubectl apply -f k8s/frontend/secret.yaml
kubectl apply -f k8s/postgres/secret.yaml
kubectl apply -f k8s/minio/secret.yaml
```

### 2. Deploy dos Serviços

```bash
# PostgreSQL
kubectl apply -f k8s/postgres/

# MinIO
kubectl apply -f k8s/minio/

# Backend
kubectl apply -f k8s/backend/

# Frontend
kubectl apply -f k8s/frontend/
```

### 3. Verificar Status

```bash
kubectl get pods -n rag-agent
kubectl get svc -n rag-agent
kubectl logs -n rag-agent deployment/rag-backend
```

## 📚 Documentação

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura detalhada do sistema
- **[SETUP.md](docs/SETUP.md)** - Guia de configuração completo
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Guia de deploy em Kubernetes
- **[API.md](docs/API.md)** - Documentação da API REST
- **[RAG_PIPELINE.md](docs/RAG_PIPELINE.md)** - Detalhes do pipeline RAG
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Guia de troubleshooting

## 🔐 Segurança

- Autenticação JWT com expiração configurável
- Senhas com hash bcrypt
- CORS configurável
- Secrets gerenciados via Kubernetes Secrets
- Credenciais Google Drive criptografadas

## 📊 Performance

### Otimizações Implementadas

- **Busca Vetorial**: Índice HNSW no PgVector para O(log n)
- **Hybrid Search**: Combinação de semântica + palavra-chave
- **Re-ranking**: Cross-encoder para ordenação inteligente
- **Caching**: Embeddings cacheados no banco
- **Chunking**: Sobreposição inteligente para contexto

### Limites Recomendados

| Métrica | Limite | Observação |
| :--- | :--- | :--- |
| Tamanho máximo de arquivo | 100 MB | Processamento local |
| Documentos por usuário | 1000 | Sem limite técnico |
| Mensagens por sessão | 10000 | Histórico persistente |
| Réplicas backend | 2-4 | Escalabilidade automática |

## 🛠️ Desenvolvimento

### Estrutura de Diretórios

```
backend/
├── app/
│   ├── main.py              # Aplicação FastAPI
│   ├── config.py            # Configurações
│   ├── rag/                 # Pipeline RAG
│   ├── agents/              # Hub de agentes Agno
│   ├── storage/             # Integração MinIO/GDrive
│   ├── auth/                # Autenticação JWT
│   └── api/                 # Rotas FastAPI
├── requirements.txt
└── Dockerfile

frontend/
├── chainlit_app.py          # Aplicação Chainlit
├── auth_handler.py          # Manipulação de auth
├── admin_interface.py       # Interface admin
├── chat_interface.py        # Interface de chat
├── requirements.txt
└── Dockerfile
```

### Executar Testes

```bash
cd backend
pytest tests/ -v --cov=app
```

### Lint e Formatação

```bash
cd backend
black app/
flake8 app/
mypy app/
```

## 📝 Variáveis de Ambiente

### Backend

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `DATABASE_URL` | Conexão PostgreSQL | postgresql://... |
| `GEMINI_API_KEY` | Chave API Gemini | (obrigatório) |
| `MINIO_ENDPOINT` | Endpoint MinIO | minio:9000 |
| `JWT_SECRET` | Chave secreta JWT | (obrigatório) |
| `CHUNK_SIZE` | Tamanho dos chunks | 1024 |
| `TOP_K_RESULTS` | Resultados retornados | 5 |

### Frontend

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `BACKEND_URL` | URL do backend | http://localhost:8000 |
| `CHAINLIT_AUTH_SECRET` | Chave secreta Chainlit | (obrigatório) |

## 🐛 Troubleshooting

### Erro de Conexão PostgreSQL

```bash
# Verificar logs
docker logs rag-postgres

# Reconectar
docker exec rag-backend python -c "from app.db.database import get_db; await get_db()"
```

### MinIO não conecta

```bash
# Verificar saúde
curl http://localhost:9000/minio/health/live

# Criar bucket
docker exec rag-minio mc mb minio/rag-documents
```

### Embeddings não são gerados

```bash
# Verificar logs do backend
docker logs rag-backend | grep embedding

# Testar modelo
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2')"
```

## 📞 Suporte

Para problemas, dúvidas ou sugestões:

1. Consulte [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Verifique os logs: `docker logs <container_name>`
3. Abra uma issue no repositório

## 📄 Licença

MIT License - Veja LICENSE para detalhes

## 🙏 Agradecimentos

- [Agno (Phidata)](https://github.com/agno-agi/agno) - Framework de agentes
- [Chainlit](https://chainlit.io) - Interface de chat
- [pgvector](https://github.com/pgvector/pgvector) - Busca vetorial PostgreSQL
- [Google Gemini](https://ai.google.dev) - LLM
- [MinIO](https://min.io) - Armazenamento de objetos

---

**Desenvolvido com ❤️ para a comunidade de IA**
