FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn mcp
CMD ["python", "server.py"]
