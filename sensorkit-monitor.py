from apscheduler.schedulers.background import BackgroundScheduler
import argparse
import logging
from logging.config import dictConfig
import sys

import board
from starlette.applications import Starlette
import uvicorn

from api import metrics
from config import Config, load_config
from sensorkit import SensorKit

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def main():
    parser = argparse.ArgumentParser(description='monitor.py: I2C sensor monitor')
    parser.add_argument(
        '--config-file',
        help='Global configuration file',
        default='${HOME}/.config/sensorkit-monitor/config.yaml'
    )
    parser.add_argument(
        '--test',
        help='Temp argument for development',
        default=False
    )
    args = parser.parse_args()
    data = load_config(args.config_file)
    config = Config(data)
    dictConfig(config.logging)

    scheduler.start()
    do_debug = True if logger.root.level == logging.DEBUG else False
    app = Starlette(debug=do_debug)

    try:
        encoding = config.metrics_encoding
        labels = config.metrics_labels
        endpoint = config.metrics_endpoint

        exporter = metrics.metrics_factory.get_exporter(encoding, labels)
        app.add_route(endpoint, exporter.export)
    except AttributeError as e:
        logger.info('disabling metrics exporting - %s', e)

    kit = SensorKit(board.I2C(), data['sensorkit'], scheduler, app.state)
    kit.run()

    host = config.host
    port = config.port
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)

    if args.test is False:
        server.run()

    kit.stop()
    scheduler.shutdown()

if __name__ == '__main__':
    main()
