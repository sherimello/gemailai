FROM python:3.11.2

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# CMD uvicorn app.main:app --reload --port=8000 --host=0.0.0.0
CMD uvicorn main:app --host 0.0.0.0 --port 10000
