import logging
import urllib2
import re
import time


_default_url = 'http://169.254.169.254/latest/meta-data/spot/termination-time'

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Client:
    def __init__(self, url=_default_url, logger=_logger):
        self.url = url
        self.logger = logger
        self.when_is_shutdown = None

        self.logger.debug('Initialized SpotD client with URL %s' % url)

    def is_shutting_down(self):
        date = self.fetch_shutdown_time()

        if date is None:
            return False

        if self.is_valid_datetime(date):
            self.when_is_shutdown = date
            return True

        return False

    def fetch_shutdown_time(self):
        self.logger.debug('Calling spot API for shutdown status')

        request = urllib2.Request(self.url)
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self.logger.debug('Got HTTPError: %s' % str(e))
            return None
        except urllib2.URLError as e:
            self.logger.debug('Got URLError: %s' % str(e))
            return None

        return response.read()

    def is_valid_datetime(self, date):
        regex = re.compile('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z.*')
        return regex.match(date) is not None


class UI:
    def __init__(self, client, sleep=time.sleep, exit=exit, logger=_logger):
        self.client = client
        self.sleep = sleep
        self.exit = exit
        self.logger = logger

    def loop_forever(self):
        while not self.client.is_shutting_down():
            self.delay()

        self.terminate()

    def delay(self):
        self.sleep(5)

    def terminate(self):
        self.logger.warn("Received notice to shut-down at %s" %
                         self.client.when_is_shutdown)
        self.exit(1)


def main():
    UI(Client()).loop_forever()

if __name__ == "__main__":
    main()
