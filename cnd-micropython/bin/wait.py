import time

def __main__(args):
    if len(args) < 3:
        print ("Usage: wait <seconds>")
        return

    time.sleep(int(args[2]))


