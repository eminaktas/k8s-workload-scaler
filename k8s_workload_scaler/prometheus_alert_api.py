from k8s_workload_scaler.workload_scaler import WorkloadScaler

import requests
import logging

__author__ = "Emin AKTAS <eminaktas34@gmail.com>"


class PrometheusAlertAPI(WorkloadScaler):
    """
    PrometheusAlertAPI watches Prometheus alert api to trigger the scaling

    Alert manager api
    $ curl http://localhost:30000/api/v1/alertmanagers
    List alerts
    $ curl http://localhost:30000/api/v1/alerts
    Sample query for alert rule
    $ sum(container_memory_usage_bytes{container="php-apache", namespace="default"}) /
     (count(container_memory_usage_bytes{container="php-apache", namespace="default"}))
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
            scaling_out_name,
            scaling_in_name,
    ):
        self.host = host
        self.port = port
        self.scaling_out_name = scaling_out_name
        self.scaling_in_name = scaling_in_name
        WorkloadScaler.__init__(self, workload, name, namespace, scaling_range, max_number, min_number)

        # Logging
        self.logger = logging.getLogger("PrometheusAlertAPI")
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def control_alert_and_trigger_scaling(self):
        """
        Finds the alert and controls if alert if firing and triggers the scaling
        """
        url = f"http://{self.host}:{self.port}/api/v1/alerts"
        self.logger.info(f"Now, calling the Prometheus API ({url}) to check if alert is firing")
        result = requests.get(url)
        if result.status_code > 299:
            self.logger.error(f"Exception at control_alert_ad_trigger_scaling, "
                              f"status code: {result.status_code}, reason: {result.reason}")
            raise requests.RequestException
        j_result = result.json()
        if j_result.get('status', None) == 'success' and j_result.get('data', {}).get('alerts', None):
            alert = next(_alert for _alert in j_result['data']['alerts']
                         if (_alert['labels']['alertname'] == self.scaling_out_name or
                             _alert['labels']['alertname'] == self.scaling_in_name))
            if alert['state'] == 'firing':
                self.logger.info("Prometheus alert is firing, the scaling is triggered")
                self.scale(f"scaling_{alert['labels']['scaling']}")
            else:
                self.logger.info("Prometheus alert is not firing, scaling not triggered")
                self.logger.info(f"Current metric value {alert['value']}")
