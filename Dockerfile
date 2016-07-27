# The GoCD bot that posts to an RocketChat webhook
# To build: sudo docker build [--no-cache=true] [--pull=true] --rm=true -t gobot .
# To run e.g: sudo docker run --name=gobot -d gobot -e "WEBHOOK=pahtorocketchatwebhook.com/tokenz" -e "GODOMAIN=domain" -e "GOSTAGES=stage,names"


FROM ubuntu:16.04

MAINTAINER Eugene Venter

# install required packages
RUN apt-get update && apt-get -y install git python python-dev python-pip


RUN useradd -ms /bin/bash iamgobot

USER iamgobot
WORKDIR /home/iamgobot

RUN git clone http://github.com/eugeneventer/rocketgobot.git
RUN git config --global user.name gobot
RUN git config --global user.email gobothasnoemail

USER root
RUN pip install -r rocketgobot/requirements.txt

USER iamgobot
ENTRYPOINT ["/bin/bash", "/home/iamgobot/rocketgobot/start_gobot.sh"]
