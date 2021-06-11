
FROM python:3.8

RUN apt-get update -y 

COPY ./requirements.txt /requirements.txt

ENV PYTHONUNBUFFERED=0
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt

COPY . /
WORKDIR /

CMD ["python3","-u","main.py"]
#ENTRYPOINT [ "python3" ]
#CMD [ "main.py" ]