FROM python:3.8.3-slim-buster
RUN apt-get update -y && apt-get install -y python-pip python-dev
COPY ./requirements.txt /index/requirements.txt
WORKDIR /index
RUN pip install -r requirements.txt
COPY . /index
ENTRYPOINT [ "python" ]
CMD [ "index.py" ]
