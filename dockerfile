FROM jupyter/base-notebook
RUN pip install Flask==0.12 requests line-bot-sdk SQLAlchemy pymysql flask-script flask_sqlalchemy
