import sys
import json
import time
import logging
import argparse
import websocket
import requests
import signal


class GoBotRocket(object):

    def __init__(self, webhookurl, godomain, stages):
        self.failedpipes = []
        self.webhookurl = webhookurl
        self.godomain = godomain
        self.stages = stages
        self.stop = False

        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://{domain}:8887/".format(domain=self.godomain),
                                         on_message=self.gocd_message,
                                         on_error=self.gocd_error,
                                         on_close=self.gocd_close)

        # if we later wanna do more stuff, start a thread in somefunc?
        # self.ws.on_open = somefunc

    def __del__(self):
        self.ws.close()

    def terminate(self, signum, frame):
        self.stop = True
        if self.ws:
            try:
                self.ws.close()
            except:
                pass

    def run(self):
        sleepsecs = 60
        while not self.stop:
            try:
                logging.info('Start websocket listener')
                self.ws.run_forever()
            except:
                logging.error("Unexpected error: {}".format(sys.exc_info()[0]))
                logging.error("Trying websocket reconnect in {} seconds".format(sleepsecs))
                time.sleep(sleepsecs)

    def gocd_message(self, ws, message):
        msg = json.loads(message)
        pipename = msg['pipeline']['name']
        stage = msg['pipeline']['stage']
        if stage['name'] in self.stages:
            golink = 'https://{domain}/go/tab/pipeline/history/{pipe}'.format(domain=self.godomain, pipe=pipename)
            if stage['state'] == 'Passed' and pipename in self.failedpipes:
                self.failedpipes.remove(pipename)
                self.send_message_fixed(pipename, golink, stage['name'])
            elif stage['state'] == 'Failed' and pipename not in self.failedpipes:
                self.failedpipes.append(pipename)
                self.send_message_failed(pipename, golink, stage['name'])

    def gocd_error(self, ws, error):
        logging.error("GOCD ERROR!!!")
        logging.error(error)

    def gocd_close(self, ws):
        logging.info("### gocd ws closed ###")

    def send_message_fixed(self, pipe, link, stage):
        self.rocket_message("[{pipe}]({link}) ({stage}) *fixed* :grinning:"
                            .format(pipe=pipe, link=link, stage=stage))

    def send_message_failed(self, pipe, link, stage):
        self.rocket_message("[{pipe}]({link}) ({stage}) *broken* :scream:"
                            .format(pipe=pipe, link=link, stage=stage))

    def rocket_message(self, message):
        msgdata = {
            "username": "gobot",
            "text": message
        }
        requests.post(self.webhookurl, data=json.dumps(msgdata))


if __name__ == '__main__':
    # Setup the command line arguments.
    argp = argparse.ArgumentParser(description="GoCD bot for RocketChat")

    argp.add_argument('-q', '--quiet', help='set logging to ERROR',
                      action='store_const', dest='loglevel',
                      const=logging.ERROR, default=logging.INFO)
    argp.add_argument("-w", "--webhook", dest="webhookurl",
                      help="The RocketChat webhook URL, including token")
    argp.add_argument("-g", "--godomain", dest="godomain",
                      help="GoCD domain to connect to")
    argp.add_argument("-s", "--stages", dest="stages",
                      help="Comma-separated list of stage names to report on")

    args = argp.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel, format='%(levelname)-8s %(message)s')

    rocketbot = GoBotRocket(
        args.webhookurl,
        args.godomain,
        args.stages.split(',')
    )
    rocketbot.run()
