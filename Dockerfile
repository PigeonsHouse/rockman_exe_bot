FROM python:3.9-alpine

RUN apk --update add tzdata gcc

RUN mkdir -p /opt/rockman
COPY . /opt/rockman
WORKDIR /opt/rockman

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]
