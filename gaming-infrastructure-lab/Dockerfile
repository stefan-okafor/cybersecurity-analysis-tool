FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    useradd --create-home --uid 10001 labuser
COPY app.py agent.py ./
COPY static ./static
USER labuser
EXPOSE 8080
CMD ["python", "app.py"]
