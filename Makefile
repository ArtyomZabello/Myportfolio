.PHONY: env up down wait-for-backend test-api test-load test-security run-all run-all-py

env:
	@if [ ! -f .env ]; then cp .env.example .env; fi

up:
	docker compose -f app/docker-compose.yml up -d --build

down:
	docker compose -f app/docker-compose.yml down -v

wait-for-backend:
	python scripts/wait_for_backend.py

run-all-py:
	python scripts/run_all.py

test-api:
	pytest tests/api/ -v --alluredir=allure-results

test-load:
	locust -f performance/locustfile.py --headless -u 50 -r 10 --run-time 1m --host $$(python -c "from config.settings import Config; print(Config().BASE_URL.rstrip('/'))")

test-security:
	docker run --rm -v $$(pwd)/security:/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t $$(python -c "from config.settings import Config; print(Config().BASE_URL)") -c zap_baseline.conf -r zap_report.html || true

run-all: env up wait-for-backend test-api down
