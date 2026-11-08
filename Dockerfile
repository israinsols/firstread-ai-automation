FROM python:3.12-slim AS build

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SITE_BASE_PATH=

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python main.py --build

FROM nginx:alpine

ENV NGINX_ENVSUBST_FILTER=^PORT$
COPY --from=build /app/public /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
RUN rm -f /etc/nginx/conf.d/default.conf

EXPOSE 8080
