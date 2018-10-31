FROM python:3

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY .  .

CMD ["python3", "watch_door.py"]