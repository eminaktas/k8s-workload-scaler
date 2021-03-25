from unittest import TestCase, mock
from k8s_workload_scaler.workload_scaler import WorkloadScaler


class WorkloadScalerTestCase(TestCase):
    @mock.patch('k8s_workload_scaler.kubectl.config.load_incluster_config')
    def setUp(self, mock_config):
        self.workload_scaler = WorkloadScaler(
            'Deployment',
            'scale-name',
            'default',
            1,
            10,
            2,
        )
        mock_config.return_value = mock.MagicMock()


class ControlReplicasTest(WorkloadScalerTestCase):
    def setUp(self):
        super(ControlReplicasTest, self).setUp()

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_out(self, mock_get_replica_info):
        mock_get_replica_info.return_value = {'replicas': 5}
        result = self.workload_scaler.control_replicas('scaling_out')
        self.assertEqual(result, 6)

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_in(self, mock_get_replica_info):
        mock_get_replica_info.return_value = {'replicas': 5}
        result = self.workload_scaler.control_replicas('scaling_in')
        self.assertEqual(result, 4)

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_min(self, mock_get_replica_info):
        mock_get_replica_info.return_value = {'replicas': 2}
        result = self.workload_scaler.control_replicas('scaling_in')
        self.assertEqual(result, None)

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_less_min(self, mock_get_replica_info):
        mock_get_replica_info.return_value = {'replicas': 0}
        result = self.workload_scaler.control_replicas('scaling_in')
        self.assertEqual(result, 2)

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_max(self, mock_get_replica_info):
        mock_get_replica_info.return_value = {'replicas': 10}
        result = self.workload_scaler.control_replicas('scaling_out')
        self.assertEqual(result, None)

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_more_max(self, mock_get_replica_info):
        mock_get_replica_info.return_value = {'replicas': 12}
        result = self.workload_scaler.control_replicas('scaling_out')
        self.assertEqual(result, 10)

    @mock.patch('k8s_workload_scaler.workload_scaler.Kubectl.get_replica_info')
    def test_control_replica_exception(self, mock_get_replica_info):
        mock_get_replica_info.return_value = None
        self.assertRaises(Exception, self.workload_scaler.control_replicas)


class ScaleTestCase(WorkloadScalerTestCase):
    def setUp(self):
        super(ScaleTestCase, self).setUp()

    @mock.patch('k8s_workload_scaler.workload_scaler.WorkloadScaler.control_replicas')
    @mock.patch('k8s_workload_scaler.workload_scaler.WorkloadScaler.scale_workload')
    def test_scale_none(self, mock_scale_workload, mock_control_replicas):
        mock_control_replicas.return_value = None
        mock_scale_workload = mock.Mock()
        self.workload_scaler.scale('scaling_out')
        mock_scale_workload.assert_not_called()

    @mock.patch('k8s_workload_scaler.workload_scaler.WorkloadScaler.control_replicas')
    def test_scale_exception(self, mock_control_replicas):
        self.assertRaises(Exception, self.workload_scaler.scale)

    # @mock.patch('k8s_workload_scaler.workload_scaler.WorkloadScaler.control_replicas')
    # @mock.patch('k8s_workload_scaler.workload_scaler.WorkloadScaler.scale_workload')
    # def test_scale_success(self, mock_scale_workload, mock_control_replicas):
    #     mock_control_replicas.return_value = 5
    #     mock_scale_workload.return_value = {
    #         'old_replicas': 2,
    #         'new_replicas': 5
    #     }
    #     result = self.workload_scaler.scale('scale_out')
    #     self.assertEqual(result, {'old_replicas': 2, 'new_replicas': 5})
