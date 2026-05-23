FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e ".[dev]"
EXPOSE 18080
CMD ["llm-router", "serve", "--config", "/app/configs/router.local.yaml"]
