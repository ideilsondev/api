#!/bin/bash

# Carrega senhas dos arquivos de segredos
POSTGRES_PASSWORD=$(cat secrets/postgres_password.txt)
REDIS_PASSWORD=$(cat secrets/redis_password.txt)

# Verifica conexão com o PostgreSQL
echo "Testando conexão com o PostgreSQL..."
docker exec postgres psql -h localhost -U postgres -d icbox_db -c "SELECT 1;" -w <<<"$POSTGRES_PASSWORD"
if [ $? -eq 0 ]; then
  echo "Conexão com PostgreSQL bem-sucedida!"
else
  echo "Falha na conexão com PostgreSQL. Verifique as configurações."
  exit 1
fi

# Verifica conexão com o Redis
echo "Testando conexão com o Redis..."
docker exec redis redis-cli -h localhost -a "$REDIS_PASSWORD" ping
if [ $? -eq 0 ]; then
  echo "Conexão com Redis bem-sucedida!"
else
  echo "Falha na conexão com Redis. Verifique as configurações."
  exit 1
fi