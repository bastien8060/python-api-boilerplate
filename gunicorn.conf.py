# gunicorn.conf.py

bind = "0.0.0.0:5000"
workers = 4
threads = 8
timeout = 60
loglevel = "info"
accesslog = "-"
errorlog = "-"
