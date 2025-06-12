FROM apache/airflow:2.7.2-python3.11

COPY requirements.txt /requirements.txt

USER airflow

RUN pip install --user --no-cache-dir -r /requirements.txt
