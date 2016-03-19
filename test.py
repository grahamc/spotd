from spotd import Client, UI
import httpretty
from unittest import TestCase
import urllib2


class TestSpotDClient(TestCase):
    def setUp(self):
        httpretty.enable()
        httpretty.HTTPretty.allow_net_connect = False

    def tearDown(self):
        httpretty.disable()

    def set_resp(self, **kwargs):
        httpretty.register_uri(
            httpretty.GET,
            'http://169.254.169.254/latest/meta-data/spot/termination-time',
            **kwargs
        )

    def testReturnedDateShouldShutDown(self):
        self.set_resp(status=200, body='2015-01-05T18:02:00Z')

        c = Client()
        self.assertEquals(c.is_shutting_down(), True)

    def testReturnedDateShouldSetWhen(self):
        self.set_resp(status=200, body='2015-01-05T18:02:00Z')

        c = Client()
        c.is_shutting_down()
        self.assertEquals(c.when_is_shutdown, '2015-01-05T18:02:00Z')

    def testReturned404ShouldNotShutDown(self):
        self.set_resp(status=404)

        c = Client()
        self.assertEquals(c.is_shutting_down(), False)

    def testSocketTimeoutShouldNotShutDown(self):
        def urlopen_error(x, y, z):
            raise urllib2.URLError("urlopen error")
        self.set_resp(body=urlopen_error)

        c = Client()
        self.assertEquals(c.is_shutting_down(), False)

    def testReturnedGarbageDataShouldNotShutDown(self):
        self.set_resp(
            status=200,
            body='<html><head><title>This is an error page!'
        )

        c = Client()
        self.assertEquals(c.is_shutting_down(), False)

    def testReturnedGarbageDataShouldNotSetWhen(self):
        self.set_resp(
            status=200,
            body='<html><head><title>This is an error page!'
        )

        c = Client()
        c.is_shutting_down()
        self.assertEquals(c.when_is_shutdown, None)

    def testIsValidDateTimeNoTimezone(self):
        c = Client()
        self.assertEqual(
            c.is_valid_datetime('2015-01-05T18:02:00Z'),
            True
        )

    def testIsValidDateTimeGarbage(self):
        c = Client()
        self.assertEqual(
            c.is_valid_datetime('Wargleblarg'),
            False
        )


class StubClient:
    def __init__(self, loops):
        self.desired_loops = loops
        self.when_is_shutdown = None
        self.iteration = 0

    def is_shutting_down(self):
        self.iteration += 1
        if self.iteration == self.desired_loops:
            self.when_is_shutdown = self.iteration
            return True
        return False


class StubSleep:
    def __init__(self):
        self.called_for = None

    def __call__(self, length):
        self.called_for = length


class StubExit:
    def __init__(self):
        self.code = None

    def __call__(self, code):
        self.code = code


class StubShutdownLogger:
    def __init__(self):
        self.warn_text = None

    def warn(self, text):
        self.warn_text = text


class TestUI(TestCase):
    def testLoopsUntilClientIsShuttingDown(self):
        iterations = 5
        client = StubClient(iterations)

        ui = UI(client, sleep=StubSleep(), exit=StubExit())
        ui.loop_forever()

        self.assertEquals(iterations, client.iteration)

    def testDelaysBetweenEachLoop(self):
        desired_delay = 5  # seconds

        client = StubClient(2)
        sleep = StubSleep()

        ui = UI(client, sleep=sleep, exit=StubExit())
        ui.loop_forever()

        self.assertEquals(sleep.called_for, desired_delay)

    def testExitsWhenShuttingDown(self):
        client = StubClient(1)

        exit = StubExit()
        ui = UI(client, exit=exit)
        ui.loop_forever()

        self.assertEquals(exit.code, 1)

    def testOutputsShutdownTimeAtShutdown(self):
        client = StubClient(1)
        logger = StubShutdownLogger()

        exit = StubExit()
        ui = UI(client, exit=exit, logger=logger)
        ui.loop_forever()

        self.assertEquals(
            logger.warn_text,
            'Received notice to shut-down at 1'
        )
