import os
import grpc
from concurrent import futures
import proto.echo_pb2 as echo_pb2
import proto.echo_pb2_grpc as echo_pb2_grpc

SERVICE_NAME = os.getenv("SERVICE_NAME", "echo-unknown")


class EchoServicer(echo_pb2_grpc.EchoServicer):
    def Ping(self, request, context):
        print(f"Received message: {request.message}")
        msg = f"{SERVICE_NAME}: {request.message}"
        return echo_pb2.EchoReply(message=msg)

    def StreamPing(self, request_iterator, context):
        for req in request_iterator:
            yield echo_pb2.EchoReply(message=f"{SERVICE_NAME}: {req.message}")


def serve():
    server_port = 5002
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    echo_pb2_grpc.add_EchoServicer_to_server(EchoServicer(), server)
    server.add_insecure_port(f"[::]:{server_port}")
    print(f"gRPC Echo server {SERVICE_NAME} running on port {server_port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
