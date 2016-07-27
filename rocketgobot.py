import sys
import json
import time
import logging
from optparse import OptionParser
import websocket
import requests

class GoBotRocket(object):
    def __init__(self, webhookurl, godomain, stages):
        self.failedpipes = []
        self.webhookurl = webhookurl
        self.godomain = godomain
        self.stages = stages

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("ws://%s:8887/" % self.godomain,
                                            on_message=self.gocd_message,
                                            on_error=self.gocd_error,
                                            on_close=self.gocd_close)

        # if we later wanna do more stuff, start a thread in somefunc?
        # self.ws.on_open = somefunc
    def __del__(self):
        self.ws.close()


    def run(self):
        sleepsecs = 60
        while 1:
            try:
                logging.info('start websocket listener')
                self.ws.run_forever()
                logging.error("Trying websocket reconnect in %s secs",
                        sleepsecs)
                time.sleep(sleepsecs)
            except:
                logging.error("Unexpected error: %s", sys.exc_info()[0])
                logging.error("Trying websocket reconnect in %s seconds",
                        sleepsecs)
                time.sleep(sleepsecs)


    def gocd_message(self, ws, message):
        msg = json.loads(message)
        pipename = msg['pipeline']['name']
        stage = msg['pipeline']['stage']
        if stage['name'] in self.stages:
            golink = 'https://%s/go/tab/pipeline/history/%s' % (self.godomain, pipename)
            if stage['state'] == 'Passed' and pipename in self.failedpipes:
                self.failedpipes.remove(pipename)
                self.rocket_message("[%s](%s) (%s) fixed :grinning:" %
                        (pipename, golink, stage['name']))
            elif stage['state'] == 'Failed' and pipename not in self.failedpipes:
                self.failedpipes.append(pipename)
                self.rocket_message("[%s](%s) (%s) broken :scream:" %
                        (pipename, golink, stage['name']))


    def gocd_error(self, ws, error):
        logging.error("GOCD ERROR!!!")
        logging.error(error)


    def gocd_close(self, ws):
        logging.info("### gocd ws closed ###")

    def rocket_message(self, message):
        msgdata = {
            "username": "gobot",
            "text": message
        }

        requests.post(self.webhookurl, data=json.dumps(msgdata))

if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option("-w", "--webook", dest="webhookurl",
                    help="The rocketchat web hook url, incl token")
    optp.add_option("-g", "--godomain", dest="godomain",
                    help="GoCD domain to connect to")
    optp.add_option("-s", "--stages", dest="stages",
                    help="comma-seperated list of stage names to report on")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')


    rocketbot = GoBotRocket(
        opts.webhookurl,
        opts.godomain,
        opts.stages.split(',')
    )
    rocketbot.run()

