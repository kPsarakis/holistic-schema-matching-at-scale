import logging
from os import environ

from celery import Celery
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['CELERY_BROKER_URL'] = 'amqp://{user}:{pwd}@{host}:{port}/'.format(user=environ['RABBITMQ_DEFAULT_USER'],
                                                                              pwd=environ['RABBITMQ_DEFAULT_PASS'],
                                                                              host=environ['RABBITMQ_HOST'],
                                                                              port=environ['RABBITMQ_PORT'])

app.config['CELERY_RESULT_BACKEND_URL'] = 'redis://:{password}@{host}:{port}/0'.format(host=environ['REDIS_HOST'],
                                                                                       port=environ['REDIS_PORT'],
                                                                                       password=environ['REDIS_PASSWORD'])

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND_URL'])

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
