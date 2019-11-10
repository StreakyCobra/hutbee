FROM python:3.7

# Update the distribution and install dependencies from the official repos
RUN apt-get update && apt-get install -y nginx supervisor \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/locale/* && rm -rf /usr/share/man/* && rm -rf /usr/share/doc/*

# Install dependencies from pip
RUN pip install uwsgi

# Configure nginx
COPY containers/backend/nginx.conf /etc/nginx/sites-enabled/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# Configure supervisor
COPY containers/backend/supervisord.conf /etc/supervisor/conf.d/

# Configure uwsgi
RUN mkdir /etc/uwsgi/
COPY containers/backend/uwsgi.ini /etc/uwsgi/uwsgi.ini

# Prepare the app at build time
COPY backend /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Fix permissions
RUN chown www-data:www-data -R /app

# Declare container parameters
WORKDIR /app

# Define command to run
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
