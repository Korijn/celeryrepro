# How to reproduce

* Run rabbitmq:
  `docker run --rm -d -p 5672:5672 rabbitmq`
* Run the celery worker:
  `poetry run celery -A app:app worker -P solo -c 1`
* Run the client:
  `poetry run python app.py`

Toggle the `LEAK` variable in `app.py` to toggle the `ThreadPoolExecutor` usage to collect results.
