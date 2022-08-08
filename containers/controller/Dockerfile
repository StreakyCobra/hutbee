FROM python:3.9

COPY controller /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD python -u controller.py
