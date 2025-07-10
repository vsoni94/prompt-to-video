# Text-to-Video Generation Service

This repository contains a FastAPI-based backend and Celery worker setup for generating videos from text prompts using the Genmo Mochi pipeline. The system is deployed on Kubernetes with GPU acceleration enabled.

---

## Features

- Submit video generation jobs via REST API
- Asynchronous video generation using Celery workers
- Video files served via static endpoints
- Redis used as a job queue and status store
- GPU acceleration for model inference on NVIDIA GPUs in Kubernetes
- ffmpeg used for video encoding compatible with browsers

---

## Prerequisites

- Kubernetes cluster with NVIDIA GPUs
- NVIDIA drivers and device plugin installed on the cluster nodes
- Docker installed for building container images
- Redis deployed in the Kubernetes cluster
- `kubectl` CLI configured to access your cluster
- `jq` installed locally (for JSON processing)

---

## Project Structure

- `app/main.py` — FastAPI app for job management and video result serving
- `app/worker.py` — Celery worker process that generates videos
- `app/video_generator.py` — Video generation logic using MochiPipeline
- `app/jobs.py` — Redis utility functions for job status management
- `k8s/` — Kubernetes manifests for API, worker, Redis, and services

---

## Building and Pushing Docker Images

```bash
# backenc
docker build -t varunsoni94/text2video-api .
docker push varunsoni94/text2video-api
#frontend
docker build -t varunsoni94/text2video-frontend ./frontend
docker push varunsoni94/text2video-frontend
```

---
## Kubernetes Deployment

### Apply manifests in order:
```bash
kubectl --kubeconfig kube.conf apply -f k8s/redis-deployment.yaml
kubectl --kubeconfig kube.conf apply -f k8s/api-deployment.yaml
kubectl --kubeconfig kube.conf apply -f k8s/worker-deployment.yaml
kubectl --kubeconfig kube.conf apply -f k8s/service.yaml
kubectl --kubeconfig kube.conf apply -f k8s/frontend-deployment.yaml
```
### Restart deployments if needed:
```bash
kubectl --kubeconfig kube.conf rollout restart deployment text2video-api
kubectl --kubeconfig kube.conf rollout restart deployment text2video-worker
kubectl --kubeconfig kube.conf rollout restart deployment redis
kubectl --kubeconfig kube.conf rollout restart deployment text2video-frontend
```

## Useful Kubernetes commands
```bash
kubectl --kubeconfig kube.conf get deployments
kubectl --kubeconfig kube.conf get pods -o wide
kubectl --kubeconfig kube.conf get svc

# View Logs (Live)
kubectl --kubeconfig kube.conf logs -f deployment/text2video-api
kubectl --kubeconfig kube.conf logs -f deployment/text2video-worker
kubectl --kubeconfig kube.conf logs -f <pod-name>

# Exec Into Pod Shell
kubectl --kubeconfig kube.conf exec -it text2video-worker-xxxxxx -- /bin/bash

kubectl --kubeconfig kube.conf port-forward svc/text2video-api-service 8000:8000

# Delete Pods, Deployments, Services
kubectl --kubeconfig kube.conf delete pod <pod-name>
kubectl --kubeconfig kube.conf delete deployment <deployment-name>
kubectl --kubeconfig kube.conf delete svc <service-name>
```

## Debugging Tips
- Check pod status and events using kubectl describe pod <pod-name>

- Ensure Redis is reachable and healthy

- Verify GPU allocation via nvidia-smi inside the pod shell

- Confirm ffmpeg is installed and working correctly in the container

- Look for "Cannot re-initialize CUDA in forked subprocess" errors — use spawn start method in multiprocessing

- Monitor pod memory usage and adjust Kubernetes resource limits accordingly

## FFmpeg Setup and Troubleshooting

- Install ffmpeg on the host or inside containers as needed:

```bash
sudo apt update
sudo apt install -y ffmpeg
```
 - Re-encode generated videos for browser compatibility using H264 codec and faststart flag (done in code).

 - Use to check video codec and container format.
 ```bash
 ffmpeg -i /mnt/data/output/<video>.mp4
 ```

 ## Exposing Services Outside Cluster
 - Optionally use MetalLB for LoadBalancer IP on LAN:
 ```bash
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml
kubectl apply -f k8s/metallb-config.yaml
```
- Set service type to LoadBalancer in your YAML manifests
- Set up port forwarding or router port forwarding to expose the service externally

## If model is using using, follow below
## NVIDIA GPU Setup on Kubernetes

- Install NVIDIA device plugin:
```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
```
- Verify GPUs available on nodes:
```bash
kubectl get nodes -o json | jq '.items[].status.allocatable'
```
- Install NVIDIA Container Toolkit on nodes:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart containerd
```
- Fix containerd config (if needed) to point to correct nvidia-container-runtime path and restart.
- Create RuntimeClass for NVIDIA in deployment.yaml:
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: nvidia
handler: nvidia
```
- Apply with:
```bash
kubectl apply -f nvidia-runtimeclass.yaml
```