# Makefile para gerenciar containers PostgreSQL e Redis

# Variáveis
COMPOSE := docker-compose
PSQL_CONTAINER := postgres
REDIS_CONTAINER := redis
TEST_SCRIPT := test_connection.sh

# Alvo padrão
.PHONY: all
all: secrets up

# Criar diretório e arquivos de segredos
.PHONY: secrets
secrets:
	@echo "Criando diretório de segredos..."
	@mkdir -p secrets
	@echo "supersecret_postgres_2025!" > secrets/postgres_password.txt
	@echo "supersecret_redis_2025!" > secrets/redis_password.txt
	@chmod 600 secrets/*.txt

# Subir os containers
.PHONY: up
up:
	@echo "Subindo containers PostgreSQL e Redis..."
	$(COMPOSE) up -d

# Parar os containers
.PHONY: down
down:
	@echo "Parando containers PostgreSQL e Redis..."
	$(COMPOSE) down

# Reiniciar os containers
.PHONY: restart
restart: down up
	@echo "Containers reiniciados."

# Verificar logs
.PHONY: logs
logs:
	@echo "Exibindo logs dos containers..."
	$(COMPOSE) logs --tail=100

# Verificar status dos containers
.PHONY: status
status:
	@echo "Verificando status dos containers..."
	docker ps -f name=$(PSQL_CONTAINER) -f name=$(REDIS_CONTAINER)

# Testar conexão com os serviços
.PHONY: test
test:
	@echo "Testando conexões com PostgreSQL e Redis..."
	chmod +x $(TEST_SCRIPT)
	./$(TEST_SCRIPT)

# Limpar recursos (containers, volumes, redes)
.PHONY: clean
clean:
	@echo "Limpando containers, volumes e redes..."
	$(COMPOSE) down -v --rmi local
	@rm -rf secrets
	@echo "Recursos limpos."

# Ajuda com os comandos disponíveis
.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  make secrets  - Criar arquivos de segredos"
	@echo "  make up      - Subir containers PostgreSQL e Redis"
	@echo "  make down    - Parar containers"
	@echo "  make restart - Reiniciar containers"
	@echo "  make logs    - Exibir logs dos containers"
	@echo "  make status  - Verificar status dos containers"
	@echo "  make test    - Testar conexão com PostgreSQL e Redis"
	@echo "  make clean   - Remover containers, volumes, imagens e segredos"
	@echo "  make help    - Exibir esta ajuda"