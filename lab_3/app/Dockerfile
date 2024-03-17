# basic python image
FROM python:3.7

# install redis to access redis APIs
RUN pip install redis fastapi gunicorn uvicorn

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/

# copy the file
COPY main.py .

# start command
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:80", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "5555"]
