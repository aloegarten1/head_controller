import head_logic

def main():
    context = head_logic.HeadLogic("COM4", head_logic.AppMode.SCRIPT)
    context.set_script("resources\scripts\script.json")
    context.start()

if __name__  == "__main__":
    main()
