# How to deploy?

## Install dependencies

```bash
# NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
nvm install --lts

# snapd
sudo apt update
sudo apt install snapd nginx

# certbot
sudo snap install --classic certbot
```

## Setup project directory
 Setup UI and API directories, npm i, npx vite build, python3 -m venv env, pip install -r requirements.txt, etc.

## Setup SSL
```bash
sudo certbot --nginx
```

## Deploy configurations

```bash
sudo make update # sudo make help for more options
```

or alternatively manually move the nginx configuration files to /etc/nginx/sites-available, symlink the files to /etc/nginx/sites-enabled, sudo nginx -t, sudo nginx -s reload

> After deploying Nginx configuration through make, make sure you run certbot to redeploy SSL configurations (without generating new certificates) as the SSL configs will be overwritten.