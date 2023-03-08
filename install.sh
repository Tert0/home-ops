#!/bin/bash
# Check if sealed secrets main.key exists
if [[ ! -f main.key ]]
then
    echo "The sealed secrets main private key file (main.key) is missing."
    exit 1
fi

# Check if Cluster is viable
flux check --pre

kubectl create namespace flux-system
# Install Flux
kubectl apply -k kubernetes/bootstrap
sleep 10
# TODO automate with kubectl wait
read -p "Press enter when the basic flux components are read."
# Add sealed secret main.key
kubectl apply -f main.key
# Adding Cluster-wide ConfigMap
kubectl apply -f kubernetes/flux/vars/cluster-settings.yaml
# Adding Flux Configs (Repository and main Kustomization)
kubectl apply -k kubernetes/flux/config