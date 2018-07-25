FROM python:2.7-slim
WORKDIR /app
ADD . /app
EXPOSE 9999
CMD ["python", "server.py"]
