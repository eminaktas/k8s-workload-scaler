import logging

from kubernetes import client, config
from kubernetes.client.rest import ApiException

__author__ = "Emin AKTAS <eminaktas34@gmail.com>"

CORE_CLIENT = "core_v1"
APP_CLIENT = "apps_v1"
deployment = "Deployment"
stateful_set = "StatefulSet"
replica_set = "ReplicaSet"
replication_controller = "ReplicationController"


class Kubectl:
    def __init__(self):
        # Loads K8s configs from within a cluster within a pod.
        config.load_incluster_config()
        # K8s clients
        self._clients = {
            "core_v1": client.CoreV1Api(),
            "apps_v1": client.AppsV1Api()
        }
        # Logging
        self.logger = logging.getLogger("Kubectl")
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    @property
    def clients(self):
        return self._clients

    def scale_workload(
            self,
            workload: str,
            name: str,
            namespace: str,
            replicas: int,
    ) -> dict:
        """
        Scales namespaced workload
        Workload List:
            Deployment
            Stateful Set
            Replica Set
            Replication Controller
        """
        # Specify the number of replicas for scale out and in

        scale_info = None

        body = {"spec": {"replicas": replicas}}
        try:
            if workload == deployment:
                result = self.clients[APP_CLIENT].patch_namespaced_deployment_scale(name, namespace, body)
            elif workload == stateful_set:
                result = self.clients[APP_CLIENT].patch_namespaced_stateful_set_scale(name, namespace, body)
            elif workload == replica_set:
                result = self.clients[APP_CLIENT].patch_namespaced_replica_set_scale(name, namespace, body)
            elif workload == replication_controller:
                result = self.clients[CORE_CLIENT].patch_namespaced_replication_controller_scale(name, namespace, body)
            else:
                raise Exception
            self.logger.info(f"{name} {workload} scaled to {replicas}")
            # self.logger.info(result)

            scale_info = {
                "new_replicas": result.spec.replicas,
                "old_replicas": result.status.replicas,
            }
        except ApiException as e:
            self.logger.error(f"Error scaling {name} {workload}: {e}")
        finally:
            return scale_info

    def get_replica_info(
            self,
            workload: str,
            name: str,
            namespace: str,
    ) -> dict:
        # Gets the replica information from specific source.

        replica_info = None

        try:
            self.logger.info(f"Getting number of replicas information "
                             f"from {name} (namespace: {namespace}, workload: {workload})")
            if workload == deployment:
                result = self.clients[APP_CLIENT].read_namespaced_deployment(name, namespace)
            elif workload == stateful_set:
                result = self.clients[APP_CLIENT].read_namespaced_stateful_set(name, namespace)
            elif workload == replica_set:
                result = self.clients[APP_CLIENT].read_namespaced_replica_set(name, namespace)
            elif workload == replication_controller:
                result = self.clients[CORE_CLIENT].read_namespaced_replication_controller(name, namespace)
            else:
                raise Exception
            # self.logger.info(result)

            replica_info = {
                'replicas': result.status.replicas
            }

        except ApiException as e:
            self.logger.error(f"Error reading {name} {workload}: {e}")

        finally:
            return replica_info
