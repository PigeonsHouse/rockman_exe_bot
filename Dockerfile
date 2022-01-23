FROM python:3.9

RUN mkdir -p /opt/rockman
COPY . /opt/rockman
WORKDIR /opt/rockman

RUN pip install pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]
