from .commands import COMMANDS

def run_cli(server):
    while True:
        parts = input(">> ").strip().split()
        if not parts:
            continue

        cmd = COMMANDS.get(parts[0])
        if not cmd:
            print("unk command")
            continue
        
        cmd(server, parts)  
