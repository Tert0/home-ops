#!/bin/python
import base64
import subprocess
import yaml
import os
KUBESEAL="kubeseal --controller-name=sealed-secrets"

def seal(data: str) -> str:
    process = subprocess.run(f"{KUBESEAL} --format yaml".split(" "), input=data, capture_output=True, text=True)
    return process.stdout

def unseal(data: str) -> str:
    process = subprocess.run(f"{KUBESEAL} --format yaml --recovery-unseal --recovery-private-key main.key".split(" "), input=data, capture_output=True, text=True)
    return process.stdout

def encode_secret(content: dict) -> dict:
    assert 'apiVersion' in content and 'kind' in content
    assert content['apiVersion'] == "v1" and content['kind'] == "Secret"
    assert 'stringData' in content or 'data' in content
    if 'stringData' in content:
        if 'data' not in content:
            content['data'] = dict()
        for k, v in content['stringData'].items():
            content['data'][k] = base64.b64encode(v.encode()).decode()
        del content['stringData']
    return content


def process_secret(unsealed_path, sealed_path):
    print(f"Processing '{unsealed_path}'")
    with open(unsealed_path, "r") as f:
        unsealed_raw = f.read()
        unsealed_content = encode_secret(yaml.safe_load(unsealed_raw))
    try:
        os.stat(sealed_path)
        sealed_exists = True
    except FileNotFoundError:
        sealed_exists = False

    if not sealed_exists:
        print("\033[0;32m  Sealing Secret\033[0;0m")
        sealed_raw = seal(unsealed_raw)
        with open(sealed_path, "w") as f:
            f.write(sealed_raw)
    else:
        with open(sealed_path, "r") as f:
            sealed_raw = f.read()
            unsealed_sealed_raw = unseal(sealed_raw)
            unsealed_sealed_content = yaml.safe_load(unsealed_sealed_raw)
        metadata_matching = unsealed_sealed_content['metadata']['name'] == unsealed_content['metadata']['name'] and \
            unsealed_sealed_content['metadata'].get("namespace") == unsealed_content['metadata'].get("namespace", "default")
        data_matching = unsealed_sealed_content['data'] == unsealed_content['data']
        if not metadata_matching or not data_matching:
            print("\033[0;32m    Resealing Secret\033[0;0m")
            with open(sealed_path, "w") as f:
                f.write(seal(unsealed_raw))
        else:
            print("\033[0;31m    Not Resealing Secret \033[0;0m")
for root, _, files in os.walk("."):
    for file in files:
        if 'unsealed' not in file:
            continue
        process_secret(f"{root}/{file}", f"{root}/{file.replace('unsealed', 'sealed')}")