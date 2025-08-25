# Makefile para gerenciar containers PostgreSQL, Redis e n8n

# Variáveis
COMPOSE := docker compose
PSQL_CONTAINER := postgres
REDIS_CONTAINER := redis
N8N_CONTAINER := n8n
TEST_SCRIPT := test_connection.sh

# Alvo padrão
.PHONY: install
install: secrets update-secrets up restart status test

# Criar diretório e arquivos de segredos
.PHONY: secrets
secrets:
	@echo "Criando diretório de segredos..."
	@mkdir -p secrets
	@echo "supersecret_postgres_2025!" > secrets/postgres_password.txt
	@echo "supersecret_redis_2025!" > secrets/redis_password.txt
	@chmod 600 secrets/*.txt

# Atualizar senhas nos arquivos de segredos
.PHONY: update-secrets
update-secrets:
	@echo "Atualizando senhas dos arquivos de segredos..."
	@mkdir -p secrets
	@read -s -p "Digite a nova senha para o PostgreSQL (Enter para gerar automaticamente): " pgpass; echo; \
	 if [ -z "$$pgpass" ]; then \
	   pgpass=$$(openssl rand -base64 12); \
	   echo "Senha gerada automaticamente para PostgreSQL."; \
	 fi; \
	 echo "$$pgpass" > secrets/postgres_password.txt; \
	 chmod 600 secrets/postgres_password.txt; \
	 echo "Senha do PostgreSQL salva em secrets/postgres_password.txt"
	@read -s -p "Digite a nova senha para o Redis (Enter para gerar automaticamente): " redispass; echo; \
	 if [ -z "$$redispass" ]; then \
	   redispass=$$(openssl rand -base64 12); \
	   echo "Senha gerada automaticamente para Redis."; \
	 fi; \
	 echo "$$redispass" > secrets/redis_password.txt; \
	 chmod 600 secrets/redis_password.txt; \
	 echo "Senha do Redis salva em secrets/redis_password.txt"
	@echo "Reiniciando containers para aplicar novas senhas..."
	$(COMPOSE) restart
	@echo "Senhas atualizadas e containers reiniciados. Execute 'make test' para verificar."

# Subir os containers
.PHONY: up
up:
	@echo "Subindo containers PostgreSQL, Redis e n8n..."
	$(COMPOSE) up -d

# Parar os containers
.PHONY: down
down:
	@echo "Parando containers PostgreSQL, Redis e n8n..."
	$(COMPOSE) down

# Reiniciar todos os containers
.PHONY: restart
restart: down up
	@echo "Todos os containers reiniciados."

# Reiniciar container PostgreSQL
.PHONY: restart-postgres
restart-postgres:
	@echo "Reiniciando container PostgreSQL..."
	$(COMPOSE) restart postgres
	@echo "Container PostgreSQL reiniciado."

# Reiniciar container Redis
.PHONY: restart-redis
restart-redis:
	@echo "Reiniciando container Redis..."
	$(COMPOSE) restart redis
	@echo "Container Redis reiniciado."

# Reiniciar container n8n
.PHONY: restart-n8n
restart-n8n:
	@echo "Reiniciando container n8n..."
	$(COMPOSE) restart n8n
	@echo "Container n8n reiniciado."

# Atualizar imagem do n8n
.PHONY: update-n8n
update-n8n:
	@echo "Atualizando imagem do n8n..."
	$(COMPOSE) pull n8n
	$(COMPOSE) up -d n8n
	@echo "Imagem do n8n atualizada."

# Atualizar imagem do Redis
.PHONY: update-redis
update-redis:
	@echo "Atualizando imagem do Redis..."
	$(COMPOSE) pull redis
	$(COMPOSE) up -d redis
	@echo "Imagem do Redis atualizada."

# Verificar logs
.PHONY: logs
logs:
	@echo "Exibindo logs dos containers..."
	$(COMPOSE) logs --tail=100

# Verificar status dos containers
.PHONY: status
status:
	@echo "Verificando status dos containers..."
	docker ps -f name=$(PSQL_CONTAINER) -f name=$(REDIS_CONTAINER) -f name=$(N8N_CONTAINER)

# Testar conexão com os serviços
.PHONY: test
test:
	@echo "Testando conexões com PostgreSQL, Redis e n8n..."
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
	@echo "  make install                         - Instalar containers"
	@echo "  make secrets                         - Criar arquivos de segredos"
	@echo "  make update-secrets                  - Atualizar senhas nos arquivos de segredos"
	@echo "  make up                              - Subir containers PostgreSQL, Redis e n8n"
	@echo "  make down                            - Parar containers"
	@echo "  make restart                         - Reiniciar todos os containers"
	@echo "  make restart-postgres                - Reiniciar container PostgreSQL"
	@echo "  make restart-redis                   - Reiniciar container Redis"
	@echo "  make restart-n8n                     - Reiniciar container n8n"
	@echo "  make update-n8n                      - Atualizar imagem do n8n"
	@echo "  make update-redis                    - Atualizar imagem do Redis"
	@echo "  make logs                            - Exibir logs dos containers"
	@echo "  make status                          - Verificar status dos containers"
	@echo "  make test                            - Testar conexão com PostgreSQL, Redis e n8n"
	@echo "  make clean                           - Remover containers, volumes, imagens e segredos"
	@echo "  make help                            - Exibir esta ajuda"
	               