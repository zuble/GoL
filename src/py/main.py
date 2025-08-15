#!/usr/bin/env python3

import time
import random

from utils import KeyboardHandler, get_value, get_seed, clear_console
from engine import GameOfLifeEngine, GameOfLifeDisplay


#seed = get_seed()
seed = 2094158199
random.seed(seed)


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
    
    
    def start(self, delay=0.2, gens=1000, fullscreen_check=True):
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
    mode = input('mode original (y/n)').lower().startswith('y')
    
    if use_fullscreen:
        controller = GameOfLifeController(
            mode='original' if mode else 'other'
        )
        controller.setup_game(fullscreen=True)
    else:
        rows = get_value("Enter the number of rows (10-60): ", 10, 60, int)
        cols = get_value("Enter the number of cols (10-118): ", 10, 118, int)
        controller = GameOfLifeController(
            mode='original' if mode else 'other',
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
    
    controller.start(delay=tsleep, gens=generations)


if __name__ == "__main__":
    main()
