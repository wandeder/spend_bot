lint: #linter for code
	poetry run flake8 spend_bot
start: #start bot
	poetry run python3 -m spend_bot.bot
requirements: # update requirements.txt
	poetry export --output requirements.txt --without-hashes
