# Kubernetes Workload Scaler

This is a controller to scale the specific deployment with various way. This controller can work for multi-cluster.
* If cluster name is given within metric labels, it calculates the rate and scale the workload by cluster name
* If cluster name is given alarm labels, it scales the workload on the specified cluster
* If cluster name is not given, it will only calculate and scale in the same cluster controller lives

Organizing multi-cluster: 
* https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/
* https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/

## Supported methods to scale workload and Usage

### 1- Prometheus Alert API:

Constantly, watches the Prometheus API (http://host:port/api/v1/alerts) to 
catch the firing alarms. We must have two different alarm rule for scaling out
and scaling in with the following labels. \
For example:
```yaml
  prometheus.rules: |-
    groups:
    - name: Pod Memory
      rules:
      - alert: php-apache-scaling-out # This must be provided
        expr: sum(container_memory_usage_bytes{container="php-apache", namespace="default"}) / (count(container_memory_usage_bytes{container="php-apache", namespace="default"})) > 11000000
        for: 1m
        labels:
          severity: slack
          scaling: out # Must include
          cluster_name: <cluster_name> # If not specified, it load incluster config
        annotations:
          summary: High Memory Usage
      - alert: php-apache-scaling-in # This must be provided
        expr: sum(container_memory_usage_bytes{container="php-apache", namespace="default"}) / (count(container_memory_usage_bytes{container="php-apache", namespace="default"})) < 11000000
        for: 1m
        labels:
          severity: slack
          scaling: in # Must include
          cluster_name: <cluster_name> # If not specified, it load incluster config
        annotations:
          summary: Low Memory Usage
```
Before deploying the pod, define the parameters
```yaml
      env:
        - name: workload
          value: "Deployment"
        - name: scale-name
          value: "php-apache"
        - name: namespace
          value: "default"
        - name: scaling-number
          value: "1"
        - name: max-pod-number
          value: "10"
        - name: min-pod-number
          value: "2"
        - name: time-interval
          value: "60"
        - name: kube-config
          value: "/etc/kube/config"
        - name: managment-type
          value: "prometheus_alert_api"
        - name: prometheus-host
          value: "prometheus-service"
        - name: prometheus-port
          value: "8080"
        - name: scaling-out-name
          value: "php-apache-scaling-out"
        - name: scaling-in-name
          value: "php-apache-scaling-in"
```
If you set the alarms, you can simply run this deployment to scale out/in
```bash
kubectl apply -f https://raw.githubusercontent.com/eminaktas/k8s-workload-scaler/main/examples/php-apache-sample.yaml
```
Then,
```bash
kubectl apply -f https://raw.githubusercontent.com/eminaktas/k8s-workload-scaler/main/examples/k8s-prometheus-sample.yaml
```
It will simply chekcs the Prometheus API and if receives a firing alarm it will trigger regarding the scaling type 
(we must define scaling: in and scaling: out labels) 

### 2- Prometheus Metric API:
Reads, calculates and checks for any violation of thresholds to scale out or scale in

```yaml
      env:
        - name: workload
          value: "Deployment"
        - name: scale-name
          value: "php-apache"
        - name: namespace
          value: "default"
        - name: scaling-number
          value: "1"
        - name: max-pod-number
          value: "10"
        - name: min-pod-number
          value: "2"
        - name: time-interval
          value: "0"
        - name: kube-config
          value: "/etc/kube/config"
        - name: management-type
          value: "prometheus_metric_api"
        - name: prometheus-host
          value: "prometheus-service"
        - name: prometheus-port
          value: "8080"
        - name: metric-name
          value: "apache_accesses_total"
        - name: label-1
          value: "kubernetes_name=apache-exporter"
        - name: label-2
          value: "run=php-apache"
        - name: scaling-out-threshold-value
          value: "0.8"
        - name: scaling-in-threshold-value
          value: "0.2"
        - name: rate_value
          value: "300" # 5 min
```
You can simply run this deployment to scale out/in. This includes an apache exporter. After deploying, make sure 
your Prometheus collecting metrics.
```bash
kubectl apply -f https://raw.githubusercontent.com/eminaktas/k8s-workload-scaler/main/examples/php-apache-sample.yaml
```
Then,
```bash
kubectl apply -f https://raw.githubusercontent.com/eminaktas/k8s-workload-scaler/main/examples/k8s-prometheus-metric-sample.yaml
```

## Supported Workloads
```python3
SUPPORTED_WORKLOAD = [
    'Deployment',
    'StatefulSet',
    'ReplicaSet',
    'ReplicationController',
]
```

## Features
* Auto-Scaling
* Multi-cluster support
* Prometheus alert api and metric api support

## Docker image 
* https://hub.docker.com/r/eminaktas/k8s-workload-scaler
