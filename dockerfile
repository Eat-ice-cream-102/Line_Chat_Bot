FROM python:3.6

WORKDIR ~/LineChatBot

RUN pip install --upgrade pip; pip install Flask==0.12 requests line-bot-sdk SQLAlchemy

CMD ["python","manage.py", "runserver"]
