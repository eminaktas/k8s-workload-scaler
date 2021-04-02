import logging
import argparse
from time import sleep
from k8s_workload_scaler.prometheus_alert_api import PrometheusAlertAPI
from k8s_workload_scaler.prometheus_metric_api import PrometheusMetricAPI

__author__ = "Emin AKTAS <eminaktas34@gmail.com>"

# BASE INFORMATION
WORKLOAD = 'workload'
NAME = 'name'
NAMESCAPE = 'namespace'
SCALING_RANGE = 'scaling_range'
MAX_NUMBER = 'max_number'
MIN_NUMBER = 'min_number'
TIME_INTERVAL = 'delay'
MANAGEMENT_TYPE = 'management_type'

# PROMETHEUS HOST INFORMATION
HOST = 'host'
PORT = 'port'

# PROMETHEUS ALERT INFORMATION
SCALING_OUT_NAME = 'scaling_out_name'
SCALING_IN_NAME = 'scaling_in_name'

# PROMETHEUS METRIC INFORMATION
METRIC_NAME = 'metric_name'
LABEL_LIST = 'label_list'
SCALING_OUT_THRESHOLD_VALUE = 'scaling_out_threshold_value'
SCALING_IN_THRESHOLD_VALUE = 'scaling_in_threshold_value'
RATE_VALUE = 'rate_value'

SUPPORTED_WORKLOAD = [
    'Deployment',
    'StatefulSet',
    'ReplicaSet',
    'ReplicationController',
]
SUPPORTED_MANAGEMENT_TYPE = [
    'prometheus_alert_api',
    'prometheus_metric_api',
]


def parse_args():
    # BASE PARSER
    argument_parser = argparse.ArgumentParser(description="This program is a controller for scaling the K8s workloads")
    argument_parser.add_argument('-w', '--workload', dest=WORKLOAD, required=True, type=str,
                                 help=f"Enter workload name. Supported workloads: {SUPPORTED_WORKLOAD}")
    argument_parser.add_argument('-n', '--name', dest=NAME, required=True, type=str,
                                 help="Enter name of the workload")
    argument_parser.add_argument('-ns', '--namespace', dest=NAMESCAPE, required=True, type=str,
                                 help="Enter namespace of the workload")
    argument_parser.add_argument('-s', '--scaling-range', dest=SCALING_RANGE, required=False, type=int,
                                 default=1, help="Enter scaling range. Adds or removes an amount of Pods")
    argument_parser.add_argument('-max', '--max-number', dest=MAX_NUMBER, required=True, type=int,
                                 help="Enter maximum number of Pods")
    argument_parser.add_argument('-min', '--min-number', dest=MIN_NUMBER, required=True, type=int,
                                 help="Enter minimum number of Pods")
    argument_parser.add_argument('-ti', '--time-interval', dest=TIME_INTERVAL, required=False, default=60,
                                 type=float, help="Enter a time for alert control interval. "
                                                  "Default value is 60 seconds")

    # SUB PARSER
    sub_argument_parsers = argument_parser.add_subparsers(
        help=f"Enter a management type. Supported management types: {SUPPORTED_MANAGEMENT_TYPE}",
        dest=MANAGEMENT_TYPE)

    # PROMETHEUS ALERT PARSER
    prometheus_alert_api_parser = sub_argument_parsers.add_parser('prometheus_alert_api')
    prometheus_alert_api_parser.add_argument('-ph', '--prometheus-host', dest=HOST, required=True, type=str,
                                             help="Enter Prometheus host.")
    prometheus_alert_api_parser.add_argument('-pp', '--prometheus-port', dest=PORT, required=True, type=str,
                                             help="Enter Prometheus port.")
    prometheus_alert_api_parser.add_argument('-son', '--scaling-out-alert-name', dest=SCALING_OUT_NAME, required=True,
                                             type=str, help="Enter alert name for scaling out")
    prometheus_alert_api_parser.add_argument('-sin', '--scaling-in-alert-name', dest=SCALING_IN_NAME, required=True,
                                             type=str, help="Enter alert name for scaling in")

    # PROMETHEUS METRIC PARSER
    prometheus_metric_api_parser = sub_argument_parsers.add_parser('prometheus_metric_api')
    prometheus_metric_api_parser.add_argument('-ph', '--prometheus-host', dest=HOST, required=True, type=str,
                                              help="Enter Prometheus host")
    prometheus_metric_api_parser.add_argument('-pp', '--prometheus-port', dest=PORT, required=True, type=str,
                                              help="Enter Prometheus port")
    prometheus_metric_api_parser.add_argument('-mn', '--metric-name', dest=METRIC_NAME, required=True, type=str,
                                              help="Enter metric name for scaling decision")
    prometheus_metric_api_parser.add_argument('-l', '--label', dest=LABEL_LIST, required=True, action='append',
                                              type=lambda lv: lv.split("="),
                                              help="Enter label and value for scaling decision. You can add as much"
                                                   "as label and value by repeating the label value"
                                                    "Example: label_name=label_value")
    prometheus_metric_api_parser.add_argument('-sotv', '--scaling-out-threshold-value',
                                              dest=SCALING_OUT_THRESHOLD_VALUE, required=True, type=float,
                                              help="Enter scaling out threshold value for scaling decision")
    prometheus_metric_api_parser.add_argument('-sitv', '--scaling-in-threshold-value', dest=SCALING_IN_THRESHOLD_VALUE,
                                              required=True, type=float,
                                              help="Enter scaling in threshold value for scaling decision")
    prometheus_metric_api_parser.add_argument('-r', '--rate-value', dest=RATE_VALUE, required=True, type=int,
                                              help="Enter rate value to calculate the ratio of the metric"
                                                   " for scaling decision")

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
        self.time_interval = parameters[TIME_INTERVAL]
        if self.management_type == 'prometheus_alert_api':
            self.host = parameters[HOST]
            self.port = parameters[PORT]
            self.scaling_out_name = parameters[SCALING_OUT_NAME]
            self.scaling_in_name = parameters[SCALING_IN_NAME]
        elif self.management_type == 'prometheus_metric_api':
            self.host = parameters[HOST]
            self.port = parameters[PORT]
            self.metric_name = parameters[METRIC_NAME]
            self.label_list = dict(parameters[LABEL_LIST])
            self.scaling_out_threshold_value = parameters[SCALING_OUT_THRESHOLD_VALUE]
            self.scaling_in_threshold_value = parameters[SCALING_IN_THRESHOLD_VALUE]
            self.rate_value = parameters[RATE_VALUE]

        self.common_log = f"Scaling workload for {self.name} (namespace: {self.namespace}, " \
                          f"workload: {self.workload}) is started. Management type is "\
                          f"{self.management_type}. Make sure that always have two alert in Prometheus "\
                          f"for scaling out and scaling in. Each scaling alert workload will change "\
                          f"the pod {self.scaling_range} number amount of pod. "

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

            self.logger.info(self.common_log + f"(host: {self.host}, port: {self.port}, "
                                               f"scaling_out_name: {self.scaling_out_name}, "
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
        elif self.management_type == 'prometheus_metric_api':

            """
            python3 run.py
            -w Deployment -n php-apache -ns default -s 1 -max 10 -min 2 -ti 60
            -mt prometheus_metric_api -ph localhost -pp 9090
            -mn apache_accesses_total -l kubernetes_name=apache-exporter
            -sotv 0.8 -sitv 0.2 -r 300
            """

            self.logger.info(self.common_log + f"(host: {self.host}, port: {self.port}, "
                                               f"metric_name: {self.metric_name}, labels: {self.label_list}, "
                                               f"scaling_out_threshold_value: {self.scaling_out_threshold_value}, "
                                               f"scaling_in_threshold_value: {self.scaling_in_threshold_value}, "
                                               f"range_value:{self.rate_value})")
            manager = PrometheusMetricAPI(
                self.workload,
                self.name,
                self.namespace,
                self.scaling_range,
                self.max_number,
                self.min_number,
                self.host,
                self.port,
                self.metric_name,
                self.label_list,
                self.scaling_out_threshold_value,
                self.scaling_in_threshold_value,
                self.rate_value
            )
            while True:
                manager.control_and_trigger_scaling()
                self.logger.info(f"Waiting {self.time_interval} seconds for the next query if there is any"
                                 f"violation")
                sleep(self.time_interval)
        else:
            self.logger.error(f"Not valid management_type: {self.management_type}")
            raise Exception("Not valid management_type")


if __name__ == '__main__':
    parameter = parse_args()
    run = Run(parameter)
    run.run()
