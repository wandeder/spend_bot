lint: # linter for code
	poetry run flake8 spend_bot
start: # start bot
	poetry run python3 -m spend_bot.bot
requirements: # update requirements.txt
	poetry export --output requirements.txt --without-hashes
up: # build and start Docker container
	docker compose -f docker-compose.yml up --build -d
logs: # container logs
	docker logs -f spend_bot
enter: # enter into container
	docker exec -it spend_bot /bin/bash
stop: # stop spend_bot
	docker compose stop spend_bot
