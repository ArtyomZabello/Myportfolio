.PHONY: env up down wait-for-backend test-api test-load run-all

env:
	@if [ ! -f .env ]; then cp .env.example .env; fi

up:
	docker-compose -f app/docker-compose.yml up -d

down:
	docker-compose -f app/docker-compose.yml down -v

wait-for-backend:
	@echo "Waiting for Conduit backend to become healthy..."
	@health_url=$$(python -c "from config.settings import Config; print(Config().BASE_URL.rstrip('/') + '/tags')"); \
	timeout=30; \
	elapsed=0; \
	while [ $$elapsed -lt $$timeout ]; do \
		if curl -sf "$$health_url" > /dev/null 2>&1; then \
			echo "Backend is ready at $$health_url"; \
			exit 0; \
		fi; \
		sleep 1; \
		elapsed=$$((elapsed + 1)); \
	done; \
	echo "Backend did not become healthy within $$timeout seconds."; \
	exit 1

test-api:
	pytest tests/api/ -v --alluredir=allure-results

test-load:
	locust -f performance/locustfile.py --headless -u 50 -r 10 --run-time 1m --host $$(python -c "from config.settings import Config; print(Config().BASE_URL.rstrip('/'))")

run-all: env up wait-for-backend test-api down
