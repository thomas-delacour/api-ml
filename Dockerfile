FROM ubuntu:latest

RUN apt update && apt install python3-pip -y

ADD requirements.txt .
ADD api_models.py .
COPY train /train
COPY ml_models /ml_models

RUN pip install -r requirements.txt

EXPOSE 8000

CMD python3 api_models.py