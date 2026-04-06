from .commands import COMMANDS

def run_cli(server):
    while True:
        try:   
            parts = input(">> ").strip().split()
            if not parts:
                continue
            
            name = parts[0]
            args = parts[1:]

            cmd = COMMANDS.get(name)
            if not cmd:
                print("unknown command (type 'help')")
                continue

            cmd(server, args)

        except KeyboardInterrupt:
             print("\nuse 'exit' to quit")
        except Exception as e:
            print(f"error: {e}")  
