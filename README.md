# API Server

## Quickstart 

### Dependencies

```sh
# Init GelDB project (Formely known as EdgeDB)
$ npx gel project init

# install CLI for Gel
$ curl --proto '=https' --tlsv1.2 -sSf https://www.geldata.com/sh | sh

# run database migrations for schema
$ gel migrate # or npx gel migrate if CLI is not installed
```

### Setup environment

Make a configuration file with Firebase Service Account credentials
```sh
# create app/config.py from app/config.template.py
$ cp app/config.template.py app/config.py
$ nano app/config.py
```

Create a virtual environment and install dependencies
```
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

### Run the server inline

> Ideally, you should use the Makefile in ../confs to deploy the NGINX reverse proxy and the API's Systemd service.

Development server (port 5000 with Flask)
```sh
$ python main.py
```

Production server (port 5050 with Gunicorn) 
```sh
$ gunicorn -c gunicorn.conf.py main:app
```