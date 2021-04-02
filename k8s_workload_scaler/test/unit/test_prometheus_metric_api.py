from unittest import TestCase, mock
from k8s_workload_scaler.prometheus_metric_api import PrometheusMetricAPI


class PrometheusMeticAPITestCase(TestCase):
    @mock.patch('k8s_workload_scaler.kubectl.config.load_incluster_config')
    def setUp(self, mock_config):
        self.prometheus_alert_api = PrometheusMetricAPI(
            'Deployment',
            'scale-name',
            'default',
            1,
            10,
            2,
            'prometheus',
            '9090',
            'metric-name',
            {'label': 'value'},
            0.8,
            0.2,
            300,
        )
        mock_config.return_value = mock.MagicMock()


class GetOneMetricTest(PrometheusMeticAPITestCase):
    def setUp(self):
        super(GetOneMetricTest, self).setUp()

    @mock.patch('prometheus_api_client.prometheus_connect.PrometheusConnect.get_current_metric_value')
    def test_prometheus_connect_exception(self, mock_get_current_metric_value):
        mock_get_current_metric_value.side_effect = Exception
        self.assertRaises(Exception, self.prometheus_alert_api.get_one_metric())
