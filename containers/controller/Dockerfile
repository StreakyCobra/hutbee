FROM python:3.7

COPY controller/temperature.py temperature.py

RUN pip install smbus flask

CMD python -u temperature.py
