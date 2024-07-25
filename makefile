include .env
RUN_PYTHON=PYTHONPATH=./ poetry run

build:
	docker compose --file ./docker-compose.dev.yaml build web

dev: format lint build
	docker compose --file ./docker-compose.dev.yaml up --remove-orphans -d

dev-local: format lint migrate
	docker compose --file ./docker-compose.dev.yaml up postgres -d --remove-orphans
	BOT_MAIN=False ${RUN_PYTHON} celery -A config worker -l INFO -E -P gevent -c 500 &
	export WORKER_PID=$$!;
	BOT_MAIN=False ${RUN_PYTHON} celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
	export BEAT_PID=$$!;

	BOT_MAIN=True ${RUN_PYTHON} gunicorn -k uvicorn.workers.UvicornWorker config.asgi:app --bind 0.0.0.0:8000
	kill ${WORKER_PID}
	kill ${BEAT_PID}


lint:
	${RUN_PYTHON} ruff check --fix ./config ./regbot

format:
	${RUN_PYTHON} ruff format ./config ./regbot

set-webhook:
	${RUN_PYTHON} python ./manage.py setwebhook

delete-webhook:
	${RUN_PYTHON} python ./manage.py deletewebhook

start-ngrok:
	ngrok http 8080

makemigrations:
	$(RUN_PYTHON) poetry run python ./manage.py makemigrations

migrate: makemigrations
	${RUN_PYTHON} python ./manage.py migrate

createsuperuser:
	poetry run python ./manage.py createsuperuser

showmigrations:
	$(RUN_PYTHON) poetry run python ./manage.py showmigrations