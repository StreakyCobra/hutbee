FROM python:3.9

RUN echo '[global]\nextra-index-url=https://www.piwheels.org/simple\n' >> /etc/pip.conf

COPY controller/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY controller /app
WORKDIR /app

CMD python -u -m hutbee_controller
