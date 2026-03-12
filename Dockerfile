FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the local package
RUN pip install --no-cache-dir -e .

EXPOSE ${PORT:-8000}

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
