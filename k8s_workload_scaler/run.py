import logging
from time import sleep
import argparse
from prometheus_alert_api import PrometheusAlertAPI

__author__ = "Emin AKTAS <eminaktas34@gmail.com>"

WORKLOAD = 'workload'
NAME = 'name'
NAMESCAPE = 'namespace'
SCALING_RANGE = 'scaling_range'
MAX_NUMBER = 'max_number'
MIN_NUMBER = 'min_number'
TIME_INTERVAL = 'delay'
MANAGEMENT_TYPE = 'management_type'
HOST = 'host'
PORT = 'port'
SCALING_OUT_NAME = 'scaling_out_name'
SCALING_IN_NAME = 'scaling_in_name'
SUPPORTED_WORKLOAD = [
    'Deployment',
    'StatefulSet',
    'ReplicaSet',
    'ReplicationController',
]
SUPPORTED_MANAGEMENT_TYPE = [
    'prometheus_alert_api',
]


# parse_args function allows us to set the parameters in commandline
def parse_args():
    parent_parser = argparse.ArgumentParser(add_help=False)
    argument_parser = argparse.ArgumentParser(
        description="This program for scaling the K8s workloads", parents=[parent_parser])
    argument_parser.add_argument('-w', '--worklod', dest=WORKLOAD, required=True, type=str,
                                 help="<Required> Enter a workload name"
                                      f"Supported workloads: {SUPPORTED_WORKLOAD}")
    argument_parser.add_argument('-n', '--name', dest=NAME, required=True, type=str,
                                 help="<Required> Enter a name of the workload")
    argument_parser.add_argument('-ns', '--namespace', dest=NAMESCAPE, required=True, type=str,
                                 help="<Required> Enter a namespace of the workload")
    argument_parser.add_argument('-s', '--scaling-range', dest=SCALING_RANGE, required=False, type=int,
                                 default=1, help="<Optional> Enter a scaling range")
    argument_parser.add_argument('-max', '--max-number', dest=MAX_NUMBER, required=True, type=int,
                                 help="<Required> Enter maximum number of Pods")
    argument_parser.add_argument('-min', '--min-number', dest=MIN_NUMBER, required=True, type=int,
                                 help="<Required> Enter minimum number of Pods")
    argument_parser.add_argument('-ti', '--time-interval', dest=TIME_INTERVAL, required=False, default=60,
                                 type=float, help="<Optional> Enter a time interval for alert "
                                                  "control. Default value is 60 seconds")
    argument_parser.add_argument('-mt', '--management-type', dest=MANAGEMENT_TYPE, required=True, type=str,
                                 help="<Required> Enter a management type. "
                                      f"Supported management types: {SUPPORTED_MANAGEMENT_TYPE}")
    argument_parser.add_argument('-ph', '--prometheus-host', dest=HOST, required=False, type=str,
                                 help="<Optional> Enter a Prometheus host if management type is prometheus_alert_api")
    argument_parser.add_argument('-pp', '--prometheus-port', dest=PORT, required=False, type=str,
                                 help="<Optional> Enter a Prometheus port if management type is prometheus_alert_api")
    argument_parser.add_argument('-son', '--scaling-out-alert-name', dest=SCALING_OUT_NAME, required=False,
                                 type=str,
                                 help="<Optional> Enter an alert name for scaling out"
                                      " if management type is prometheus_alert_api")
    argument_parser.add_argument('-sin', '--scaling-in-alert-name', dest=SCALING_IN_NAME, required=False,
                                 type=str,
                                 help="<Optional> Enter an alert name for scaling in"
                                      " if management type is prometheus_alert_api")

    args = vars(argument_parser.parse_args())
    return args


class Run:
    def __init__(
            self,
            parameters
    ):
        self.management_type = parameters[MANAGEMENT_TYPE]
        self.workload = parameters[WORKLOAD]
        self.name = parameters[NAME]
        self.namespace = parameters[NAMESCAPE]
        self.scaling_range = parameters[SCALING_RANGE]
        self.max_number = parameters[MAX_NUMBER]
        self.min_number = parameters[MIN_NUMBER]
        self.host = parameters[HOST]
        self.port = parameters[PORT]
        self.scaling_out_name = parameters[SCALING_OUT_NAME]
        self.scaling_in_name = parameters[SCALING_IN_NAME]
        self.time_interval = parameters[TIME_INTERVAL]

        # Logging
        self.logger = logging.getLogger('Run')
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def run(self):
        """
        Runs the workload scaler for specific management
        """

        self.logger.info("Workload Scaler is running")

        if self.management_type == 'prometheus_alert_api':

            """
            python3 run.py
            -w Deployment -n php-apache -ns default -s 1 -max 10 -min 2 -ti 60
            -mt prometheus_alert_api -ph localhost -pp 9090
            -son php-apache-scaling-out -sin php-apache-scaling-in
            """

            self.logger.info(f"Scaling workload for {self.name} (namespace: {self.namespace}, "
                             f"workload: {self.workload}) is started. Management type is "
                             f"{self.management_type}. Make sure that always have two alert in Prometheus "
                             f"for scaling out and scaling in. Each scaling alert workload will change "
                             f"the pod {self.scaling_range} number amount of pod. (host: {self.host}, "
                             f"port: {self.port}, scaling_out_name: {self.scaling_out_name}, "
                             f"scaling_in_name: {self.scaling_in_name})")

            manager = PrometheusAlertAPI(
                self.workload,
                self.name,
                self.namespace,
                self.scaling_range,
                self.max_number,
                self.min_number,
                self.host,
                self.port,
                self.scaling_out_name,
                self.scaling_in_name,
            )

            while True:
                manager.control_alert_and_trigger_scaling()
                self.logger.info(f"Waiting {self.time_interval} seconds for the next query if alarm is firing")
                sleep(self.time_interval)
        else:
            self.logger.error(f"Not valid management_type: {self.management_type}")
            raise Exception("Not valid management_type")


if __name__ == '__main__':
    parameter = parse_args()
    run = Run(parameter)
    run.run()
