web: cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4
worker: cd backend && python -m workers.task_worker
