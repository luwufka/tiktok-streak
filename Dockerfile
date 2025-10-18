FROM python:3.10-alpine as builder

# setup
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip && pip install -U --no-cache-dir -r requirements.txt

# run __main__.py
CMD ["python", "."]