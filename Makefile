lint: #linter for code
	poetry run flake8 spend_bot tests
start: #start bot
	poetry run python3 -m spend_bot.bot
