import multiprocessing

import uvicorn

bind = "127.0.0.1:8000"
worker_class = uvicorn.workers.UvicornWorker
workers = multiprocessing.cpu_count() * 2 + 1
name = "fastapi-battlesnakes"
user = "fastapi-user"
group = "fastapi-group"
bind = "unix:/home/ubuntu/battle-python/run/battle-python.sock"
loglevel = "ERROR"
errorlog = "/home/ubuntu/battle-python/error_log.txt"
