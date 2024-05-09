FROM python:3.12
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY validators.py /app
COPY api.py /app
COPY wsgi.py /app
COPY test_api.py /app
CMD gunicorn -w 8 --bind 0.0.0.0:5000 wsgi:app -k 'gevent'