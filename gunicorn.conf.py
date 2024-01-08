# gunicorn.conf.py
worker_class = "gevent"
workers = 4
bind = "0.0.0.0:3000"
