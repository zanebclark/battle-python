import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
name = "fastapi-battlesnakes"
bind = "unix:/run/gunicorn.sock"
loglevel = "ERROR"
errorlog = "/home/ubuntu/battle-python/error_log.txt"
forwarded_allow_ips = "*"
