# python-grpc-server-langchain-ai
Python  gRPC Server with LangChain cloud native (Kubernetes-Ready)

you can test with Go client here : https://github.com/lao-tseu-is-alive/go-cloud-grpc-client-ai

### Features

+ gRPC Service: High-performance communication based on a .proto contract.

+ LangChain Integration: Easily connect to models like Gemini Pro.

+ Kubernetes-Ready: Includes manifests for Deployment and Service.

+ Graceful Shutdown: Handles SIGTERM to finish in-flight requests before shutting down.

+ Health Probes: Implements the standard gRPC Health Checking Protocol for Kubernetes liveness and readiness probes.

+ Secure Configuration: Manages API keys via Kubernetes Secrets.

+ Optimized Dockerfile: Uses a multi-stage build for a small and secure final image.

### How to deploy



