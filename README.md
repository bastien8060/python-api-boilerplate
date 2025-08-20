# API Server

## Quickstart

### Dependencies

```sh
# Init GelDB project (Formely known as EdgeDB)
$ npx gel project init
$ gel migrate
```

### Setup environment

```sh
$ cp .env.example .env
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

### Run the server inline

Development server (port 5000 with Flask)
```sh
$ python main.py
```

Production server (port 5000 with Gunicorn)
```sh
$ gunicorn -c gunicorn.conf.py main:app
```

### Docker

```sh
$ docker-compose up --build
```

Production deployment
```sh
$ docker-compose -f docker-compose.yml up -d
```
