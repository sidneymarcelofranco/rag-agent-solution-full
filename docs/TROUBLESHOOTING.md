# Troubleshooting - RAG Agent Solution

## Erros Docker

### Erro 1: "The attribute `version` is obsolete"

**Problema**: Docker Compose avisa que o atributo `version` é obsoleto.

**Solução**: ✅ Já foi corrigido no `docker-compose.yml`. A versão foi removida.

---

### Erro 2: "manifest for pgvector/pgvector:pg15-latest not found"

**Problema**: A imagem `pgvector/pgvector:pg15-latest` não existe.

**Solução**: ✅ Já foi corrigido. Alteramos para `pgvector/pgvector:pg15` (versão estável).

---

### Erro 3: "The GEMINI_API_KEY variable is not set"

**Problema**: Variável de ambiente não configurada.

**Solução**:

1. Abra `backend/.env`
2. Substitua `sua_chave_gemini_aqui` pela sua chave real
3. Obtenha em: https://ai.google.dev

```bash
# Editar backend/.env
GEMINI_API_KEY=sua_chave_real_aqui
```

---

### Erro 4: "unable to get image 'minio/minio:latest'"

**Problema**: Docker não consegue baixar a imagem do MinIO.

**Solução**:

1. Verifique conexão com internet
2. Tente fazer pull manualmente:

```bash
docker pull minio/minio:latest
```

3. Se ainda falhar, use uma versão específica:

```bash
docker pull minio/minio:RELEASE.2024-01-16T16-07-38Z
```

---

## Problemas de Conexão

### Erro: "Connection refused" ao conectar no PostgreSQL

**Problema**: Backend não consegue conectar no PostgreSQL.

**Solução**:

```bash
# Verificar se container está rodando
docker ps | grep rag-postgres

# Verificar logs
docker logs rag-postgres

# Reiniciar container
docker restart rag-postgres

# Aguardar health check passar
docker exec rag-postgres pg_isready -U rag_user -d rag_db
```

---

### Erro: "Connection refused" ao conectar no MinIO

**Problema**: Backend não consegue conectar no MinIO.

**Solução**:

```bash
# Verificar se container está rodando
docker ps | grep rag-minio

# Verificar logs
docker logs rag-minio

# Testar conectividade
docker exec rag-backend curl -f http://minio:9000/minio/health/live

# Reiniciar
docker restart rag-minio
```

---

## Problemas de Construção (Build)

### Erro: "failed to solve with frontend dockerfile.v0"

**Problema**: Erro ao fazer build da imagem Docker.

**Solução**:

```bash
# Limpar cache do Docker
docker system prune -a

# Tentar build novamente
docker-compose build --no-cache

# Se persistir, verificar Dockerfile
cat backend/Dockerfile
```

---

### Erro: "ModuleNotFoundError: No module named 'xxx'"

**Problema**: Dependência Python não instalada.

**Solução**:

```bash
# Verificar requirements.txt
cat backend/requirements.txt

# Reconstruir imagem
docker-compose build --no-cache backend

# Reiniciar
docker-compose restart backend
```

---

## Problemas de Performance

### Container muito lento

**Problema**: Docker está consumindo muitos recursos.

**Solução**:

```bash
# Verificar uso de recursos
docker stats

# Limpar volumes não utilizados
docker volume prune

# Limpar imagens não utilizadas
docker image prune

# Limpar tudo
docker system prune -a
```

---

### Erro: "no space left on device"

**Problema**: Disco cheio.

**Solução**:

```bash
# Verificar espaço
df -h

# Limpar Docker
docker system prune -a

# Remover volumes não utilizados
docker volume prune

# Remover containers parados
docker container prune
```

---

## Problemas de Rede

### Containers não conseguem se comunicar

**Problema**: Backend não consegue acessar PostgreSQL/MinIO.

**Solução**:

```bash
# Verificar rede
docker network ls
docker network inspect rag-network

# Verificar DNS
docker exec rag-backend nslookup postgres
docker exec rag-backend nslookup minio

# Testar ping
docker exec rag-backend ping postgres
docker exec rag-backend ping minio
```

---

### Erro: "Cannot assign requested address"

**Problema**: Porta já está em uso.

**Solução**:

```bash
# Verificar portas em uso
netstat -ano | findstr :8000
netstat -ano | findstr :8501
netstat -ano | findstr :5432

# Matar processo
taskkill /PID <PID> /F

# Ou mudar porta no docker-compose.yml
# Alterar: "8000:8000" para "8001:8000"
```

---

## Problemas de Banco de Dados

### Erro: "FATAL: password authentication failed"

**Problema**: Senha do PostgreSQL incorreta.

**Solução**:

```bash
# Verificar credenciais em docker-compose.yml
cat docker/docker-compose.yml | grep -A 3 "POSTGRES_"

# Resetar banco (CUIDADO: apaga dados!)
docker-compose down -v
docker-compose up -d
```

---

### Erro: "PgVector extension not found"

**Problema**: Extensão PgVector não instalada.

**Solução**:

```bash
# Conectar ao banco
docker exec -it rag-postgres psql -U rag_user -d rag_db

# Criar extensão
CREATE EXTENSION vector;

# Verificar
SELECT * FROM pg_extension WHERE extname = 'vector';

# Sair
\q
```

---

## Problemas de Frontend

### Erro: "Connection refused" ao acessar Chainlit

**Problema**: Frontend não está respondendo.

**Solução**:

```bash
# Verificar se container está rodando
docker ps | grep rag-frontend

# Verificar logs
docker logs rag-frontend

# Verificar porta
netstat -ano | findstr :8501

# Reiniciar
docker restart rag-frontend
```

---

### Erro: "Failed to connect to backend"

**Problema**: Frontend não consegue conectar no backend.

**Solução**:

```bash
# Verificar URL do backend em frontend/.env
cat frontend/.env | grep BACKEND_URL

# Verificar se backend está rodando
docker ps | grep rag-backend

# Testar conectividade
docker exec rag-frontend curl http://backend:8000/health

# Verificar logs do backend
docker logs rag-backend
```

---

## Problemas de Armazenamento

### Erro: "Bucket not found"

**Problema**: Bucket do MinIO não existe.

**Solução**:

```bash
# Criar bucket
docker exec rag-minio mc mb minio/rag-documents

# Verificar
docker exec rag-minio mc ls minio
```

---

### Erro: "Access Denied" ao acessar MinIO

**Problema**: Credenciais incorretas.

**Solução**:

```bash
# Verificar credenciais em docker-compose.yml
cat docker/docker-compose.yml | grep -A 2 "MINIO_"

# Acessar console MinIO
# URL: http://localhost:9001
# Usuário: minioadmin
# Senha: minioadmin
```

---

## Comandos Úteis

### Visualizar Logs

```bash
# Todos os containers
docker-compose logs -f

# Container específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f minio

# Últimas 100 linhas
docker-compose logs --tail=100 backend
```

### Executar Comandos

```bash
# Dentro do backend
docker exec -it rag-backend bash

# Dentro do PostgreSQL
docker exec -it rag-postgres psql -U rag_user -d rag_db

# Dentro do MinIO
docker exec -it rag-minio sh
```

### Reiniciar Tudo

```bash
# Parar tudo
docker-compose down

# Remover volumes (CUIDADO: apaga dados!)
docker-compose down -v

# Iniciar novamente
docker-compose up -d
```

---

## Checklist de Diagnóstico

- [ ] Docker Desktop está rodando?
- [ ] Variáveis de ambiente estão configuradas? (`backend/.env`, `frontend/.env`)
- [ ] Portas 8000, 8501, 5432, 9000, 9001 estão livres?
- [ ] Internet está funcionando?
- [ ] Espaço em disco disponível?
- [ ] Todos os containers estão rodando? (`docker ps`)
- [ ] Health checks estão passando? (`docker ps`)
- [ ] Logs não mostram erros? (`docker-compose logs`)

---

## Suporte

Se o problema persistir:

1. Colete os logs: `docker-compose logs > logs.txt`
2. Verifique a documentação: `docs/SETUP.md`
3. Abra uma issue no repositório

**Repositório**: https://github.com/sidneymarcelofranco/rag-agent-solution-full
