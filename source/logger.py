import logging
from sys import stdout

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logFormatter = logging.Formatter('%(asctime)s.%(msecs)03d %(lineno)3s:%(name)-22s %(levelname)-6s %(message)s')
consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(logFormatter)
LOG.addHandler(consoleHandler)
