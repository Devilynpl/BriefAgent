FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt* ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit httpx pydantic dnspython jinja2 python-dotenv && \
    pip install --no-cache-dir -e .

COPY src/ ./src/
COPY BriefAgent_logo.jpg ./

EXPOSE 8503

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8503/_stcore/health || exit 1

CMD ["streamlit", "run", "src/briefagent/ui/app.py", "--server.port=8503", "--server.address=0.0.0.0", "--server.headless=true"]
