import multiprocessing
import socket

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "wsgi:app"

# The granularity of Error log outputs
loglevel = "debug"

# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1

# The socket to bind
#bind = "unix:/var/run/gunicorn.sock"
bind = '0.0.0.0:3111'

# Write access and error info to /var/log
#accesslog = "/var/log/gunicorn/access.log"
#errorlog = "/var/log/gunicorn/error.log"
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"

# Redirect stdout/stderr to log file
capture_output = True

# PID file so you can easily fetch process ID
pidfile = 'gunicorn.pid'

# Daemonize the Gunicorn process (detach & enter background)
daemon = True

# Timeout
timeout = 200

# User
user = 'root'