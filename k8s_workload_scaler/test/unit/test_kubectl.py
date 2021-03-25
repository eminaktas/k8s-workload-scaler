from unittest import TestCase, mock
from k8s_workload_scaler.kubectl import Kubectl, APP_CLIENT
from k8s_workload_scaler.utils import Dict


class FakeCoreV1Api:
    def patch_namespaced_replication_controller_scale(self, name, namescape, body):
        return fake_scale_return

    def read_namespaced_replication_controller(self, name, namescape):
        return fake_replica_return


class FakeAppsV1Api:
    def patch_namespaced_deployment_scale(self, name, namescape, body):
        return fake_scale_return

    def patch_namespaced_stateful_set_scale(self, name, namescape, body):
        return fake_scale_return

    def patch_namespaced_replica_set_scale(self, name, namescape, body):
        return fake_scale_return

    def read_namespaced_deployment(self, name, namescape):
        return fake_replica_return

    def read_namespaced_stateful_set(self, name, namescape):
        return fake_replica_return

    def read_namespaced_replica_set(self, name, namescape):
        return fake_replica_return


class KubectlTestCase(TestCase):
    @mock.patch('k8s_workload_scaler.kubectl.config.load_incluster_config')
    @mock.patch('k8s_workload_scaler.kubectl.client.CoreV1Api')
    @mock.patch('k8s_workload_scaler.kubectl.client.AppsV1Api')
    def setUp(self, mock_app, mock_core, mock_config):
        mock_app.return_value = FakeAppsV1Api()
        mock_core.return_value = FakeCoreV1Api()
        mock_config.return_value = mock.MagicMock()
        self.kubectl = Kubectl()


fake_scale_return = Dict(
    {
        'spec': Dict(
            {
                'replicas': 6
            }
        ),
        'status': Dict(
            {
                'replicas': 3
            }
        )
    }
)

fake_replica_return = Dict(
    {
        'status': Dict(
            {
                'replicas': 5
            }
        )
    }
)


class ScaleWorkloadTest(KubectlTestCase):
    def setUp(self):
        super(ScaleWorkloadTest, self).setUp()

    def test_scale_deployment_workload(self):
        # Deployment test
        result = self.kubectl.scale_workload(
            'Deployment',
            'scale-name',
            'default',
            6,
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    def test_scale_stateful_set_workload(self):
        # StatefulSet test
        result = self.kubectl.scale_workload(
            'StatefulSet',
            'scale-name',
            'default',
            6,
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    def test_scale_replica_set_workload(self):
        # ReplicaSet test
        result = self.kubectl.scale_workload(
            'ReplicaSet',
            'scale-name',
            'default',
            6,
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    def test_scale_replication_controller_workload(self):
        # ReplicationController test
        result = self.kubectl.scale_workload(
            'ReplicaSet',
            'scale-name',
            'default',
            6,
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    def test_scale_workload_exception(self):
        # Exception test
        result = self.kubectl.scale_workload(
            'random',
            'scale-name',
            'default',
            6,
        )
        self.assertEqual(result, None)


class GetReplicaInfoTest(KubectlTestCase):
    def setUp(self):
        super(GetReplicaInfoTest, self).setUp()

    def test_get_replica_deployment_info(self):
        # Deployment test
        result = self.kubectl.get_replica_info(
            'Deployment',
            'scale-name',
            'default',
        )
        self.assertEqual(result['replicas'], 5)

    def test_get_replica_stateful_set_info(self):
        # StatefulSet test
        result = self.kubectl.get_replica_info(
            'StatefulSet',
            'scale-name',
            'default',
        )
        self.assertEqual(result['replicas'], 5)

    def test_get_replica_replica_set_info(self):
        # ReplicaSet test
        result = self.kubectl.get_replica_info(
            'ReplicaSet',
            'scale-name',
            'default',
        )
        self.assertEqual(result['replicas'], 5)

    def test_get_replica_replication_controller_info(self):
        # ReplicationController test
        result = self.kubectl.get_replica_info(
            'ReplicationController',
            'scale-name',
            'default',
        )
        self.assertEqual(result['replicas'], 5)

    def test_get_replica_exception(self):
        # Exception test
        result = self.kubectl.scale_workload(
            'random',
            'scale-name',
            'default',
            6,
        )
        self.assertEqual(result, None)
