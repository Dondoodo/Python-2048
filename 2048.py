#curses show images on terminal
import curses
#random generate random numbers
from random import randrange, choice
#collections a default value when key is not found
from collections import defaultdict

#six types of actions a player can do by pressing w a s d r q
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
#get the ASCII of the six characters including their capitals
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
#conects the input ASCII and actions
actions_dict = dict(zip(letter_codes, actions * 2))

#get the meaningful input from player
def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        #Get the ASCII of the character entered
        char = keyboard.getch()
    #return the action paired with the input character
    return actions_dict[char]
    
    #get the transpose matrix and invert matrix
def transpose(field):
    return [list(row) for row in zip(*field)]
    
def invert(field):
    return [row[::-1] for row in field]
    
class GameField(object):
    #set the initial board size, score and goal
    def __init__(self, height=4, width=4, win=2048):
        self.height = height       
        self.width = width         
        self.win_value = 2048      # Score required to win
        self.score = 0             # current score
        self.highscore = 0         # top score
        self.reset()               # reset game
        
    #put a 2 or 4 on a empty spot of the board    
    def spawn(self):
        #get a random number if >89 put a 4 on the board else put a 2 on the board
        new_element = 4 if randrange(100) > 89 else 2
        #get the coordinate of a random empty loction
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element
    
    #set the board to the initial state
    def reset(self):
        # update the highest score
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        # reset everything on board to 0 
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        #spwan a 2 or 4 twice 
        self.spawn()
        self.spawn()
    
    def move(self, direction):
    #create a move dictionary using board movement as key 
        def move_row_left(row):
            #get all the non-zero elements together
            def tighten(row):
                #add every non-zero elements into a new list
                new_row = [i for i in row if i != 0]
                #append zeros to the remaining space depending on the length of the original list
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            #merge all adjacent elements
            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        #append a new elements in the new row
                        new_row.append(2 * row[i])
                        #update the score 
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        #check if the two adjacent elements can be merged
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            #if merge, append 0 to the current location 
                            new_row.append(0)
                        else:
                            #if not merge, append the element to the new row
                            new_row.append(row[i])
                # if the new row after merge is not the same length with the old row, raise AssertionError
                assert len(new_row) == len(row)
                return new_row
            #tighten the row before merge then tighten the new row again
            return tighten(merge(tighten(row)))
        
        #use transpose and invert to transform every directions into move left
        moves = {}
        moves['Left']  = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up']    = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down']  = lambda field: transpose(moves['Right'](transpose(field)))
        #check if the direction moving is possible
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False
    
    #use the any function to determine if there is any number greater than the win value on the board
    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)

    #determine if there is no possible move left
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    #display content in the terminal
    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        help_string3 = 'Tiles with the same number merge'
        help_string4 = '  into one when they touch. '
        help_string5 = ' Move the tiles to reach 2048!'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        def cast(string):
            #using addstr()to display in the terminal
            screen.addstr(string + '\n')

        #draw horizontal seperation lines
        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            cast(line)

        #draw vertical seperation lines
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        #clear the screen
        screen.clear()
        #display current score and highscore
        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHSCORE: ' + str(self.highscore))

        #draw the game board
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()

        #show help lines on the terminal
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)
        cast('')
        cast(help_string3)
        cast(help_string4)
        cast(help_string5)
        
    #check if its possible to move towards the direction    
    def move_is_possible(self, direction):
        #check if its possible to move left in a row
        def row_is_left_movable(row):
            def change(i):
                #if there is a zero on the left and a non-zero on the right, it can move left
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                #if there are two equal adjacent non-zero numbers ,it can move left
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        check = {}
        #check if any row can move left
        check['Left']  = lambda field: any(row_is_left_movable(row) for row in field)
        #use transpose and invert to check if the matrix can move right,up or down
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up']    = lambda field: check['Left'](transpose(field))
        check['Down']  = lambda field: check['Right'](transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False
    
def main(stdscr):

    #initial state of the game
    def init():
        game_field.reset()
        return 'Game'
   
    #this is the ending scence of the game. It reads whether the player wants the restart or exit
    def not_game(state):
        #draw the game board based on settings
        game_field.draw(stdscr)
        #read the keyboard input for restart or exit
        action = get_user_action(stdscr)
        # if there is no 'Restart' or 'Exit', do nothing
        responses = defaultdict(lambda: state)   
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]
           
    #this is the current board status. It reads actions from player
    def game():
        game_field.draw(stdscr)
        # get the player action
        action = get_user_action(stdscr)
        
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):  # if move successful
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'

    state_actions = {
            'Init': init,
            'Win': lambda: not_game('Win'),
            'Gameover': lambda: not_game('Gameover'),
            'Game': game
        }
    # use the default color setting
    curses.use_default_colors()

    # display the game field and set the goal to 2048
    game_field = GameField(win=2048)


    state = 'Init'
    #start the finite-state machine
    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)
