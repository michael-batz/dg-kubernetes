apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ app_id }}
  labels:
    appid: {{ app_id }}
    appname: {{ app_name }}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: "{{ hostname }}.dev.michael-batz.de"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ app_id }}
            port:
              number: 4000
---
apiVersion: v1
kind: Service
metadata:
  name: {{ app_id }}
  labels:
    appid: {{ app_id }}
    appname: {{ app_name }}
spec:
  type: ClusterIP
  selector:
    appid: {{ app_id }}
  ports:
  - protocol: TCP
    port: 4000
    targetPort: 4000
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ app_id }}
  labels:
    appid: {{ app_id }}
    appname: {{ app_name }}
spec:
  selector:
    matchLabels:
      appid: {{ app_id }}
  serviceName: "{{ app_id }}"
  replicas: 1
  template:
    metadata:
      labels:
        appid: {{ app_id }}
        appname: {{ app_name }}
    spec:
      containers:
      - name: datagerry
        image: nethinks/datagerry:{{ app_version }}
        env:
        - name: DATAGERRY_Database_host
          value: "127.0.0.1"
        - name: DATAGERRY_MessageQueueing_host
          value: "127.0.0.1"
      - name: db
        image: mongo:4.2-bionic
        volumeMounts:
        - name: {{ app_id }}
          mountPath: /data/db
        - name: {{ app_id }}
          mountPath: /data/configdb
      - name: broker
        image: rabbitmq:3.8
        volumeMounts:
        - name: {{ app_id }}
          mountPath: /var/lib/rabbitmq
  volumeClaimTemplates:
  - metadata:
      name: {{ app_id }}
      labels:
        appid: {{ app_id }}
        appname: {{ app_name }}
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 10Gi
      storageClassName: do-block-storage
