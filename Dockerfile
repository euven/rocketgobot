# The GoCD bot that posts to an RocketChat webhook
# To build: sudo docker build [--no-cache=true] [--pull=true] --rm=true -t gobot .
# To run e.g: sudo docker run --name=gobot -e "WEBHOOK=pahtorocketchatwebhook.com/tokenz" -e "GODOMAIN=domain" -e "GOSTAGES=stage,names" --restart=unless-stopped -d gobot

FROM ubuntu:16.04

MAINTAINER Eugene Venter

# install required packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get -y install python python-dev python-pip && \
    apt-get clean && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash iamgobot

ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt
ADD rocketgobot.py start_rocketgobot.sh /rocketgobot/

USER iamgobot
WORKDIR /rocketgobot
CMD ["/bin/sh", "/rocketgobot/start_rocketgobot.sh"]
