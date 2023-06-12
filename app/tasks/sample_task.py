from config import celery_app



@celery_app.task()
def sample_task():
    print("Running Sample Task")