from .commands import COMMANDS

def run_cli(server):
    while True:
        parts = input(">> ").strip().split()
        if not parts:
            continue
        
        name = parts[0]
        args = parts[1:]

        cmd = COMMANDS.get(name)
        if not cmd:
            print("unk command")
            continue
        
        cmd(server, args)  
