FROM ubuntu:latest

RUN apt update -y 
RUN apt upgrade -y 
RUN apt install python3 python3-pip python3-dev -y 

WORKDIR /buffet-manager/dashboard

COPY . .

RUN pip3 install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0.:8000", "app:app"]