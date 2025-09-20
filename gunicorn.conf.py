bind = "0.0.0.0:8000"
workers = int(__import__('os').environ.get('GUNICORN_WORKERS', '3'))
timeout = 30
worker_class = 'gthread'
threads = 4
accesslog = '-'
errorlog = '-'