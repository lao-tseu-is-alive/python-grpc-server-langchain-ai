# Use a multi-stage build for a smaller and more secure final image.

# --- Stage 1: Builder ---
# This stage installs dependencies and generates the gRPC code.
# Use Python 3.11, which has broad and stable support for AI/ML libraries.
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Install Python dependencies required for building
RUN pip install --no-cache-dir grpcio-tools==1.62.0

# Copy the requirements file and install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Generate the gRPC Python code from the .proto file
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inference.proto

# --- Stage 2: Final Image ---
# This stage creates the final, lean image for production.
FROM python:3.11-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Production image for the Python gRPC LangChain server."

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code and the generated gRPC files from the builder stage
COPY --from=builder /app .

# Expose the gRPC port
EXPOSE 50051

# Define the command to run the application
CMD ["python", "grpcServer.py"]

