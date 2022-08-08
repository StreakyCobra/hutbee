FROM python:3.9

RUN echo '[global]\nextra-index-url=https://www.piwheels.org/simple\n' >> /etc/pip.conf

COPY controller /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD python -u controller.py
