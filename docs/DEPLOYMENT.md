# Guia de Deployment em Kubernetes

## Pré-requisitos

- Cluster Kubernetes 1.27+
- kubectl configurado
- Docker Registry (DockerHub, ECR, GCR, etc.)
- Helm 3.12+ (opcional)

## Arquitetura de Deployment

```
┌─────────────────────────────────────────────────┐
│           Ingress Controller (nginx)            │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
    ┌────────────┐           ┌──────────────┐
    │ Frontend   │           │   Backend    │
    │ (Chainlit) │           │  (FastAPI)   │
    │ x2 replicas│           │  x2 replicas │
    └────────────┘           └──────────────┘
        │                           │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
    ┌──────────────┐         ┌─────────────┐
    │ PostgreSQL   │         │   MinIO     │
    │ + PgVector   │         │  + Backup   │
    │ (1 replica)  │         │ (1 replica) │
    └──────────────┘         └─────────────┘
```

## Passo 1: Preparar Imagens Docker

### Build das Imagens

```bash
# Backend
docker build -t seu-registry/rag-backend:v1.0.0 backend/
docker push seu-registry/rag-backend:v1.0.0

# Frontend
docker build -t seu-registry/rag-frontend:v1.0.0 frontend/
docker push seu-registry/rag-frontend:v1.0.0
```

### Atualizar Deployments

```bash
# Editar deployment backend
sed -i 's|rag-backend:latest|seu-registry/rag-backend:v1.0.0|g' k8s/backend/deployment.yaml

# Editar deployment frontend
sed -i 's|rag-frontend:latest|seu-registry/rag-frontend:v1.0.0|g' k8s/frontend/deployment.yaml
```

## Passo 2: Criar Namespace e Secrets

### Criar Namespace

```bash
kubectl apply -f k8s/namespace.yaml

# Verificar
kubectl get namespace rag-agent
```

### Criar Secrets

```bash
# Backend Secret
kubectl apply -f k8s/backend/secret.yaml

# Frontend Secret
kubectl apply -f k8s/frontend/secret.yaml

# PostgreSQL Secret
kubectl create secret generic rag-postgres-secret \
  --from-literal=POSTGRES_USER=rag_user \
  --from-literal=POSTGRES_PASSWORD=seu_password_seguro \
  -n rag-agent

# MinIO Secret
kubectl create secret generic rag-minio-secret \
  --from-literal=MINIO_ROOT_USER=minioadmin \
  --from-literal=MINIO_ROOT_PASSWORD=seu_password_seguro \
  -n rag-agent

# Verificar
kubectl get secrets -n rag-agent
```

## Passo 3: Deploy dos Serviços

### PostgreSQL

```bash
# Criar PVC
kubectl apply -f k8s/postgres/pvc.yaml

# Criar ConfigMap
kubectl apply -f k8s/postgres/configmap.yaml

# Deploy
kubectl apply -f k8s/postgres/deployment.yaml
kubectl apply -f k8s/postgres/service.yaml

# Verificar
kubectl get pods -n rag-agent -l app=rag-postgres
kubectl logs -n rag-agent deployment/rag-postgres
```

### MinIO

```bash
# Criar PVC
kubectl apply -f k8s/minio/pvc.yaml

# Deploy
kubectl apply -f k8s/minio/deployment.yaml
kubectl apply -f k8s/minio/service.yaml

# Verificar
kubectl get pods -n rag-agent -l app=rag-minio
```

### Backend

```bash
# ConfigMap
kubectl apply -f k8s/backend/configmap.yaml

# Deploy
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml

# Verificar
kubectl get pods -n rag-agent -l app=rag-backend
kubectl logs -n rag-agent deployment/rag-backend -f
```

### Frontend

```bash
# ConfigMap
kubectl apply -f k8s/frontend/configmap.yaml

# Deploy
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml

# Verificar
kubectl get pods -n rag-agent -l app=rag-frontend
kubectl logs -n rag-agent deployment/rag-frontend -f
```

## Passo 4: Configurar Ingress

### Criar Ingress

```bash
# Editar ingress.yaml com seu domínio
nano k8s/ingress.yaml

# Aplicar
kubectl apply -f k8s/ingress.yaml

# Verificar
kubectl get ingress -n rag-agent
```

### Exemplo de Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rag-ingress
  namespace: rag-agent
spec:
  ingressClassName: nginx
  rules:
  - host: rag.seu-dominio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rag-frontend
            port:
              number: 80
  - host: api.rag.seu-dominio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rag-backend
            port:
              number: 8000
```

## Passo 5: Verificação de Saúde

### Verificar Pods

```bash
# Todos os pods
kubectl get pods -n rag-agent

# Detalhes de um pod
kubectl describe pod -n rag-agent <pod-name>

# Logs
kubectl logs -n rag-agent <pod-name>
```

### Verificar Services

```bash
# Listar services
kubectl get svc -n rag-agent

# Detalhes
kubectl describe svc -n rag-agent rag-backend
```

### Health Checks

```bash
# Port forward para testar
kubectl port-forward -n rag-agent svc/rag-backend 8000:8000

# Em outro terminal
curl http://localhost:8000/health

# Frontend
kubectl port-forward -n rag-agent svc/rag-frontend 8501:80
curl http://localhost:8501
```

## Passo 6: Configuração de Produção

### Resource Limits

Os deployments já incluem:
- **Requests**: CPU 500m, Memory 512Mi (backend)
- **Limits**: CPU 1000m, Memory 1Gi (backend)

Ajustar conforme necessário:

```bash
kubectl set resources deployment rag-backend \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=2000m,memory=2Gi \
  -n rag-agent
```

### Auto-scaling

```bash
# Criar HPA
kubectl autoscale deployment rag-backend \
  --min=2 --max=5 \
  --cpu-percent=80 \
  -n rag-agent

# Verificar
kubectl get hpa -n rag-agent
```

### Persistência de Dados

Verificar PVCs:

```bash
kubectl get pvc -n rag-agent

# Detalhes
kubectl describe pvc -n rag-agent rag-postgres-pvc
```

## Passo 7: Monitoramento

### Logs

```bash
# Logs em tempo real
kubectl logs -n rag-agent deployment/rag-backend -f

# Logs de todos os pods
kubectl logs -n rag-agent -l app=rag-backend --all-containers=true -f
```

### Métricas

```bash
# Uso de recursos
kubectl top nodes
kubectl top pods -n rag-agent

# Detalhes
kubectl describe node <node-name>
```

### Eventos

```bash
# Eventos do namespace
kubectl get events -n rag-agent --sort-by='.lastTimestamp'

# Monitorar em tempo real
kubectl get events -n rag-agent -w
```

## Troubleshooting

### Pod não inicia

```bash
# Verificar status
kubectl describe pod -n rag-agent <pod-name>

# Verificar logs
kubectl logs -n rag-agent <pod-name>

# Verificar eventos
kubectl get events -n rag-agent
```

### Erro de conexão com banco

```bash
# Verificar service do PostgreSQL
kubectl get svc -n rag-agent rag-postgres

# Testar conectividade
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h rag-postgres -U rag_user -d rag_db -c "SELECT 1"
```

### Erro de memória

```bash
# Aumentar limits
kubectl set resources deployment rag-backend \
  --limits=memory=2Gi \
  -n rag-agent

# Verificar uso
kubectl top pods -n rag-agent
```

## Backup e Restore

### Backup do PostgreSQL

```bash
# Fazer dump
kubectl exec -n rag-agent rag-postgres-<pod-id> -- \
  pg_dump -U rag_user rag_db > backup.sql

# Restaurar
kubectl exec -i -n rag-agent rag-postgres-<pod-id> -- \
  psql -U rag_user rag_db < backup.sql
```

### Backup do MinIO

```bash
# Sincronizar para local
kubectl exec -n rag-agent rag-minio-<pod-id> -- \
  mc mirror minio/rag-documents /backup/
```

## Scaling

### Aumentar Réplicas

```bash
# Backend
kubectl scale deployment rag-backend --replicas=3 -n rag-agent

# Frontend
kubectl scale deployment rag-frontend --replicas=3 -n rag-agent

# Verificar
kubectl get deployment -n rag-agent
```

## Rollout e Rollback

### Atualizar Imagem

```bash
# Atualizar backend
kubectl set image deployment/rag-backend \
  backend=seu-registry/rag-backend:v1.0.1 \
  -n rag-agent

# Verificar rollout
kubectl rollout status deployment/rag-backend -n rag-agent
```

### Rollback

```bash
# Ver histórico
kubectl rollout history deployment/rag-backend -n rag-agent

# Fazer rollback
kubectl rollout undo deployment/rag-backend -n rag-agent

# Rollback para versão específica
kubectl rollout undo deployment/rag-backend --to-revision=2 -n rag-agent
```

## Limpeza

```bash
# Deletar todos os recursos
kubectl delete namespace rag-agent

# Deletar PVs (se necessário)
kubectl delete pv <pv-name>
```

## Próximas Etapas

1. Configurar CI/CD (GitHub Actions, GitLab CI)
2. Implementar monitoring (Prometheus, Grafana)
3. Configurar logging centralizado (ELK, Loki)
4. Implementar backup automático
5. Configurar disaster recovery
