from k8s_workload_scaler.workload_scaler import WorkloadScaler
from prometheus_api_client import PrometheusConnect

import logging

__author__ = "Emin AKTAS <eminaktas34@gmail.com>"


class PrometheusMetricAPI(WorkloadScaler):
    """
    PrometheusMetricAPI scrapes metrics and controls to trigger scaling

    This function basically grapes the metrics of specified with label name, label value and metric name.
    It sums metric values and dived by the pod number of target pod which is to be scaled.
    With the defined threshold values, it controls the violation
    """

    def __init__(
            self,
            workload,
            name,
            namespace,
            scaling_range,
            max_number,
            min_number,
            host,
            port,
            metric_name,
            label_name,
            label_value,
            scaling_out_threshold_value,
            scaling_in_threshold_value,
    ):
        self.host = host
        self.port = port
        self.metric_name = metric_name
        self.scaling_in_threshold_value = scaling_in_threshold_value
        self.scaling_out_threshold_value = scaling_out_threshold_value
        self.label_value = label_value
        self.label_name = label_name
        WorkloadScaler.__init__(self, workload, name, namespace, scaling_range, max_number, min_number)

        # Logging
        self.logger = logging.getLogger("PrometheusMetricAPI")
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # TODO: define get_metric_custom function for custom queries

    def get_metric(self):
        """
        Get defined metric from Prometheus API
        """
        try:
            url = f"http://{self.host}:{self.port}"
            self.logger.info(f"Getting metrics from Prometheus (url={url})")
            prom = PrometheusConnect(url=url, disable_ssl=True)
            label_config = {self.label_name: self.label_value}
            metrics = prom.get_current_metric_value(metric_name=self.metric_name, label_config=label_config)
            self.logger.debug(f"{metrics}")
            return metrics
        except Exception as e:
            self.logger.error(f"Exception at get_metric: {e}")
            return None

    def control_scaling(self):
        """
        Controls scaling if there is any violation of threshold
        """
        self.logger.info(f"Controlling for scaling if there is any violation")
        metrics = self.get_metric()
        if metrics:
            metric_count = len(metrics)
            total = 0
            for _ in metrics:
                # The value of metric
                total += float(_['value'][1])
            avg_total = total / metric_count

            if avg_total > self.scaling_out_threshold_value:
                self.logger.info(f"Violation detected ({avg_total} > {self.scaling_out_threshold_value})")
                self.logger.info("The scaling out is triggered")
                self.scale(f"scaling_out")
            elif avg_total < self.scaling_in_threshold_value:
                print(f"Violation detected ({avg_total} < {self.scaling_in_threshold_value})")
                self.logger.info("The scaling in is triggered")
                self.scale(f"scaling_in")
            else:
                print("Violation not detected")
        else:
            self.logger.debug(f"Not found: {self.metric_name}[{self.label_name}={self.label_value}] in Prometheus API")
