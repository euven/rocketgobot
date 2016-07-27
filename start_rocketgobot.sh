#!/bin/bash

# first, ensure git repo is up to date
cd /home/iamgobot/rocketgobot && git pull
python rocketgobot.py -w $WEBHOOK -g $GODOMAIN -s $GOSTAGES
