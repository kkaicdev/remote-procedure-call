from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import deque
import uuid
import json

PORT = 8000

class Server:
    def __init__(self):
        self.clients = {}

    def identify(self, hostname, mac):
        cid = str(uuid.uuid4())

        self.clients[cid] = {
            "id": cid,
            "hostname": hostname,
            "mac": mac,
            "tasks": deque()
        }

        print(f"new client {cid} / {hostname} / {mac}")
        return {"client_id": cid}
        
    def beacon(self, client_id):
        self.get_client(client_id)
        return {"task": self.dequeue(client_id)}

    def send_task(self, client_id, method, params=None):
        self.enqueue(client_id, {
            "method": method,
            "params": params or {}
        })
    
    def get_client(self, client_id):
        c = self.clients.get(client_id)
        if not c:
            raise Exception("client not found")
        return c
    
    def get_queue(self, client_id):
        return self.get_client(client_id)["tasks"]
    
    def enqueue(self, client_id, task):
        self.get_queue(client_id).append(task)

    def dequeue(self, client_id):
        queue = self.get_queue(client_id)
        return queue.popleft() if queue else None

class Dispatcher:
    def __init__(self):
        self.methods = {}

    def register(self, name, fn):
        self.methods[name] = fn

    def call(self, method, params):
        fn = self.methods.get(method)
        if not fn:
            raise Exception(f"method not found: {method}")

        if isinstance(params, dict):
            return fn(**params)
        if isinstance(params, list):
            return fn(*params)
        return fn()

server = Server()
dispatcher = Dispatcher()

dispatcher.register("identify", server.identify)
dispatcher.register("beacon", server.beacon)

# ========
# RPC core
# ========
def call_method(method, params):
    return dispatcher.call(method, params)

def handle(req):
    if "method" not in req:
        raise Exception("invalid request")
    return call_method(req["method"], req.get("params", []))

def response(req_id, result=None, error=None):
    base = {"jsonrpc": "2.0", "id": req_id}
    return base | ({"result": result} if error is None else {"error": error})

def process(data):
    def single(req):
        try:
            result = handle(req)
            return None if req.get("id") is None else response(req.get("id"), result=result)
        except Exception as e:
            return None if req.get("id") is None else response(req.get("id"), error=str(e))
        
    if isinstance(data, list):
        res = list(filter(None, (single(r) for r in data)))
        return res or None
        
    return single(data)

# ============
# CLI commands
# ============
def cmd_list(_):
    for cid, c in server.clients.items():
        print(f"{cid} | {c['hostname']} | {c['mac']}")
    
def cmd_send(parts):
    if len(parts) < 3:
        print("usage: send <id> <msg>")
        return
    
    cid = parts[1]

    if cid not in server.clients:
        print("client not found")
        return
    
    msg = " ".join(parts[2:])
    server.send_task(cid, "print_message", {"message": msg})

def cmd_queue(parts):
    if len(parts) < 2:
        print("usage: queue <id>")
        return
    
    try:
        print(list(server.get_queue(parts[1])))
    except Exception as e:
        print(e)

COMMANDS = {
    "list": cmd_list,
    "send": cmd_send,
    "queue": cmd_queue
}

def cli():
    while True:
        parts = input(">> ").strip().split()
        if not parts:
            continue
        
        COMMANDS.get(parts[0], lambda _: print("unk command"))(parts)

# ====
# HTTP
# ====
class RPCHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/rpc":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode())

            res = process(data)

            if res is None:
                self.send_response(204)
                self.end_headers()
                return

            body = json.dumps(res).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            body = json.dumps(response(None, error=str(e))).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

def run():
    print(f'server on {PORT}')

    import threading

    threading.Thread(target=cli, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), RPCHandler).serve_forever()

if __name__ == "__main__":
    run()