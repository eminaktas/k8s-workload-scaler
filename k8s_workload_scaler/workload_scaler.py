from k8s_workload_scaler.kubectl import Kubectl
import logging

__author__ = "Emin AKTAS <eminaktas34@gmail.com>"


class WorkloadScaler(Kubectl):
    """
    WorkloadScaler class
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
    ):
        self.workload = workload
        self.name = name
        self.namespace = namespace
        self.scaling_range = scaling_range
        self.max_number = max_number
        self.min_number = min_number

        # Parent class
        Kubectl.__init__(self, kube_config)

        # Logging
        self.logger = logging.getLogger("WorkloadScaler")
        logging.basicConfig(
            level=logging.NOTSET,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def control_replicas(self, scaling, cluster_name: str = None):
        """
        Controls the replica information from the workload
        """
        try:
            self.logger.info(f"Getting information for {self.name} (namespace: {self.namespace}, "
                             f"workload: {self.workload})")
            # Get the replica information from the workload
            replica_info = self.get_replica_info(self.workload, self.name, self.namespace, cluster_name)

            if replica_info:
                # Replica number of the workload
                replicas = replica_info['replicas'] or 0

                if scaling == 'scaling_out':
                    new_replicas = replicas + self.scaling_range
                elif scaling == 'scaling_in':
                    new_replicas = replicas - self.scaling_range
                else:
                    self.logger.error("Scaling direction must be defined (scaling_out or scaling_in)")
                    raise Exception

                # Control if scaling is already met
                if (replicas == self.max_number or replicas == self.min_number)\
                        and not self.min_number < new_replicas < self.max_number:
                    self.logger.info(f"current replica number is already at "
                                     f"max:{self.max_number}/min:{self.min_number}"
                                     f" current replicas: {replicas}")
                    return None
                if replicas > self.max_number:
                    self.logger.warning(f"current replica number is more than max_number"
                                        f" scaling to max_number: {self.max_number}")
                    return self.max_number
                elif replicas < self.min_number:
                    self.logger.warning(f"current replica number is less than min_number"
                                        f" scaling to min_number: {self.min_number}")
                    return self.min_number
                else:
                    self.logger.info(f"Scaling {self.name} (namespace: {self.namespace}, workload: {self.workload}) "
                                     f"from {replicas} to {new_replicas}")
                    return new_replicas
            else:
                self.logger.error(f"{self.name} (namespace: {self.namespace}, workload: {self.workload}) not found")
                raise Exception("replica_info not found")
        except Exception as e:
            self.logger.error(f"Exception at control_replicas: {e}")
            return None

    def scale(self, scaling, cluster_name: str = None):
        """
        Scales the target workload
        """
        self.logger.info(f"Scaling {self.name} (namespace: {self.namespace}, workload: {self.workload})")

        new_replica_number = self.control_replicas(scaling, cluster_name)

        if new_replica_number is None:
            self.logger.warning(f"Scaling {self.name} (namespace: {self.namespace}, "
                                f"workload: {self.workload}) is aborted.")
            return
        try:
            result = self.scale_workload(self.workload, self.name, self.namespace, new_replica_number)

            if result:
                self.logger.info(f"{self.name} (namespace: {self.namespace}, workload: {self.workload}) is scaled from "
                                 f"{result['old_replicas']} to {result['new_replicas']}")
        except Exception as e:
            self.logger.error(f"Exception at scale: {e}")
