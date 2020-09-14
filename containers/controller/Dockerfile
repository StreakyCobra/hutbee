FROM python:3.7

COPY controller /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD python -u sensing.py
