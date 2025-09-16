SHELL := /bin/bash


.PHONY: up down reset logs ps sh init runner-logs runner-status


up:
	@docker compose up -d db gitea
	@./scripts/init.sh


down:
	@docker compose down


reset:
	@docker compose down -v || true
	@rm -f .env.bak .env.bak2 || true
	@echo "Stack stopped and volumes deleted."


logs:
	@docker compose logs -f --tail=200


ps:
	@docker compose ps


sh:
	@S=$${S:-gitea}; echo "Shell into: $$S"; docker exec -it $$S sh


init:
	@./scripts/init.sh


runner-logs:
	@docker compose logs -f runner


runner-status:
	@echo "==> Actions Runner Status:"
	@docker compose ps runner
	@echo ""
	@echo "==> Runner logs (last 20 lines):"
	@docker compose logs --tail=20 runner
