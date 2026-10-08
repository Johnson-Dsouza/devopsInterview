FROM python:3.12-slim
WORKDIR /srv
COPY app/requirements.txt .
RUN pip install --no-cache-dir flask==3.0.3
COPY app ./app
EXPOSE 5000
CMD ["python", "-m", "app.main"]
