#!/bin/bash
kubectl delete -k kubernetes/flux/config
kubectl delete -f kubernetes/flux/vars/cluster-settings.yaml
flux uninstall
sleep 15s
kubectl delete namespace flux-system