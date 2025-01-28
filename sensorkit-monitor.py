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
        type=bool,
        default=False
    )
    args = parser.parse_args()
    data = load_config(args.config_file)
    config = Config(data)
    dictConfig(config.logging)

    scheduler.start()
    do_debug = True if logger.root.level == logging.DEBUG else False
    app = Starlette(debug=do_debug)

    kit = SensorKit(board.I2C(), data['sensorkit'], scheduler)
    kit.run()

    app.state.tree = kit.tree
    try:
        encoding = config.metrics_encoding
        labels = config.metrics_labels
        endpoint = config.metrics_endpoint

        exporter = metrics.metrics_factory.get_exporter(encoding, labels)
        app.add_route(endpoint, exporter.export)
    except AttributeError as e:
        logger.info('disabling metrics exporting - %s', e)

    if args.test is True:
        import littletable as db
        from sensorkit import datastructures as ds
        ds.links.present()
        ds.nodes.present()
        ds.multiplexer_attributes.present()
        ds.channel_attributes.present()
        ds.device_attributes.present()
        ds.meter_attributes.present()
        for ns in ds.nodes.where(kind=5):
            meter = ns.obj
            msg = 'Meter {} on device id {} (using channel {}) has address {} : {} {}'.format(
                    meter.name, meter.device_id, meter.channel_id, hex(meter.address),
                    meter.measure, meter.units)
            print(msg)

        devs = ds.join_devices()
        devs.present()
        nodes = ds.join_devices_meters()
        nodes.where(name='BMP390', measurement=8).present()
        virtuals = ds.join_virtuals()
        virtuals.present()

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
