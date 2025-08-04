.PHONY: dev backend frontend stop prod

# Start local dev with frontend on host, backend in Docker
dev: backend frontend

backend:
	docker compose up --detach

logs:
	docker compose logs -f

frontend:
	cd frontend && pnpm i && pnpm dev

stop:
	docker compose down

# Run full production stack (frontend SSR in Docker)
prod:
	docker compose --profile prod up --build