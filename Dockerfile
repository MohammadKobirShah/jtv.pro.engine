FROM python:3.11-alpine

LABEL maintainer="Kobir Shah"
LABEL description="JTV Pro - #1 Ultimate Smart Cookie & Stream API Engine"

WORKDIR /app

COPY . /app/

RUN chmod +x /app/app.py /app/scripts/start.sh

EXPOSE 8080

CMD ["python3", "/app/app.py"]
