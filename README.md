# Kubernetes Workload Scaler

This intended to run on a K8s Workload to scale the specific deployment with 
various way.

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
        annotations:
          summary: High Memory Usage
      - alert: php-apache-scaling-in # This must be provided
        expr: sum(container_memory_usage_bytes{container="php-apache", namespace="default"}) / (count(container_memory_usage_bytes{container="php-apache", namespace="default"})) < 11000000
        for: 1m
        labels:
          severity: slack
          scaling: in # Must include
        annotations:
          summary: Low Memory Usage
```
Before deploying the pod, define the parameters
```env
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
kubectl apply -f https://raw.githubusercontent.com/eminaktas/k8s-workload-scaler/main/examples/prometheus_alert_api/php-apache-sample.yaml
```

Then,
```bash
kubectl apply -f https://raw.githubusercontent.com/eminaktas/k8s-workload-scaler/main/examples/prometheus_alert_api/k8s-prometheus-sample.yaml
```
It will simply chekcs the Prometheus API and if receives a firing alarm it will trigger regarding the scaling type 
(we must define scaling: in and scaling: out labels) 

## Supported Worklodas
```python3
SUPPORTED_WORKLOAD = [
    'Deployment',
    'StatefulSet',
    'ReplicaSet',
    'ReplicationController',
]
```
## Docker image 
* https://hub.docker.com/r/eminaktas/k8s-workload-scaler
