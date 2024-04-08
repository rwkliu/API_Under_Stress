FROM python:3.12
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY api.py /app
CMD python api.py