"""
"""
import logging.config
import signal

from bridge_factory import BridgeFactory
from configuration import Configuration
from ipx800V4.IPX800Engine import IPX800Engine


def signal_handler(_signal, _frame):
    logger.info("stopping ipx")
    ipx.stop()
    logger.info("stopping homekit")
    driver.stop()
# end

# main
logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger(__name__)
#
config = Configuration()
ipx = IPX800Engine()

bf = BridgeFactory(config)
(driver, accessories) = bf.create_driver()

ipx.register_accessory(accessories)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

logger.info("starting ipx")
ipxSettings = config.get_ipx800

ipx.start(host=ipxSettings.get('host'),
          port=ipxSettings.get('port'),
          apiKey=ipxSettings.get('apikey'),
          interval=ipxSettings.get('interval', IPX800Engine.DEFAULT_INTERVAL))

logger.info("starting homekit")
driver.start()
logger.info("terminated")
