# Dernières versions stables (Python, nginx stable), épinglées par version exacte et empreinte
FROM python:3.15.1-slim-trixie@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51 AS build

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python tools/polices.py construire \
    && python tools/polices.py verifier \
    && python tools/polices.py site --sortie /app/_site

FROM nginxinc/nginx-unprivileged:1.30.6-alpine3.24@sha256:f5116ed4606f3eb015dd4a8e28cb9b351476dc0ad4bc6e9f93b19cec130cdf03

# Correctifs de sécurité d'Alpine publiés après l'image de base
USER root
RUN apk upgrade --no-cache
USER nginx

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY --from=build /app/_site /usr/share/nginx/html

EXPOSE 8080
