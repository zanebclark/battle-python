#!/bin/bash
sudo apt update -y
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update -y
sudo apt install -y python3.12
sudo apt install -y python3-pip nginx

touch /etc/nginx/sites-enabled/fastapi_nginx.conf
echo "server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}" >> /etc/nginx/sites-enabled/fastapi_nginx.conf

sudo service nginx restart
