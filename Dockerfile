FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git

ENTRYPOINT ["python", "main.py"]
