# Guia de Configuração - RAG Agent Solution

## Pré-requisitos

### Desenvolvimento Local
- Docker 24+
- Docker Compose 2.20+
- Python 3.11+ (opcional, para desenvolvimento)
- Git

### Produção
- Kubernetes 1.27+
- kubectl 1.27+
- Helm 3.12+ (opcional)
- Ingress Controller (nginx ou similar)

## Obter Chaves de API

### 1. Google Gemini Flash API

1. Acesse [Google AI Studio](https://ai.google.dev)
2. Clique em "Get API Key"
3. Crie um novo projeto ou use um existente
4. Copie a chave API
5. Salve em local seguro

**Free Tier Limits**:
- 15 requisições por minuto
- Sem custo
- Janela de contexto: 1M tokens

### 2. Google Drive (Opcional)

Para backup automático de documentos:

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto
3. Ative a API do Google Drive
4. Crie credenciais (Service Account)
5. Baixe o arquivo JSON
6. Salve em `backend/secrets/google_drive_credentials.json`

## Configuração Local (Docker Compose)

### 1. Clonar Repositório

```bash
git clone https://github.com/seu-usuario/rag-agent-solution.git
cd rag-agent-solution-full
```

### 2. Configurar Variáveis de Ambiente

```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env

# Frontend
cp frontend/.env.example frontend/.env
nano frontend/.env
```

**Editar `backend/.env`**:

```bash
# Obrigatório
GEMINI_API_KEY=sua_chave_api_aqui

# Opcional
GOOGLE_DRIVE_FOLDER_ID=seu_folder_id
GOOGLE_DRIVE_ENABLED=true

# Segurança (mudar em produção)
JWT_SECRET=sua_chave_secreta_aqui
ADMIN_PASSWORD=sua_senha_admin_aqui
```

### 3. Criar Diretório de Secrets

```bash
mkdir -p docker/secrets

# Se usar Google Drive
cp /caminho/para/google_drive_credentials.json docker/secrets/
```

### 4. Iniciar Serviços

```bash
cd docker
docker-compose up -d
```

**Verificar status**:

```bash
docker-compose ps
docker-compose logs -f backend
```

### 5. Acessar Aplicação

- **Chainlit (Chat)**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
  - Usuário: minioadmin
  - Senha: minioadmin

### 6. Criar Bucket MinIO

```bash
# Acessar container MinIO
docker exec rag-minio mc mb minio/rag-documents
```

## Configuração Produção (Kubernetes)

### 1. Preparar Cluster

```bash
# Verificar conexão
kubectl cluster-info

# Criar namespace
kubectl apply -f k8s/namespace.yaml

# Verificar
kubectl get namespace rag-agent
```

### 2. Configurar Secrets

```bash
# Editar arquivo de secrets
nano k8s/backend/secret.yaml
nano k8s/frontend/secret.yaml
nano k8s/postgres/secret.yaml
nano k8s/minio/secret.yaml

# Aplicar secrets
kubectl apply -f k8s/backend/secret.yaml
kubectl apply -f k8s/frontend/secret.yaml
kubectl apply -f k8s/postgres/secret.yaml
kubectl apply -f k8s/minio/secret.yaml
```

### 3. Build e Push de Imagens

```bash
# Build backend
docker build -t seu-registry/rag-backend:latest backend/
docker push seu-registry/rag-backend:latest

# Build frontend
docker build -t seu-registry/rag-frontend:latest frontend/
docker push seu-registry/rag-frontend:latest

# Atualizar deployment com sua registry
sed -i 's|rag-backend:latest|seu-registry/rag-backend:latest|g' k8s/backend/deployment.yaml
sed -i 's|rag-frontend:latest|seu-registry/rag-frontend:latest|g' k8s/frontend/deployment.yaml
```

### 4. Deploy dos Serviços

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

### 5. Verificar Deployment

```bash
# Verificar pods
kubectl get pods -n rag-agent

# Verificar services
kubectl get svc -n rag-agent

# Verificar logs
kubectl logs -n rag-agent deployment/rag-backend
kubectl logs -n rag-agent deployment/rag-frontend

# Port forward para testar
kubectl port-forward -n rag-agent svc/rag-frontend 8501:80
```

### 6. Configurar Ingress (Opcional)

```bash
# Criar ingress
kubectl apply -f k8s/ingress.yaml

# Verificar
kubectl get ingress -n rag-agent
```

## Verificação de Saúde

### Verificar Backend

```bash
# Health check
curl http://localhost:8000/health

# Swagger UI
curl http://localhost:8000/docs
```

### Verificar Frontend

```bash
# Acessar Chainlit
curl http://localhost:8501
```

### Verificar Banco de Dados

```bash
# Conectar ao PostgreSQL
docker exec -it rag-postgres psql -U rag_user -d rag_db

# Verificar tabelas
\dt

# Verificar extensão PgVector
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Verificar MinIO

```bash
# Listar buckets
docker exec rag-minio mc ls minio

# Verificar bucket
docker exec rag-minio mc ls minio/rag-documents
```

## Troubleshooting

### Erro: "Connection refused" ao conectar no PostgreSQL

**Solução**:
```bash
# Verificar se container está rodando
docker ps | grep postgres

# Verificar logs
docker logs rag-postgres

# Reiniciar container
docker restart rag-postgres
```

### Erro: "Gemini API key not found"

**Solução**:
```bash
# Verificar variável de ambiente
docker exec rag-backend env | grep GEMINI

# Atualizar .env
nano backend/.env
docker-compose restart backend
```

### Erro: "MinIO bucket not found"

**Solução**:
```bash
# Criar bucket
docker exec rag-minio mc mb minio/rag-documents

# Verificar
docker exec rag-minio mc ls minio
```

### Erro: "PgVector extension not found"

**Solução**:
```bash
# Conectar ao banco
docker exec -it rag-postgres psql -U rag_user -d rag_db

# Criar extensão
CREATE EXTENSION vector;

# Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## Próximas Etapas

1. Upload de documentos via interface admin
2. Testar chat com perguntas
3. Monitorar logs e performance
4. Configurar backups
5. Implementar CI/CD

## Suporte

Para problemas:

1. Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verifique logs: `docker logs <container_name>`
3. Abra uma issue no repositório
