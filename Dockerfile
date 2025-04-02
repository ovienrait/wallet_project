FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir \
    && rm requirements.txt
CMD ["python", "manage.py", "runserver", "0:8000"]