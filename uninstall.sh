#!/bin/bash
kubectl delete -k kubernetes/flux/config
kubectl delete -f kubernetes/flux/vars/cluster-settings.yaml
kubectl delete -f main.key
flux uninstall
sleep 15s