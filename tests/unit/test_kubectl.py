from unittest import TestCase, mock
from k8s_workload_scaler.kubectl import Kubectl
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

    def setUp(self):
        self.kubectl = Kubectl('kube-config')


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

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_scale_deployment_workload(self, mock_pick_cluster):
        # Deployment tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.scale_workload(
            'Deployment',
            'scale-name',
            'default',
            6,
            'cluster-name',
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_scale_stateful_set_workload(self, mock_pick_cluster):
        # StatefulSet tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.scale_workload(
            'StatefulSet',
            'scale-name',
            'default',
            6,
            'cluster-name',
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_scale_replica_set_workload(self, mock_pick_cluster):
        # ReplicaSet tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.scale_workload(
            'ReplicaSet',
            'scale-name',
            'default',
            6,
            'cluster-name',
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_scale_replication_controller_workload(self, mock_pick_cluster):
        # ReplicationController tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.scale_workload(
            'ReplicaSet',
            'scale-name',
            'default',
            6,
            'cluster-name',
        )
        self.assertEqual(result['old_replicas'], 3)
        self.assertEqual(result['new_replicas'], 6)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_scale_workload_exception(self, mock_pick_cluster):
        # Exception tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.scale_workload(
            'random',
            'scale-name',
            'default',
            6,
            'cluster-name',
        )
        self.assertEqual(result, None)


class GetReplicaInfoTest(KubectlTestCase):
    def setUp(self):
        super(GetReplicaInfoTest, self).setUp()

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_get_replica_deployment_info(self, mock_pick_cluster):
        # Deployment tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.get_replica_info(
            'Deployment',
            'scale-name',
            'default',
            'cluster-name',
        )
        self.assertEqual(result['replicas'], 5)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_get_replica_stateful_set_info(self, mock_pick_cluster):
        # StatefulSet tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.get_replica_info(
            'StatefulSet',
            'scale-name',
            'default',
            'cluster-name',
        )
        self.assertEqual(result['replicas'], 5)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_get_replica_replica_set_info(self, mock_pick_cluster):
        # ReplicaSet tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.get_replica_info(
            'ReplicaSet',
            'scale-name',
            'default',
            'cluster-name',
        )
        self.assertEqual(result['replicas'], 5)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_get_replica_replication_controller_info(self, mock_pick_cluster):
        # ReplicationController tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.get_replica_info(
            'ReplicationController',
            'scale-name',
            'default',
            'cluster-name',
        )
        self.assertEqual(result['replicas'], 5)

    @mock.patch('k8s_workload_scaler.kubectl.Kubectl.pick_cluster')
    def test_get_replica_exception(self, mock_pick_cluster):
        # Exception tests
        mock_pick_cluster.return_value = {
            'core_v1': FakeCoreV1Api(),
            'apps_v1': FakeAppsV1Api(),
        }
        result = self.kubectl.scale_workload(
            'random',
            'scale-name',
            'default',
            6,
            'cluster-name',
        )
        self.assertEqual(result, None)


class PickClusterTest(KubectlTestCase):
    def setUp(self):
        super(PickClusterTest, self).setUp()
