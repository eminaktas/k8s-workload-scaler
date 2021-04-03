import logging

from kubernetes import client, config
from kubernetes.client.rest import ApiException

__author__ = 'Emin AKTAS <eminaktas34@gmail.com>'

CORE_CLIENT = 'core_v1'
APP_CLIENT = 'apps_v1'
workload_list = {
    'deployment': 'Deployment',
    'stateful_set': 'StatefulSet',
    'replica_set': 'ReplicaSet',
    'replication_controller': 'ReplicationController',
}


class Kubectl:
    def __init__(self, kube_config):
        self.kube_config = kube_config
        # Logging
        self.logger = logging.getLogger('Kubectl')
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def pick_cluster(self, cluster_name: str = None):
        """
        Pick the cluster you will scale the workload
        """
        try:
            # Load the context in kube-config file
            contexts, active_context = config.list_kube_config_contexts(config_file=self.kube_config)
            self.logger.debug(f"contexts: {contexts}, active_context: {active_context}")
            if not contexts:
                self.logger.error("Cannot locate any context in kube-config file")
                return
            contexts = [context['name'] for context in contexts]
            self.logger.debug(f"context list: {contexts}")
            if cluster_name is None:
                cluster_name = active_context['name']
            target_cluster_index = next((i for i, j in enumerate(contexts) if cluster_name in j), None)
            if target_cluster_index is None:
                self.logger.error(f"Cannot find {cluster_name} in {contexts}")
                return

            picked_cluster = contexts[target_cluster_index]
            self.logger.debug(f"Picked cluster: {picked_cluster}")

            return {
                'core_v1': client.CoreV1Api(
                    api_client=config.new_client_from_config(context=picked_cluster)
                ),
                'apps_v1': client.AppsV1Api(
                    api_client=config.new_client_from_config(context=picked_cluster)
                ),
            }
        except Exception as e:
            self.logger.error(f"Can't pick a cluster: {e}")
            raise e

    def clients(self, cluster_name: str = None):
        self.logger.debug("Picking cluster")
        return self.pick_cluster(cluster_name)

    def scale_workload(
            self,
            workload: str,
            name: str,
            namespace: str,
            replicas: int,
            cluster_name: str = None,
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

        body = {'spec': {'replicas': replicas}}
        try:
            if workload == workload_list['deployment']:
                result = self.clients(cluster_name)[APP_CLIENT].patch_namespaced_deployment_scale(
                    name, namespace, body)
            elif workload == workload_list['stateful_set']:
                result = self.clients(cluster_name)[APP_CLIENT].patch_namespaced_stateful_set_scale(
                    name, namespace, body)
            elif workload == workload_list['replica_set']:
                result = self.clients(cluster_name)[APP_CLIENT].patch_namespaced_replica_set_scale(
                    name, namespace, body)
            elif workload == workload_list['replication_controller']:
                result = self.clients(cluster_name)[CORE_CLIENT].patch_namespaced_replication_controller_scale(
                    name, namespace, body)
            else:
                self.logger.error(f"{workload} is not supported "
                                  f"Supported workloads: {workload_list}")
                raise Exception(f"{workload} is not supported")
            self.logger.info(f"{name} {workload} scaled to {replicas}")
            # self.logger.info(result)

            scale_info = {
                'new_replicas': result.spec.replicas,
                'old_replicas': result.status.replicas,
            }
        except ApiException as e:
            self.logger.error(f"Error scaling {name} {workload}: {e}")
            raise e
        finally:
            return scale_info

    def get_replica_info(
            self,
            workload: str,
            name: str,
            namespace: str,
            cluster_name: str = None,
    ) -> dict:
        # Gets the replica information from specific source.

        replica_info = None

        try:
            self.logger.info(f"Getting number of replicas information "
                             f"from {name} (namespace: {namespace}, workload: {workload})")
            if workload == workload_list['deployment']:
                result = self.clients(cluster_name)[APP_CLIENT].read_namespaced_deployment(name, namespace)
            elif workload == workload_list['stateful_set']:
                result = self.clients(cluster_name)[APP_CLIENT].read_namespaced_stateful_set(name, namespace)
            elif workload == workload_list['replica_set']:
                result = self.clients(cluster_name)[APP_CLIENT].read_namespaced_replica_set(name, namespace)
            elif workload == workload_list['replication_controller']:
                result = self.clients(cluster_name)[CORE_CLIENT].read_namespaced_replication_controller(name, namespace)
            else:
                self.logger.error(f"{workload} is not supported "
                                  f"Supported workloads: {workload_list}")
                raise Exception(f"{workload} is not supported")
            # self.logger.info(result)

            replica_info = {
                'replicas': result.status.replicas
            }

        except ApiException as e:
            self.logger.error(f"Error reading {name} {workload}: {e}")
            raise e
        finally:
            return replica_info
