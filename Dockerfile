FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir \
    "streamlit>=1.35.0" \
    "duckdb>=1.0.0" \
    "plotly>=5.20.0" \
    "pandas>=2.0.0" \
    "openpyxl>=3.1.0" \
    "anthropic>=0.25.0"

EXPOSE 8502

CMD ["streamlit", "run", "app.py", \
     "--server.port=8502", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
