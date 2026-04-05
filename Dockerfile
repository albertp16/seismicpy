FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apecseismicpy/ ./apecseismicpy/
COPY templates/ ./templates/
COPY app.py setup.py ./

RUN pip install --no-cache-dir .

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
