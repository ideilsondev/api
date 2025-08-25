#!/bin/bash

# Carrega senhas dos arquivos de segredos
POSTGRES_PASSWORD=$(cat secrets/postgres_password.txt)
REDIS_PASSWORD=$(cat secrets/redis_password.txt)

# Verifica conexão com o PostgreSQL
echo "Testando conexão com o PostgreSQL..."
docker exec postgres env PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -U postgres -d icbox_db -c "SELECT 1;"
if [ $? -eq 0 ]; then
  echo "Conexão com PostgreSQL bem-sucedida!"
else
  echo "Falha na conexão com PostgreSQL. Verifique as configurações."
  docker logs postgres
  exit 1
fi

# Verifica conexão com o Redis
echo "Testando conexão com o Redis..."
REDIS_PING=$(echo -n "$REDIS_PASSWORD" | docker exec -i redis redis-cli -h localhost AUTH && docker exec redis redis-cli -h localhost ping)
if [ "$REDIS_PING" = "PONG" ]; then
  echo "Conexão com Redis bem-sucedida!"
else
  echo "Falha na conexão com Redis: $REDIS_PING"
  docker logs redis
  exit 1
fi

# Verifica conexão com o n8n
echo "Testando conexão com o n8n..."
N8N_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5678)
if [ "$N8N_STATUS" = "200" ]; then
  echo "Conexão com n8n bem-sucedida!"
else
  echo "Falha na conexão com n8n: HTTP $N8N_STATUS"
  docker logs n8n
  exit 1
fi