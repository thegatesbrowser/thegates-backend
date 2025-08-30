#!/bin/bash
# install: https://github.com/infinityofspace/certbot_dns_porkbun

certbot certonly \
    --non-interactive \
    --agree-tos \
    --email nordup.ondr@gmail.com \
    --preferred-challenges dns \
    --authenticator dns-porkbun \
    --dns-porkbun-credentials /opt/certbot/porkbun.ini \
    --dns-porkbun-propagation-seconds 60 \
    -d "thegates.io" \
    -d "*.thegates.io"
