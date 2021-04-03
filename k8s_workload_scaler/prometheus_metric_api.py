from k8s_workload_scaler.workload_scaler import WorkloadScaler
from prometheus_api_client import PrometheusConnect
from time import sleep

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
            workload: str = None,
            name: str = None,
            namespace: str = None,
            scaling_range: int = None,
            max_number: int = None,
            min_number: int = None,
            kube_config: str = None,
            host: str = None,
            port: str = None,
            metric_name: str = None,
            label_list: dict = None,
            scaling_out_threshold_value: float = None,
            scaling_in_threshold_value: float = None,
            rate_time: int = None,
    ):
        self.host = host
        self.port = port
        self.metric_name = metric_name
        self.scaling_in_threshold_value = scaling_in_threshold_value
        self.scaling_out_threshold_value = scaling_out_threshold_value
        self.label_list = label_list
        self.rate_time = rate_time
        WorkloadScaler.__init__(self, workload, name, namespace, scaling_range, max_number, min_number, kube_config)

        # Logging
        self.logger = logging.getLogger("PrometheusMetricAPI")
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def get_one_metric(self):
        """
        Get defined metric from Prometheus API
        """
        try:
            url = f"http://{self.host}:{self.port}"
            self.logger.info(f"Getting metrics from Prometheus (url={url})")
            prom = PrometheusConnect(url=url, disable_ssl=True)
            metrics = prom.get_current_metric_value(metric_name=self.metric_name, label_config=self.label_list)
            self.logger.debug(f"{metrics}")
            return metrics
        except Exception as e:
            self.logger.error(f"Exception at get_metric: {e}")
            return None

    def rate_metrics(self):
        """
        Calculate the rate of the metrics by cluster
        last value - first value / time(seconds)
        """
        def get_metrics():
            metric_values = self.get_one_metric()
            if not metric_values:
                self.logger.warning(f"Metrics not found: {self.metric_name}{self.label_list} in Prometheus")
                return None
            cluster_names = []
            for cluster in metric_values:
                if cluster['metric'].get('cluster_name'):
                    cluster_names.append(cluster['metric']['cluster_name'])
            return metric_values, cluster_names

        first_metrics, first_clusters = get_metrics()
        # Wait for rate calculation
        sleep(self.rate_time)
        last_metrics, last_clusters = get_metrics()

        rate_list_by_cluster = []
        if first_clusters and last_clusters:
            if sorted(first_clusters) != sorted(last_clusters):
                self.logger.warning(f"Cluster list are not equal between first and last query "
                                    f"first_cluster={first_clusters} != last_cluster={last_clusters}")
                return None

            metric_list_by_cluster = []
            for cluster_name in first_clusters:
                first_total = 0
                last_total = 0
                count_1 = 0
                count_2 = 0
                for f, l in zip(first_metrics, last_metrics):
                    if f['metric']['cluster_name'] == cluster_name:
                        count_1 += 1
                        first_total += float(f['value'][1])
                    if l['metric']['cluster_name'] == cluster_name:
                        count_2 += 1
                        last_total += float(l['value'][1])
                if count_1 != count_2:
                    self.logger.warning(f"{cluster_name} metric counts must match. Skipping...")
                else:
                    metric_list_by_cluster.append({
                        'cluster_name': cluster_name,
                        'first_total': first_total,
                        'last_total': last_total,
                        'count': count_1
                    })

            for metric in metric_list_by_cluster:
                first_avg_total = metric['first_total'] / metric['count']
                last_avg_total = metric['last_total'] / metric['count']
                rate_list_by_cluster.append({
                    'value': (last_avg_total - first_avg_total) / self.rate_time,
                    'cluster_name': metric['cluster_name']
                })
        else:
            first_metric_count = len(first_metrics)
            last_metric_count = len(last_metrics)
            first_total = 0
            last_total = 0
            for f, l in zip(first_metrics, last_metrics):
                first_total += float(f['value'][1])
                last_total += float(l['value'][1])

            first_avg_total = first_total / first_metric_count
            last_avg_total = last_total / last_metric_count

            rate_list_by_cluster.append({
                'value': (last_avg_total - first_avg_total) / self.rate_time
            })

        return rate_list_by_cluster

    def control_and_trigger_scaling(self):
        """
        Controls scaling if there is any violation of threshold
        """
        self.logger.info(f"Controlling for scaling if there is any violation")
        rate_list = self.rate_metrics()
        if rate_list is None:
            self.logger.warning(f"Rate cannot be calculated: {self.metric_name}{self.label_list} not "
                                f"found in Prometheus")
        else:
            for rate in rate_list:
                cluster_name = rate.get('cluster_name', None)
                if rate['value'] > self.scaling_out_threshold_value:
                    self.logger.info(f"Violation detected ({rate['value']} > {self.scaling_out_threshold_value})")
                    self.logger.info(f"The scaling out is triggered for the workload "
                                     f"in cluster: {cluster_name or 'In cluster config'}")
                    self.scale(f"scaling_out", cluster_name)
                elif rate['value'] < self.scaling_in_threshold_value:
                    self.logger.info(f"Violation detected ({rate['value']} < {self.scaling_in_threshold_value})")
                    self.logger.info(f"The scaling in is triggered for the workload "
                                     f"in cluster: {cluster_name or 'In cluster config'}")
                    self.scale(f"scaling_in", cluster_name)
                else:
                    self.logger.info("Violation not detected")
