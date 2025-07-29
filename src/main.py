#!/usr/bin/env python3

import time
import os
import random
import sys

from utils import KeyboardHandler, get_value, get_seed
from cell import StandardCell

cols_dflt = 20
rows_dflt = 10

seed = get_seed()
random.seed(seed)
    
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
#if self.current_generation[row][col]:
#    # Underpopulation
#    if live_neighbors < 2: 
#        self.next_generation[row][col] = 0
#        self.death_cells[row][col] = True
#    # Equilibrium
#    elif live_neighbors in [2,3]: 
#        self.next_generation[row][col] = self.current_generation[row][col]
#    # Overpopulation
#    elif live_neighbors > 3:
#        self.next_generation[row][col] = 0
#        self.death_cells[row][col] = True
#else:
#    # Reproduction
#    if live_neighbors == 3:
#        self.next_generation[row][col] = 1
#        self.birth_cells[row][col] = True  
#    else:
#        self.next_generation[row][col] = self.current_generation[row][col]
#        
## --------------------------------------------------------------------

class GameOfLifeEngine:
    def __init__(self, mode='original', rows=None, cols=None):
        """
        Initialize the Game of Life engine
        
        :param rows: Int - Number of rows (None for auto-detect)
        :param cols: Int - Number of columns (None for auto-detect)
        """
        self.mode = mode
        self.rows = rows or self._detect_terminal_rows()
        self.cols = cols or self._detect_terminal_cols()
        if self.cols < cols_dflt:
            self.cols = cols_dflt
        if self.rows < rows_dflt:
            self.rows = rows_dflt
            
        self.current_generation = []
        self.next_generation = []
        self.generation = 0
        
        self.paused = False
        self.tsleep = 0
        
        print(f"Planet {mode}: [{self.cols} * {self.rows}]")
    
    ## ---------------------
    def _detect_terminal_rows(self):
        """Detect terminal rows"""
        try:
            return os.get_terminal_size().lines - 3
        except:
            return rows_dflt
    
    def _detect_terminal_cols(self):
        """Detect terminal columns"""
        try:  # // 2 for cell spacing
            return os.get_terminal_size().columns // 2 
        except:
            return cols_dflt
    ## ---------------------
    
    ## ---------------------
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
    ## ---------------------
    
    ## ---------------------
    def initialize_grid(self, pattern=None):
        """
        Initialize the grid with a pattern or random values
        :param pattern: Cell[][] - Optional predefined pattern of cell objects
        """
        if pattern:
            # Assume pattern is already a grid of Cell objects
            self.current_generation = [[cell for cell in row] for row in pattern]
            self.rows = len(pattern)
            self.cols = len(pattern[0]) if pattern else self.cols
        else:
            self.current_generation = self._create_random_grid()
        
    
    def _get_cell(self):
        is_alive = (random.randint(0, 7) == 0)
        
        if self.mode == 'original':
            return StandardCell(
                is_alive=is_alive,
                alive_char='@',
                death_char='.',
            )
        else:
            raise NotImplementedError
            if random.randint(1, 100) == 1:
                return ImmortalCell
            else:
                return StandardCell(
                is_alive=is_alive,
                alive_char='@',
                death_char='.',
            )

    def _create_random_grid(self):
        """Create a random grid of cell objects"""
        grid = []
        for row in range(self.rows):
            grid_row = []
            for col in range(self.cols):
                grid_row.append( self._get_cell() )
            grid.append(grid_row)
        return grid
    ## ---------------------
    
    
    def _update_step(self, row, col):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (i == 0 and j == 0):
                    n_row = (row + i) % self.rows
                    n_col = (col + j) % self.cols
                    neighbors.append(self.current_generation[n_row][n_col])
            
        self.current_generation[row][col].update(neighbors) # calculate its next state

        if self.generation:
            ## Determine the cell type for the next generation
            next_cell_type = type(self.current_generation[row][col])
            ## Ensure the next cell is the correct type
            if not isinstance(self.next_generation[row][col], next_cell_type):
                print(f"MISMATCH OF CELL TYPES {self.next_generation[row][col]} {next_cell_type}")
                # Create new cell of correct type, initially dead
                self.next_generation[row][col] = next_cell_type(is_alive=False)
        
        self.current_generation[row][col].apply_update()
        
        if self.generation:
            self.next_generation[row][col].is_alive = self.current_generation[row][col].is_alive
            self.next_generation[row][col].age = self.current_generation[row][col].age
    

    ## ---------------------
    def update_generation(self):
        """Calculate the next generation using polymorphism"""
        if not self.generation:
            for row in range(self.rows):
                new_row = []
                for col in range(self.cols):
                    self._update_step(row, col)
                    #print(f"{row}{col} {cell=}")
                    new_row.append(self.current_generation[row][col])
                self.next_generation.append(new_row)
        else:   
            for row in range(self.rows):
                for col in range(self.cols):                
                    self._update_step(row, col)
        # Swap grids
        self.current_generation, self.next_generation = self.next_generation, self.current_generation
        self.generation += 1
    ## ---------------------
    
    
    def get_grid_state(self):
        """Return current grid state"""
        return {
            'generation': self.generation,
            'grid': self.current_generation, # grid of cell objects
            'rows': self.rows,
            'cols': self.cols,
            'paused': self.paused,
            'speed': self.tsleep
        }
    
    ## ---------------------
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
    ## ---------------------
    
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
        # TODO dyn according age
        self.colors = {
            'reset': '\033[0m',
            'grey': '\033[37m',
            'green': '\033[32m',    
            'bright_green': '\033[92m',
            'red': '\033[3;41m',
            'yellow': '\033[33m'
        }

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
        Print the grid to console using polymorphic cell methods
        :param grid_state: Dict - Grid state from engine
        """
        rows = grid_state['rows']
        cols = grid_state['cols']
        grid = grid_state['grid'] # engine.current_generation grid of cell objects
        generation = grid_state['generation']
        paused = grid_state['paused']
        speed = grid_state['speed']
        
        sys.stdout.write('\033[H') # Move cursor to home
        
        
        ## -----------------------------------------
        status = f"Seed {seed} | Gen {generation} | "
        if paused:
            status += "[PAUSE] | "
        status += f"Speed {speed:.2f}s | "
        
        # Truncate/pad status to fit screen width
        max_width = cols * 2
        if len(status) > max_width:
            status = status[:max_width-3] + "..."
        else:
            status = status.ljust(max_width)
        sys.stdout.write(self.colors.get('yellow', '') + status + self.colors['reset'] + "\n")
        ## -----------------------------------------
        
        for row in range(rows):
            line = ""
            for col in range(cols):
                cell = grid[row][col]
                char = cell.get_display_char()
                color = cell.get_display_color(self)
                line += f"{color}{char}{self.colors['reset']} "
                #print(f"{color} ")
            
            # Ensure line fills the width
            target_length = cols * 2
            l = line
            for k,v in self.colors.items(): l = l.replace(v,'')
            
            current_length = len(line) - len(l) #(line.count('\033[') * 6) 
            if current_length < target_length:
                line += " " * (target_length - current_length)
            sys.stdout.write(line + "\n")
            
        sys.stdout.flush()


class GameOfLifeController:
    def __init__(self, mode='original', rows=None, cols=None):
        """
        Initialize the complete Game of Life system
        
        :param rows: Int - Grid rows
        :param cols: Int - Grid columns
        """
        self.engine = GameOfLifeEngine(
            mode=mode,
            rows=rows, 
            cols=cols
        )
        self.display = GameOfLifeDisplay()
        self.keyboard_handler = KeyboardHandler(use_thread=False) 
        self.i = 0
    
    def setup_game(self, fullscreen=False):
        """Setup the game with specified parameters"""
        if fullscreen:
            self.engine.resize_to_fullscreen()    
        self.engine.initialize_grid()
    
    def is_active(self):
        """Check if the simulation is still active"""
        return True  # For now, always return True, can add stopping conditions
    
    ## ---------------------------------------
    def _key_handler(self):
        key = self.keyboard_handler.get_key()
        if key:
            if key.lower() == 'q':
                return 0
            else:
                if key == ' ':
                    self.engine.toggle_pause()
                elif key == '+': # + speed (decrease delay)
                    self.engine.adjust_speed(-0.05)
                elif key == '-': # - speed (increase delay)
                    self.engine.adjust_speed(0.05)
                
                grid_state = self.engine.get_grid_state()
                self.display.print_grid(grid_state)
        return 1
    ## ---------------------------------------        
    
    
    def start_animation(self, delay=0.2, gens=1000, fullscreen_check=True):
        """
        Start the animation loop
        
        :param delay: Float - Delay between generations
        :param fullscreen_check: Bool - Check for terminal resize
        """
        self.engine.tsleep = delay
        
        self.keyboard_handler.start()
        
        self.display.hide_cursor()
        self.display.clear_screen()
        
        try:
            while True:    
                if not self._key_handler(): break
                
                if not self.engine.paused:
                    grid_state = self.engine.get_grid_state()
                    self.display.print_grid(grid_state)
                    
                    self.engine.update_generation()
                
                    time.sleep(self.engine.tsleep)
                    if not self._key_handler(): break
                
                ## --------
                if self.i == gens: break
                self.i =+ 1
                ## --------
                
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        finally:
            self.keyboard_handler.terminate()
            self.display.show_cursor()


def main():
    """Main function with updated class-based approach"""
    clear_console()
    use_fullscreen = input("Use fullscreen? (y/n): ").lower().startswith('y')
    
    if use_fullscreen:
        controller = GameOfLifeController(
            mode='original'
        )
        controller.setup_game(fullscreen=True)
    else:
        rows = get_value("Enter the number of rows (10-60): ", 10, 60, int)
        cols = get_value("Enter the number of cols (10-118): ", 10, 118, int)
        controller = GameOfLifeController(
            mode='original',
            rows=rows, 
            cols=cols)
        controller.setup_game()
    
    generations = get_value("Enter the number of generations (0-inf): ", 0, 100000, int)
    tsleep = get_value("Enter sleep time (0-2s): ", 0, 2, float)
    
    print("The Game of Life...")
    print("  space - Pause/Resume")
    print("  +     - Increase speed")
    print("  -     - Decrease speed")
    print("  q     - Quit")
    input("enter ...")
    
    controller.start_animation(delay=tsleep, gens=generations)

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