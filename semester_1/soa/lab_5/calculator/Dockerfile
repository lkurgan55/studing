FROM python:alpine3.16
WORKDIR /server
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
COPY src src
ENTRYPOINT [ "python", "src/main.py" ]