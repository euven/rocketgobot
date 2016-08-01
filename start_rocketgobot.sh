#!/bin/sh
exec python /rocketgobot/rocketgobot.py -w "${WEBHOOK}" -g "${GODOMAIN}" -s "${GOSTAGES}"
