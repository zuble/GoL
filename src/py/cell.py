import abc

class Cell(abc.ABC):
    """Abstract base class for all cell types."""
    def __init__(self, is_alive=False, **kwargs):
        self.is_alive = is_alive
        self.age = 0
        
        if is_alive:
            self.was_born_this_gen = True
        else:
            self.was_born_this_gen = False
        self.was_alive_last_gen = False
        self.died_this_gen = False
        
        # Store the next state calculated during update
        self._next_state = None 
        self._next_age = None

    @abc.abstractmethod
    def update(self, neighbors):
        """ Calculate the cell's next state based on neighbors.
            Must set self._next_state and self._next_age.
        """
        pass

    @abc.abstractmethod
    def get_display_char(self):
        """Return the character to display for this cell."""
        pass

    @abc.abstractmethod
    def get_display_color(self, display_handler):
        """Return the ANSI color code for this cell using the display handler."""
        pass
    
    
    def apply_update(self):
        """Apply the calculated next state."""
        #print(f"apply_update: {self._next_state=}")
        if self._next_state is not None:
            self.is_alive = self._next_state
        if self._next_age is not None:
            self.age = self._next_age
        #print(f"apply_update: {self.is_alive=}\n")
        # Reset for next cycle , always set in update
        #self._next_state = None
        #self._next_age = 0


    def die(self):
        """Mark the cell to die in the next state."""
        self._next_state = False
        self._next_age = 0

    def revive(self):
        """Mark the cell to revive in the next state."""
        self._next_state = True
        # Age logic can be customized in subclasses or here
        self._next_age = getattr(self, 'age', 0) + 1 


class StandardCell(Cell):
    """Standard Conway's Game of Life cell."""
    def __init__(self, is_alive=False, alive_char='@', death_char='.', **kwargs):
        
        super().__init__(is_alive=is_alive, **kwargs) 
        
        self.alive_char = alive_char
        self.death_char = death_char
            
    def update(self, neighbors):
        live_neighbors = sum(1 for n in neighbors if n.is_alive)
        #print(f"update: {live_neighbors=}")
        #print(f"update: {self.is_alive=}")
        
        if self.is_alive:
            # Underpopulation
            if live_neighbors < 2: 
                self._next_state = False 
                self._next_age = 0
                self.died_this_gen = True 
            # Equilibrium
            elif live_neighbors in [2,3]: 
                self._next_state = True  
                self._next_age = self.age + 1
                self.died_this_gen = False
            # Overpopulation
            elif live_neighbors > 3: 
                self._next_state = False 
                self._next_age = 0
                self.died_this_gen = True   
                
            self.was_born_this_gen = False
            self.was_alive_last_gen = True
        else:
            # Reproduction
            if live_neighbors == 3: 
                self._next_state = True
                self.was_born_this_gen = True
            else:
                self._next_state = False 
                self.was_born_this_gen = False

            self._next_age = 0
            self.was_alive_last_gen = False
            self.died_this_gen = False
    
    
    # assumes that those are called after apply_update
    def get_display_char(self):
        return self.alive_char if self.is_alive else self.death_char

    # TODO increase color patterns logic
    def get_display_color(self, display_handler):
        
        if not self.is_alive:
            if self.was_alive_last_gen: # self.died_this_gen
                return display_handler.colors.get('red', '')
        
            return display_handler.colors.get('grey', '')
        else:
            if self.was_born_this_gen: 
                return display_handler.colors.get('bright_green', '')
            
            if self.age > 10:
                return display_handler.colors.get('dark_green', display_handler.colors['green'])
            
            return display_handler.colors.get('green', '')



# TODO
class ImmortalCell(Cell):
    """A cell type that never dies once born."""
    def __init__(self, is_alive=False, alive_char='I', death_char='.', **kwargs):
        
        super().__init__(is_alive=is_alive, **kwargs) 
    
        self.alive_char = alive_char
        self.death_char = death_char
        
    def update(self, neighbors):
        live_neighbors = sum(1 for n in neighbors if n.is_alive)
        self._next_age = self.age + 1
        if self.is_alive:
            self._next_state = True # Never dies
        else:
            if live_neighbors == 3:
                self._next_state = True # Can be born
                self._next_age = 0
            else:
                self._next_state = False

    def get_display_char(self):
        return self.alive_char if self.is_alive else self.death_char
    
    def get_display_color(self, display_handler):
        if self.is_alive:
            # Example: Blue for immortal, cyan if newly born
            #if getattr(self, 'was_born_this_gen', False):
            #    return display_handler.colors.get('cyan', '')
            return display_handler.colors.get('yellow', '')
        else:
            #if getattr(self, 'was_alive_last_gen', False): 
            #    return display_handler.colors.get('red', '') 
            return display_handler.colors.get('grey', '')
