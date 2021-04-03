from unittest import TestCase, mock
from k8s_workload_scaler.prometheus_alert_api import PrometheusAlertAPI
from requests import RequestException


class FakeResponse404:
    status_code = 404
    reason = 404


class FakeResponse200:
    status_code = 200

    @staticmethod
    def json():
        return {
            'status': 'success',
            'data': {
                'alerts': [{
                    'labels': {
                        'alertname': 'scaling-out-name',
                        'scaling': 'out',
                    },
                    'state': 'firing',
                    'value': 10e7
                }]
            }
        }


class FakeResponse200Inactive:
    status_code = 200

    @staticmethod
    def json():
        return {
            'status': 'success',
            'data': {
                'alerts': [{
                    'labels': {
                        'alertname': 'scaling-out-name',
                        'scaling': 'out',
                    },
                    'state': 'inactive',
                    'value': 10e6
                }]
            }
        }


class PrometheusAlertAPITestCase(TestCase):
    @mock.patch('k8s_workload_scaler.kubectl.config.load_incluster_config')
    def setUp(self, mock_config):
        self.prometheus_alert_api = PrometheusAlertAPI(
            'Deployment',
            'scale-name',
            'default',
            1,
            10,
            2,
            'kube-config',
            'prometheus',
            '9090',
            'scaling-out-name',
            'scaling-in-name'
        )
        mock_config.return_value = mock.MagicMock()


class ControlAlertandTriggerScalingTest(PrometheusAlertAPITestCase):
    def setUp(self):
        super(ControlAlertandTriggerScalingTest, self).setUp()

    @mock.patch('requests.get')
    def test_request_exception(self, mock_get):
        mock_get.return_value = FakeResponse404()
        with self.assertRaises(RequestException):
            self.prometheus_alert_api.control_alert_and_trigger_scaling()

    @mock.patch('requests.get')
    @mock.patch('k8s_workload_scaler.prometheus_alert_api.WorkloadScaler.scale')
    def test_firing_alarm(self, mock_scale, mock_get):
        mock_get.return_value = FakeResponse200()
        self.prometheus_alert_api.control_alert_and_trigger_scaling()
        mock_scale.assert_called_once()

    @mock.patch('requests.get')
    @mock.patch('k8s_workload_scaler.prometheus_alert_api.WorkloadScaler.scale')
    def test_inactive_alarm(self, mock_scale, mock_get):
        mock_get.return_value = FakeResponse200Inactive()
        self.prometheus_alert_api.control_alert_and_trigger_scaling()
        mock_scale.assert_not_called()
