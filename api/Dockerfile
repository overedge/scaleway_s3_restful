FROM ubuntu:latest
MAINTAINER Nasser "nahmed-m@student.42.fr"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN PYTHONPATH=/usr/lib/python3.5
RUN export $PYTHONPATH
COPY . /api
WORKDIR /api
RUN pip3 install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["api.py"]
