FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt fastapi uvicorn pydantic

EXPOSE 7860

CMD ["python", "inference.py"]