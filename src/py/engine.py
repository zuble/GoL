import os
import sys
import random

from cell import StandardCell, ImmortalCell
#from main import seed

cols_dflt = 20
rows_dflt = 10

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
        #aliviness = 
        is_alive = (random.randint(0, 7) == 0)
        #is_immortal = (random.randint(0, 70) == 0)
        
        if self.mode == 'original':
            return StandardCell(
                is_alive=is_alive,
                alive_char='@',
                death_char='.',
            )
        else:
            if random.randint(1, 100) == 1:
                return ImmortalCell(
                    is_alive=is_alive,
                    alive_char='R',
                    death_char='.',
                )
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
    
    def get_neighbors(self, row, col):
        neighbors = []
        tmp=[]
        #print(f"\n[{row}][{col}]")
        
        for i in range(-1, 2):
            for j in range(-1, 2):
                
                if not (i == 0 and j == 0):
                    
                    if i == -1:
                        if row == 0 or row == self.rows-1:
                            #print(f"\t row [{row+i}] skipeed")
                            pass
                        
                    if j == -1:
                        if col == 0 or col == self.cols-1: 
                            #print(f"\t col [{col+j}] skipped")
                            pass 
                        
                    n_row = (row + i) % self.rows
                    n_col = (col + j) % self.cols
                    tmp.append( [n_row, n_col] )
                    neighbors.append(self.current_generation[n_row][n_col])
        #print(f"\t{tmp=}")
        return neighbors
    
    def _update_step(self, row, col):
        neighbors = self.get_neighbors(row, col)
        self.current_generation[row][col].update(neighbors) # calculate its next state
        self.current_generation[row][col].apply_update()
        
        if self.generation:
            ## Determine the cell type for the next generation
            next_cell_type = type(self.current_generation[row][col])
            ## Ensure the next cell is the correct type
            if not isinstance(self.next_generation[row][col], next_cell_type):
                print(f"MISMATCH OF CELL TYPES {self.next_generation[row][col]} {next_cell_type}")
                # Create new cell of correct type, initially dead
                self.next_generation[row][col] = next_cell_type(is_alive=False)
            
            self.next_generation[row][col].is_alive = self.current_generation[row][col].is_alive
            self.next_generation[row][col].age = self.current_generation[row][col].age
    

    ## ---------------------
    def update_generation(self):
        """Calculate the next generation"""
        if not self.generation:
            for row in range(self.rows):
                new_row = []
                for col in range(self.cols):
                    #self._update_step(row, col)
                    neighbors = self.get_neighbors(row, col)
                    self.current_generation[row][col].update(neighbors) 
                    self.current_generation[row][col].apply_update()
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
    
    
    
class GameOfLifeDisplay:
    def __init__(self):
        """Initialize display handler"""
        self.old_settings = None
        # TODO dyn according age
        self.colors = {
            'reset': 
                '\033[0m',
            'grey': 
                '\033[37m',
            'green': 
                '\033[32m',    
            'bright_green': 
                '\033[92m',
            'red': 
                #'\033[3;41m',
                '\033[31m',
            'yellow': 
                '\033[33m',
            'purple': 
                '\033[2;95m'
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
        status = f"Seed {random.seed()} | Gen {generation} | "
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