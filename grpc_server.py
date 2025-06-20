import grpc
from concurrent import futures
import grpc_shapes_pb2
import grpc_shapes_pb2_grpc
import threading
import os
import sys
import uuid
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from client.services.supabase_client import get_supabase_client

class ShapeServiceServicer(grpc_shapes_pb2_grpc.ShapeServiceServicer):
    def CreateShape(self, request, context):
        shape_data = {
            'id': request.id or str(uuid.uuid4()),
            'type': request.type,
            'x': request.x,
            'y': request.y,
            'width': request.width,
            'height': request.height,
            'color': request.color,
            'text': request.text,
            'font_size': request.font_size,
            'version': request.version,
            'session_id': request.session_id
        }
        supabase = get_supabase_client()
        try:
            supabase.table("whiteboard_shapes").insert(shape_data).execute()
            return grpc_shapes_pb2.ShapeResponse(success=True, message="Shape created", shape=request)
        except Exception as e:
            return grpc_shapes_pb2.ShapeResponse(success=False, message=str(e))

    def UpdateShape(self, request, context):
        shape_id = request.id
        data = {
            'x': request.x,
            'y': request.y,
            'width': request.width,
            'height': request.height,
            'color': request.color,
            'text': request.text,
            'font_size': request.font_size,
            'version': request.version,
        }
        supabase = get_supabase_client()
        try:
            supabase.table("whiteboard_shapes").update(data).eq('id', shape_id).execute()
            return grpc_shapes_pb2.ShapeResponse(success=True, message="Shape updated", shape=request)
        except Exception as e:
            return grpc_shapes_pb2.ShapeResponse(success=False, message=str(e))

    def DeleteShape(self, request, context):
        shape_id = request.id
        supabase = get_supabase_client()
        try:
            supabase.table("whiteboard_shapes").delete().eq('id', shape_id).execute()
            return grpc_shapes_pb2.ShapeResponse(success=True, message="Shape deleted")
        except Exception as e:
            return grpc_shapes_pb2.ShapeResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_shapes_pb2_grpc.add_ShapeServiceServicer_to_server(ShapeServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server running on port 50051")
    server.wait_for_termination()

def start_grpc_server_in_thread():
    t = threading.Thread(target=serve, daemon=True)
    t.start()

if __name__ == "__main__":
    serve() 