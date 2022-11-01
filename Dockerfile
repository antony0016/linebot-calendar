FROM python:3.7-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /line-calendar
COPY requirements.txt /line-calendar/
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . /line-calendar/
EXPOSE 5001