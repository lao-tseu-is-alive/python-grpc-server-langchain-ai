# server.py
import os
import signal
import time
from concurrent import futures

import grpc
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

# Import the generated gRPC classes
import inference_pb2
import inference_pb2_grpc

# Load environment variables from a .env file for local development
dotenv.load_dotenv()

# --- Configuration ---
# Fetch the API key from environment variables. This is crucial for security in Kubernetes.
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

# --- LangChain Model Initialization ---
# Initialize the Gemini model from LangChain.
# This object will be reused for all requests.
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=API_KEY)
except Exception as e:
    print(f"Failed to initialize LangChain model: {e}")
    # In a real app, you might want to exit or handle this more gracefully
    exit(1)


# --- gRPC Service Implementation ---
# This class implements the service defined in the .proto file.
class InferencerServicer(inference_pb2_grpc.InferencerServicer):
    def GenerateText(self, request, context):
        """
        Handles the GenerateText RPC call.
        """
        prompt = request.prompt
        print(f"Received prompt: '{prompt}'")

        try:
            # Invoke the LangChain model with the given prompt.
            result = llm.invoke(prompt)
            generated_text = result.content
            print(f"Generated response: '{generated_text[:50]}...'")

            # Return the response object.
            return inference_pb2.GenerateResponse(generated_text=generated_text)
        except Exception as e:
            print(f"Error during model invocation: {e}")
            # Inform the gRPC client that an error occurred.
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"An error occurred in the model: {e}")
            return inference_pb2.GenerateResponse()


def serve():
    """
    Starts the gRPC server and handles graceful shutdown.
    """
    print("Initializing gRPC server...")

    # Create a gRPC server with a thread pool for concurrent request handling.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add our implemented service to the server.
    inference_pb2_grpc.add_InferencerServicer_to_server(InferencerServicer(), server)

    # --- Kubernetes Health Probes ---
    # Add the standard gRPC Health Checking service.
    # This allows Kubernetes to check if the application is live and ready.
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    # Set the health status for our specific service. 'SERVING' means it's ready.
    health_servicer.set("inference.Inferencer", health_pb2.HealthCheckResponse.SERVING)

    # Start listening on the specified port.
    port = "50051"
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"✅ Server started successfully on port {port}.")
    print("Ready to accept requests...")

    # --- Graceful Shutdown Logic ---
    # This is critical for Kubernetes. It ensures that the server finishes
    # processing ongoing requests before it is terminated.
    def handle_shutdown(signum, frame):
        print("Received shutdown signal. Stopping server gracefully...")
        # Stop accepting new requests and wait for up to 30 seconds for existing ones to complete.
        server.stop(30)
        print("Server stopped.")

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Keep the server running until it's stopped.
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
