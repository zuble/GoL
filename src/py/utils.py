import sys
import termios
import tty
import select
import threading
import queue
import random
import os


class KeyboardHandler:
    def __init__(self, use_thread=False):
        self.input_queue = queue.Queue(maxsize=-1)
        self.running = False
        self.use_thread = use_thread
        self.thread = None
        self.old_settings = None

    def _keyboard_listener(self):
        """Background thread function to listen for keyboard input"""
        try:
            while self.running:
                if select.select([sys.stdin], [], []) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1)
                    self.input_queue.put(key)
                time.sleep(0.01)  
        except Exception as e:
            pass
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        
            
    def start(self):
        """Start the keyboard listener thread"""
        if self.use_thread:
            self.running = True
            self.thread = threading.Thread(target=self._keyboard_listener, daemon=True)
            self.thread.start()
        else:
            #if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        
    def terminate(self):
        """Stop the keyboard listener"""
        if self.thread:
            self.running = False
            self.thread.join(timeout=0.5)
        else:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_key(self):
        """Get a key from the input queue (non-blocking)"""
        if self.thread:
            # TODO
            
            try:
                #return self.input_queue.get_nowait()
                return self.input_queue.get()
            except queue.Empty:
                return 'Nada'
        else:
            if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                return sys.stdin.read(1)
            

def get_seed():
    ## https://stackoverflow.com/questions/57416925/best-practices-for-generating-a-random-seeds-to-seed-pytorch/57416967#57416967
    RAND_SIZE = 4
    random_data = os.urandom( RAND_SIZE )
    return int.from_bytes(random_data, byteorder="big")


def get_value(prompt, low, high, tipo=int):
    """Get validated user input"""
    while True:
        try:
            value = tipo(input(prompt))
        except ValueError:
            if tipo is int:
                return random.randint(low, high)
            elif tipo is float:
                return random.random()
            continue
        if value < low or value > high:
            print("Input was not inside the bounds (value <= {0} or value >= {1}).".format(low, high))
        else:
            break
    return value


def clear_console():
    """Utility function to clear console"""
    if sys.platform.startswith('win'):
        os.system("cls")
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        os.system("clear")
    else:
        print("Unable to clear terminal. Your operating system is not supported.\n\r")


