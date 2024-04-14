FROM python:3.12
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
# RUN pip install mysql-connector-python
# RUN pip install pytest
COPY api.py /app
COPY test_api.py /app
CMD python api.py