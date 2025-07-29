#!/usr/bin/env python3

import time
import os
import random
import sys
import termios
import tty
import select

from utils import KeyboardHandler

cols_dflt = 32
rows_dflt = 10

class GameOfLifeEngine:
    def __init__(self,rows=None, cols=None):
        """
        Initialize the Game of Life engine
        
        :param rows: Int - Number of rows (None for auto-detect)
        :param cols: Int - Number of columns (None for auto-detect)
        """
        self.rows = rows or self._detect_terminal_rows()
        self.cols = cols or self._detect_terminal_cols()
        if self.cols < cols_dflt:
            self.cols = cols_dflt
        if self.rows < rows_dflt:
            self.rows = rows_dflt
            
        self.current_generation = None
        self.next_generation = None
        self.birth_cells = None
        self.death_cells = None
        self.generation = 0
        self.previous_grid = None
        
        self.paused = False
        self.tsleep = 0
        
        print(f"Planet: [{self.cols} * {self.rows}]")
    
    def _detect_terminal_rows(self):
        """Detect terminal rows"""
        try:
            return os.get_terminal_size().lines - 3
        except:
            return rows_dflt
    
    def _detect_terminal_cols(self):
        """Detect terminal columns"""
        try:  # Divide by 2 for cell spacing
            return os.get_terminal_size().columns // 2 
        except:
            return cols_dflt
    
    def resize_to_fullscreen(self):
        """Resize grid to fit current terminal size"""
        self.rows = self._detect_terminal_rows()
        self.cols = self._detect_terminal_cols()
        self._resize_console()
    
    def _resize_console(self):
        """Resize the console to fit the grid"""
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            command = "\x1b[8;{rows};{cols}t".format(rows=self.rows + 3, cols=self.cols * 2)
            sys.stdout.write(command)
            sys.stdout.flush()
        else: 
            print("f msoft")
    
    def initialize_grid(self, pattern=None):
        """
        Initialize the grid with a pattern or random values
        
        :param pattern: Int[][] - Optional predefined pattern
        """
        if pattern:
            self.current_generation = [row[:] for row in pattern]
            self.rows = len(pattern)
            self.cols = len(pattern[0]) if pattern else self.cols
        else:
            self.current_generation = self._create_random_grid()
        
        self.next_generation = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.birth_cells = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.death_cells = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.generation = 0
        self.previous_grid = None
    
    
    def _create_random_grid(self):
        """Create a random grid"""
        grid = []
        for row in range(self.rows):
            grid_row = []
            for col in range(self.cols):
                grid_row.append(1 if random.randint(0, 7) == 0 else 0)
            grid.append(grid_row)
        return grid
    
    def _get_live_neighbors(self, row, col):
        """Count live neighbors with wrapping edges"""
        life_sum = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (i == 0 and j == 0):
                    life_sum += self.current_generation[((row + i) % self.rows)][((col + j) % self.cols)]
        return life_sum
    
    
    def update_generation(self):
        """Calculate the next generation"""
        
        
        self.birth_cells = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.death_cells = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        
        for row in range(self.rows):
            for col in range(self.cols):
                live_neighbors = self._get_live_neighbors(row, col)
                
                ## --------------------------------------------------------------------
                
                # Underpopulation - If a live cell has is surrounded 
                #                   by less than two surrounding neighbours
                #                   it dies and does not make it to the next generation.
                # Equilibrium -     If a live cell is surrounded 
                #                   by two or three living neighbors    
                #                   the cell stays alive and makes it to the next generation.
                # Overpopulation -  If a live cell is surrounded 
                #                   by more than three living neighbors 
                #                   the cell dies and does not make it to the next generation.
                # Reproduction -    If a dead cell is surrounded 
                #                   by three living neighbors 
                #                   the cell stays alive and makes it to the next generation.

                if self.current_generation[row][col]:
                    # Underpopulation
                    if live_neighbors < 2: 
                        self.next_generation[row][col] = 0
                        self.death_cells[row][col] = True
                    # Equilibrium
                    elif live_neighbors in [2,3]: 
                        self.next_generation[row][col] = self.current_generation[row][col]
                    # Overpopulation
                    elif live_neighbors > 3:
                        self.next_generation[row][col] = 0
                        self.death_cells[row][col] = True
                else:
                    # Reproduction
                    if live_neighbors == 3:
                        self.next_generation[row][col] = 1
                        self.birth_cells[row][col] = True  
                    else:
                        self.next_generation[row][col] = self.current_generation[row][col]
                        
                ## --------------------------------------------------------------------
                
        # Swap grids
        self.current_generation, self.next_generation = self.next_generation, self.current_generation
        self.generation += 1
    
    def is_grid_changing(self):
        """Check if grid is still evolving"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.current_generation[row][col] != self.next_generation[row][col]:
                    return True
        return False
    
    def get_grid_state(self):
        """Return current grid state"""
        return {
            'generation': self.generation,
            'grid': self.current_generation,
            'birth_cells': self.birth_cells,
            'death_cells': self.death_cells,
            'rows': self.rows,
            'cols': self.cols,
            'paused': self.paused,
            'speed': self.tsleep
        }
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
    
    def adjust_speed(self, delta):
        """Adjust simulation speed"""
        self.tsleep += delta
        if self.tsleep < 0.01:
            self.tsleep = 0.01
        elif self.tsleep > 3.0:
            self.tsleep = 3.0
        return self.tsleep
    
    def clear_console(self):
        """Clear the console"""
        if sys.platform.startswith('win'):
            os.system("cls")
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            os.system("clear")
        else:
            print("Unable to clear terminal. Your operating system is not supported.\n\r")


class GameOfLifeDisplay:
    def __init__(self):
        """Initialize display handler"""
        self.old_settings = None
        self.colors = {
            'reset': '\033[0m',
            'grey': '\033[37m',
            'green': '\033[32m',    
            'bright_green': '\033[92m',
            'red': '\033[31m',
            'yellow': '\033[33m'
        }
    
    ## --------------------------------
    def setup_keyboard_input(self):
        """Setup non-blocking keyboard input"""
        #if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
    
    def restore_keyboard_input(self):
        """Restore normal keyboard input"""
        if self.old_settings: 
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            
    def check_keyboard_input(self):
        """Check for keyboard input (non-blocking)"""
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return None
    ## --------------------------------
    
    
    ## --------------------------------
    def clear_screen(self):
        """Clear screen and move cursor to home"""
        sys.stdout.write('\033[H\033[J')
        sys.stdout.flush()
    
    def hide_cursor(self):
        """Hide cursor for smooth animation"""
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    
    def show_cursor(self):
        """Show cursor"""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    ## --------------------------------
    
    def print_grid(self, grid_state):
        """
        Print the grid to console
        
        :param grid_state: Dict - Grid state from engine
        """
        rows = grid_state['rows']
        cols = grid_state['cols']
        grid = grid_state['grid']
        birth_cells = grid_state['birth_cells']
        death_cells = grid_state['death_cells']
        generation = grid_state['generation']
        paused = grid_state['paused']
        speed = grid_state['speed']
        
        sys.stdout.write('\033[H') # Move cursor to home
        
        status = f"Gen: {generation} | "
        if paused:
            status += "[PAUSED] | "
        else:
            status += "RUNNING | "
        status += f"Speed: {speed:.2f}s | "
        status += "Controls: [SPACE]=Pause | +/-=Speed | q=Quit"
        
        # Truncate/pad status to fit screen width
        max_width = cols * 2
        if len(status) > max_width:
            status = status[:max_width-3] + "..."
        else:
            status = status.ljust(max_width)
        sys.stdout.write(status + "\n")
        
        for row in range(rows):
            line = ""
            for col in range(cols):
                if grid[row][col] == 0:
                    if death_cells[row][col]:
                        line += f"{self.colors['red']}.{self.colors['reset']} "
                    else:
                        line += f"{self.colors['grey']}.{self.colors['reset']} "
                else:
                    if birth_cells[row][col]:
                        line += f"{self.colors['bright_green']}@{self.colors['reset']} "
                    else:
                        line += f"{self.colors['green']}@{self.colors['reset']} "
            # Ensure line fills the width
            remaining_chars = (cols * 2) - len(line.replace('\033[91m', '').replace('\033[37m', '').replace('\033[0m', ''))
            if remaining_chars > 0:
                line += " " * remaining_chars
            sys.stdout.write(line + "\n")
                
            #    else:
            #        line += "@ "
            #line = line.ljust(cols * 2) # Ensure line fills the width
            #sys.stdout.write(line + "\n")
        
        sys.stdout.flush()


class GameOfLifeController:
    def __init__(self, rows=None, cols=None):
        """
        Initialize the complete Game of Life system
        
        :param rows: Int - Grid rows
        :param cols: Int - Grid columns
        """
        self.engine = GameOfLifeEngine(rows, cols)
        self.display = GameOfLifeDisplay()
        
        #from multiprocessing import Process
        #self.keyboard_handler = Process(target=KeyboardHandler()) 
        #self.keyboard_handler = KeyboardHandler() 
    
    def setup_game(self, fullscreen=False):
        """Setup the game with specified parameters"""
        if fullscreen:
            self.engine.resize_to_fullscreen()    
        self.engine.initialize_grid()
    
    def is_active(self):
        """Check if the simulation is still active"""
        return True  # For now, always return True, can add stopping conditions
    
    def start_animation(self, delay=0.2, fullscreen_check=True):
        """
        Start the animation loop
        
        :param delay: Float - Delay between generations
        :param fullscreen_check: Bool - Check for terminal resize
        """
        self.engine.tsleep = delay
        
        #self.keyboard_handler.start()
        self.display.setup_keyboard_input()
        
        self.display.hide_cursor()
        self.display.clear_screen()
        
        try:
            while True:
                ## ---------------------------------------
                #key = self.keyboard_handler.get_key()
                key = self.display.check_keyboard_input()
                #print(f"{key=}")
                if key:
                    if key.lower() == 'q':
                        break
                    elif key == ' ':
                        print(f'space {key=}')
                        self.engine.toggle_pause()
                    elif key == '+': # + speed (decrease delay)
                        print('plus')
                        self.engine.adjust_speed(-0.05)  
                    elif key == '-': # - speed (increase delay)
                        print('minus')
                        self.engine.adjust_speed(0.05)   
                    grid_state = self.engine.get_grid_state()
                    self.display.print_grid(grid_state)
                ## ---------------------------------------       
                
                if not self.engine.paused:
                    grid_state = self.engine.get_grid_state()
                    self.display.print_grid(grid_state)
                    self.engine.update_generation()
                    time.sleep(self.engine.tsleep)
                
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        finally:
            #self.keyboard_handler.terminate()
            self.display.restore_keyboard_input()
            self.display.show_cursor()


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

def main():
    """Main function with updated class-based approach"""
    clear_console()
    use_fullscreen = input("Use fullscreen? (y/n): ").lower().startswith('y')
    
    if use_fullscreen:
        controller = GameOfLifeController()
        controller.setup_game(fullscreen=True)
    else:
        rows = get_value("Enter the number of rows (10-60): ", 10, 60, int)
        cols = get_value("Enter the number of cols (10-118): ", 10, 118, int)
        controller = GameOfLifeController(rows, cols)
        controller.setup_game()
    
    generations = get_value("Enter the number of generations (0-inf): ", 0, 100000, int)
    tsleep = get_value("Enter sleep time (0-2s): ", 0, 2, float)
    
    print("The Game of Life...")
    #print("  SPACE - Pause/Resume")
    #print("  +     - Increase speed")
    #print("  -     - Decrease speed")
    #print("  q     - Quit")
    input("enter ...")
    
    controller.start_animation(delay=tsleep)


def clear_console():
    """Utility function to clear console"""
    if sys.platform.startswith('win'):
        os.system("cls")
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        os.system("clear")
    else:
        print("Unable to clear terminal. Your operating system is not supported.\n\r")


if __name__ == "__main__":
    main()