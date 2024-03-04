import multiprocessing

from uvicorn.workers import UvicornWorker

worker_class = UvicornWorker
workers = multiprocessing.cpu_count() * 2 + 1
name = "fastapi-battlesnakes"
user = "fastapi-user"
group = "fastapi-group"
bind = "unix:battle-python.sock"
loglevel = "ERROR"
errorlog = "/home/ubuntu/battle-python/error_log.txt"
forwarded_allow_ips = "*"
umask = "007"
