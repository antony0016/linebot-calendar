FROM python:3.7-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /line-calendar
COPY requirements.txt /line-calendar/
RUN apk update && apk add gcc libc-dev g++ libffi-dev libxml2 unixodbc-dev mariadb-dev postgresql-dev
RUN pip install -r requirements.txt
COPY . /line-calendar/
EXPOSE 5001