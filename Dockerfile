FROM python:3.9.5-slim-buster

RUN mkdir /permapol

WORKDIR /permapol

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY permapol.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP permapol.py
EXPOSE 80

ENTRYPOINT ["/permapol/boot.sh"]
