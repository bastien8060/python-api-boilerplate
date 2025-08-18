# gunicorn.conf.py

bind = "127.0.0.1:5050"       # We’re binding to port 5050 as requested
workers = 4                 # Adjust based on cores; 2-4 is common for dev
threads = 8                # Optional, increases concurrency per worker
timeout = 60                # Optional, increases default timeout
loglevel = "info"           # Or "debug" if you want more noise
accesslog = "-"             # Sends access logs to stdout
errorlog = "-"              # Sends error logs to stderr