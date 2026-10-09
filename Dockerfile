FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY scripts/ ./scripts/
EXPOSE 8080
CMD ["python", "src/main.py"]
