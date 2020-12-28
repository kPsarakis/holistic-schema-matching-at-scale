from engine import app, celery
from engine.server.endpoints.atlas_endpoints import atlas_endpoints
from engine.server.endpoints.batch_endpoints import batch_endpoints
from engine.server.endpoints.database_endpoints import database_endpoints
from engine.server.endpoints.minio_endpoints import minio_endpoints


celery.conf.update(app.config)
celery.conf.update(task_serializer='msgpack',
                   accept_content=['msgpack'],
                   result_serializer='msgpack',
                   task_acks_late=True,
                   worker_prefetch_multiplier=1
                   )

app.register_blueprint(batch_endpoints)
app.register_blueprint(minio_endpoints)
app.register_blueprint(atlas_endpoints)
app.register_blueprint(database_endpoints)
