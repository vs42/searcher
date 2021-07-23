FROM python:3.8-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD . /searcher
WORKDIR /searcher

RUN chmod +x /searcher/run.py
ENV SERVER_PORT 5000
EXPOSE 5000
ENTRYPOINT ["python3", "/searcher/run.py"]