from app.tasks.celery_app import celery

@celery.task
def background_task(example_data: str):
    # Exemplo: processamento assíncrono
    return f"Processed: {example_data}"