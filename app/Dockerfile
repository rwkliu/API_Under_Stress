FROM python:3.12
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY api.py /app
COPY wsgi.py /app
COPY test_api.py /app
CMD hypercorn -b 0.0.0.0:5000 -w 8 wsgi:app