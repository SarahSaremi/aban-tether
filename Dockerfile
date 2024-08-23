FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install ipython

COPY . .

ENV PYTHONUNBUFFERED 1
ENTRYPOINT ["/app/run.sh"]
