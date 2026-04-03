FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/kimiroo/apac-visualizer"

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

VOLUME ["/data"]

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]