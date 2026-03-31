import urllib.request
import time
import uuid
import json
import socket

SERVER = "http://127.0.0.1:8000/rpc"
BEACON_INTERVAL = 10

def rpc(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": str(uuid.uuid4())
    }

    req = urllib.request.Request(
        SERVER,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as res:
            if res.status == 204:
                return None
            
            data = json.loads(res.read().decode())

            if "error" in data:
                raise Exception(data["error"])
            
            return data.get("result")
        
    except Exception as e:
        print("[RPC ERROR]", e)
        return None

def get_hostname():
    return socket.gethostname()

def get_mac():
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> ele) & 0xff:02x}'
                    for ele in range(40, -1, -8))

def identify():
    return rpc("identify", {
        "hostname": get_hostname(),
        "mac": get_mac()
    })

def beacon(client_id):
    return rpc("beacon", {
        "client_id": client_id
    })

def execute_task(task):
    if not task:
        return

    method = task.get("method")
    params = task.get("params", {})

    print(f"[TASK] {method} -> {params}")

    handlers = {
        "print_message": lambda p: print(f"[MSG] {p.get('message')}")
    }

    handlers.get(method, lambda _: print("[WARN] method not found"))(params)

def main():
    print("[*] loading profile...")

    result = identify()

    if not result:
        print("[-] failed to load profile")
        return
    
    client_id = result["client_id"]
    print(f"[+] ID {client_id}")

    while True:
        time.sleep(BEACON_INTERVAL)

        result = beacon(client_id)
        if not result:
            continue
        
        execute_task(result.get("task"))

if __name__ == "__main__":
    main()