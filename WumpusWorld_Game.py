import pygame
import pygame_gui
import random
from map_cell import *
import queue
import heapq
import copy
from itertools import chain
import time
import math
from bitarray import bitarray
import copy
import math
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** GAME WINDOW INITIALIZATION  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
WIN_X = 900
WIN_Y = 600
GAME_X = WIN_Y
pygame.init()
pygame.display.set_caption('WUMPUS WORLD GAME')
WINDOW = pygame.display.set_mode((WIN_X, WIN_Y))
background = pygame.Surface((WIN_X, WIN_Y))

foreground = pygame.Surface((WIN_X, WIN_Y))
# background.fill(WHITE)
manager = pygame_gui.UIManager((WIN_X, WIN_Y))
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** GLOBAL VARIABLES  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
D_MOD = 2
CLICKED_POS = (-1, -1)
LAST_CLICKED = CLICKED_POS
NUM_SELECTED = 0 # Keeps track of the number of each unit type ==> 0:Mage, 1:WUMP, 2:HERO (player side)
# QUEUE TO KEEP TRACK OF CONSECUTIVE SELECTS
PLAYER_SELECTIONS = queue.Queue(3)
PLAYER_NUM_UNITS = 0
UNITS = [D_MOD] * 3
print(UNITS)
CPU_NUM_UNITS = 0
VICTORY_TEXT = "Game In Progress..."
p_queue = []
heapq.heapify(p_queue)
FOG = True
FRESH = True


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** GAME GRID FUNCTIONS  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Grid:
    def __init__(self, dimension_mod):
        self.axis_dim = 3*dimension_mod
        self.grid = [[None for _ in range(
            self.axis_dim)] for _ in range(self.axis_dim)]


    def copy(self):
        output_grid=[[None for _ in range(self.axis_dim)]for _ in range(self.axis_dim)]
        for i in range(self.axis_dim):
            for j in range(self.axis_dim):
                output_grid[j][i]=self.grid[j][i].copy()
        return output_grid
# --------------------------------------------------------------------
    def init_grid(self):
        global PLAYER_NUM_UNITS
        global CPU_NUM_UNITS
        gap = GAME_X // self.axis_dim
        print(self.axis_dim/3-1)
        total_spots = list(range(0, self.axis_dim))
        hole_locations = []
        # row
        for i in range(self.axis_dim):
            self.grid.append([])

            if(i != 0 and i != self.axis_dim-1):
                # CHANGE THIS BASED ON WHAT THE PROFESSOR SAYS FOR NUMBER OF PITS
                hole_locations = random.sample(
                    total_spots, int(self.axis_dim/3-1))
            # column
            for j in range(self.axis_dim):
                if(i == 0):
                    cell = Cell(j, i, gap, self.axis_dim, Ctype(((j+1) % 3)+4))
                    PLAYER_NUM_UNITS += 1
                elif(i == self.axis_dim-1):
                    cell = Cell(j, i, gap, self.axis_dim, Ctype(((j+1) % 3)+1))
                    CPU_NUM_UNITS += 1
                else:
                    cell = Cell(j, i, gap, self.axis_dim, Ctype.EMPTY)
                self.grid[j][i] = cell
            for k in hole_locations:
                if(i != 0 and i != self.axis_dim-1):
                    self.grid[k][i].set_ctype(Ctype.HOLE)

        holes_in_row=int(self.axis_dim/3-1)
        for i in range(self.axis_dim):
            for j in range(self.axis_dim):
                if i==self.axis_dim-1:
                    if j%3==0:
                        self.grid[j][i].set_probabilities(0,1,0,0)
                    elif j%3==1:
                        self.grid[j][i].set_probabilities(0,0,1,0)
                    elif j%3==2:
                        self.grid[j][i].set_probabilities(0,0,0,1)
                elif i!=0:
                    self.grid[j][i].set_probabilities(holes_in_row/self.axis_dim,0,0,0)
        #print(self.grid[0][5])
        return self.grid
# --------------------------------------------------------------------
    # Resets the game, keeps the current hole locations
    def reset_grid(self):
        global PLAYER_NUM_UNITS
        global CPU_NUM_UNITS
        global VICTORY_TEXT
        VICTORY_TEXT = "Game In Progress. . . "
        PLAYER_NUM_UNITS=self.axis_dim
        CPU_NUM_UNITS=self.axis_dim
        # row
        for i in range(self.axis_dim):
            #column
            for j in range(self.axis_dim):
                if(i == 0):
                    self.grid[j][i].ctype=Ctype(((j+1) % 3)+4)

                elif(i == self.axis_dim-1):
                    self.grid[j][i].ctype=Ctype(((j+1) % 3)+1)
                else:
                    if(self.grid[j][i].ctype!=Ctype.HOLE):
                        self.grid[j][i].ctype=Ctype.EMPTY
        self.draw_map()
# --------------------------------------------------------------------
    def generate_grid(self,dimension_mod):
        global PLAYER_NUM_UNITS
        global CPU_NUM_UNITS
        global UNITS
        PLAYER_NUM_UNITS=0
        CPU_NUM_UNITS=0
        self.axis_dim=3*dimension_mod
        UNITS=[dimension_mod]*3
        self.grid=None
        self.grid = [[None for _ in range(self.axis_dim)] for _ in range(self.axis_dim)]
        background.fill((0,0,0))
        self.init_grid()
        self.draw_map()

# --------------------------------------------------------------------

    def convert_string_board(self, str_board):
        for i in range(self.axis_dim):
            for j in range(self.axis_dim):
                x = str_board[i][j]
                if x == 'PM':
                    self.grid[i][j].ctype = 1#MAGE
                elif x == 'PW':
                    self.grid[i][j].ctype = 2#WUMPUS
                elif x == 'PK':
                    self.grid[i][j].ctype = 3#KNIGHT
                elif x == 'CM':
                    self.grid[i][j].ctype = 4#CPUMAGE
                elif x == 'CW':
                    self.grid[i][j].ctype = 5#CPUWUMPUS
                elif x == 'CK':
                    self.grid[i][j].ctype = 6#CPUKNIGHT
                elif x == 'H':
                    self.grid[i][j].ctype = 7#HOLE
                elif x == '-':
                    self.grid[i][j].ctype = 8#EMPTY
        self.draw_map()

# --------------------------------------------------------------------
    def gen_string_board(self):
        string_board=[[None for _ in range(self.axis_dim)] for _ in range(self.axis_dim)]
        for i in range(self.axis_dim):
            for j in range(self.axis_dim):
                x=self.grid[i][j].ctype
                if(x==1):
                    string_board[i][j]=('PM')
                elif(x==2):
                    string_board[i][j]=('PW')
                elif(x==3):
                    string_board[i][j]=('PK')
                elif(x==4):
                    string_board[i][j]=('CM')
                elif(x==5):
                    string_board[i][j]=('CW')
                elif(x==6):
                    string_board[i][j]=('CK')
                elif(x==7):
                    string_board[i][j]=('H')
                elif(x==8):
                    string_board[i][j]=('-')
        return string_board
# --------------------------------------------------------------------
    def draw_map(self):
        gap = GAME_X//self.axis_dim
        # print(gap)
        win = background
        for row in self.grid:
            for cell in row:
                cell.set_fog(FOG)

                if(1<=cell.ctype<=3):
                    get_observations(cell, grid, False)
                if(4<=cell.ctype<=6):
                    get_observations(cell, grid, True)
                cell.draw(win)
        pygame.display.update()
# --------------------------------------------------------------------

    # SET COLOR OF A PARTICULAR CELL IN GRID
    # def set_cell_color(self, col, row, color):
    #     self.grid[col][row].set_color(color)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** END GRID FUNCTIONS  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** GLOBAL FUNCTIONS  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_clicked_pos(grid, position):
    gap = GAME_X // grid.axis_dim
    x, y = position
    row = y // gap
    col = x // gap
    return col, row


def clear_selected():
    global PLAYER_SELECTIONS
    global NUM_SELECTED
    while not PLAYER_SELECTIONS.empty():
        cell = PLAYER_SELECTIONS.get()
        print(f"Removing: '{cell.get_type_text()}' from list")
        cell.selected = False
        cell.draw(background)
    NUM_SELECTED = 0


def update_selected(cell):
    global NUM_SELECTED
    cell.selected = True
    cell.draw(background)
    #pygame.display.update()
    NUM_SELECTED += 1
    PLAYER_SELECTIONS.put(cell)
    #print(f"SELECTED CELL :: {CLICKED_POS}  {cell.get_type_text()})")


def player_move_unit(grid, event):
    global LAST_CLICKED
    global CLICKED_POS
    global NUM_SELECTED
    global PLAYER_SELECTIONS
    global PLAYER_NUM_UNITS
    global CPU_NUM_UNITS
    global VICTORY_TEXT
    global UNITS
    # Get the row and column of the clicked positin on game board
    if event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        col, row = get_clicked_pos(grid, pos)
        # Excludes positions outside of board dimensions
        if col < grid.axis_dim and row < grid.axis_dim:
            CLICKED_POS = (col, row)
            cell = grid.grid[col][row]
            # SELECT & DESELECT A CELL
            #  -- MAX 2 SELECTED
            if cell.selected == True:
                cell.selected = False
                cell.draw(background)
                NUM_SELECTED -= 1
                PLAYER_SELECTIONS.get()
            elif cell.selected == False and NUM_SELECTED < 2:
                #get_observations(cell, grid, False)
                if NUM_SELECTED == 0 and (1 <= cell.ctype <= 3):
                    update_selected(cell)
                    #get_neighbors(cell,grid, True)
                elif NUM_SELECTED == 0 and (4 <= cell.ctype <= 8):
                    print("Please select a friendly piece first!")
                elif NUM_SELECTED > 0 and (4 <= cell.ctype <= 8):
                    update_selected(cell)
            #print(f"Num selected = {NUM_SELECTED}")


            if NUM_SELECTED == 2:
                #print("CONFIRMED MOVE")
                #cell.draw(background)
                # Get the two cells from the queue
                p_piece = PLAYER_SELECTIONS.get()
                p_piece=grid.grid[p_piece.col][p_piece.row]
                p_piece.selected = False
                NUM_SELECTED -=1
                t_piece = PLAYER_SELECTIONS.get()
                t_piece=grid.grid[t_piece.col][t_piece.row]
                t_piece.selected = False
                NUM_SELECTED -=1

                code=p_piece.fight(t_piece)
                #print(f'Code:{code}')
                # No battle, swap cells
                if code==0:
                    temp_type = t_piece.ctype
                    t_piece.ctype = p_piece.ctype
                    p_piece.ctype = temp_type
                # Invalid move
                if code==-3:
                    pass
                # both pieces die
                elif code==-2:
                    UNITS[p_piece.ctype-1] -= 1 # Decrements the amount of units of a particular type
                    #print(f'UNITS: {UNITS}')
                    t_piece.ctype=Ctype.EMPTY
                    p_piece.ctype=Ctype.EMPTY
                    PLAYER_NUM_UNITS -= 1
                    CPU_NUM_UNITS -= 1
                # t_piece dies
                elif code==1:
                    # code to subtract from total pieces here
                    CPU_NUM_UNITS -= 1
                    t_piece.ctype=p_piece.ctype
                    p_piece.ctype=Ctype.EMPTY
                # p_piece dies
                elif code==-1:
                    #print('here')
                    UNITS[p_piece.ctype-1] -= 1
                    #print(f'UNITS: {UNITS}')
                    p_piece.ctype=Ctype.EMPTY
                    print(p_piece)
                    PLAYER_NUM_UNITS -= 1
                elif code==-4:
                    print('Probably a bug?')



                t_piece.draw(background)
                p_piece.draw(background)


                grid.grid=calculate_prob(grid)
                #grid.grid=calculate_observations(grid)

                str_board=grid.gen_string_board()
                grid.convert_string_board(str_board)
                pygame.display.update()
                #print(f'cpu pieces:{PLAYER_NUM_UNITS}')
                #print(f'player pieces:{CPU_NUM_UNITS}')


                #print(f"PLAYER PIECES ({PLAYER_NUM_UNITS}) ---- CPU PIECES ({CPU_NUM_UNITS})")


                VICTORY_TEXT = check_win()



                 # A method to check if the player or the cpu won should go here
                str_board=grid.gen_string_board()
                #print_string_board(str_board)

                #----- TESTING OBSERVATION ---------

                #-----------------------------------

                grid.draw_map()
                grid.grid=calculate_observations(grid)

                # x=alphabeta((str_board,CPU_NUM_UNITS,PLAYER_NUM_UNITS),2,float('inf'),float('-inf'),True)
                # PLAYER_NUM_UNITS=x[1][2]
                # CPU_NUM_UNITS=x[1][1]
                # #print('end')
                # #print(h_val(x[1],True))
                #
                # print("CHOSEN MOVE:")
                # print_string_state(x)
                #
                # grid.convert_string_board(x[1][0])
                VICTORY_TEXT = check_win()

                #update_probs(grid)
                return
            else:
                print("select another to move")

def is_terminal(node):
    if(node[1]==0):
        return True
    elif(node[2]==0):
        return True
    return False



# Reads the string board and returns the  coordinate pairs of the pieces of the current player
def get_piece_list(str_grid, maximizingPlayer):
    pieces=list()
    #col
    for i in range(grid.axis_dim):
        #range
        for j in range(grid.axis_dim):
            if(maximizingPlayer):

                if str_grid[i][j][0]=='C':
                    pieces.append([i,j])
            else:
                if str_grid[i][j][0]=='P':
                    pieces.append((i,j))
    return pieces

# Gets the cells around the piece that have valid moves
# --> If the cell has a pit, we assume that it's a bad move and don't add it to the list
# --> Depending on if the turn is maximizingPlayer or not, add cells containing enemy units but ignore friendly units
# def get_neighbors(cell, grid, maximizingPlayer):
#     global D_MOD
#     neighbors = []
#     board_size = D_MOD * 3
#     for j in range(3):
#         for i in range(3):
#             #print(f'{cell.col-1+i}, {cell.row-1+j}')
#             if(i == 1 and j == 1): # the current cell is self, don't check
#                 continue
#             if(cell.col-1+i > board_size -1 or cell.col-1+i < 0 or cell.row-1+j > board_size -1 or cell.row-1+j < 0):
#                 #print(f"({i},{j}) OUT OF BOUNDS")
#                 continue
#             if(grid.grid[cell.col-1+i][cell.row-1+j].ctype == Ctype.HOLE):
#                 #print(f"({i},{j}) IS A HOLE")                                        #------------- THIS MIGHT NEED OPTIZING ------------------
#                 continue
#             #Check maximizingPlayer:
#             # Assume player is maximizingPlayer
#             if not maximizingPlayer:
#                 if 1 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 3:
#                     #print(f"({i},{j}) IS A MAXimizingPlayer FRIENDLY PIECE (ignore)")
#                     continue
#             else:
#                 if 4 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 6:
#                     #print(f"({i},{j}) IS A MINImizingPlayer FRIENDLY PIECE (ignore)")
#                     continue
#             #print(f"({i},{j}) is VALID")
#             neighbors.append(grid.grid[cell.col-1+i][cell.row-1+j])
#     return neighbors

def get_neighbors(cell, grid):
    global D_MOD
    neighbors = []
    board_size = D_MOD * 3
    for j in range(3):
        for i in range(3):
            #print(f'{cell.col-1+i}, {cell.row-1+j}')
            if(i == 1 and j == 1): # the current cell is self, don't check
                continue
            if(cell.col-1+i > board_size -1 or cell.col-1+i < 0 or cell.row-1+j > board_size -1 or cell.row-1+j < 0):
                #print(f"({i},{j}) OUT OF BOUNDS")
                continue
            # if(grid.grid[cell.col-1+i][cell.row-1+j].p_hole==1 or grid.grid[cell.col-1+i][cell.row-1+j].p_mage==1 or grid.grid[cell.col-1+i][cell.row-1+j].p_wumpus==1 or grid.grid[cell.col-1+i][cell.row-1+j].p_hero==1):
            #     continue
            if 4 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 6:
                continue
            #print(f"({i},{j}) is VALID")
            neighbors.append(grid.grid[cell.col-1+i][cell.row-1+j])
    return neighbors


def get_neighbors_string(pair, array, maximizingPlayer):
    global D_MOD
    col = pair[0]
    row = pair[1]
    neighbors = []
    board_size = D_MOD * 3
    for j in range(3):
        for i in range(3):
            #print(f'{cell.col-1+i}, {cell.row-1+j}')
            if(i == 1 and j == 1): # the current cell is self, don't check
                continue
            if(col-1+i > board_size -1 or col-1+i < 0 or row-1+j > board_size -1 or row-1+j < 0):
                #print(f"({i},{j}) OUT OF BOUNDS")
                continue
            if(array[col-1+i][row-1+j] == 'H'):
                #print(f"({i},{j}) IS A HOLE")                                        #------------- THIS MIGHT NEED OPTIZING ------------------
                continue
            #Check maximizingPlayer:
            # Assume player is maximizingPlayer
            if not maximizingPlayer:
                #if 1 <= array[cell.col-1+i][cell.row-1+j].ctype <= 3:
                if array[col-1+i][row-1+j][0] == 'P':
                    #print(f"({i},{j}) IS A MAXimizingPlayer FRIENDLY PIECE (ignore)")
                    continue
            else:
                #if 4 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 6:
                if array[col-1+i][row-1+j][0] == 'C':
                    #print(f"({i},{j}) IS A MINImizingPlayer FRIENDLY PIECE (ignore)")
                    continue
            #print(f"({i},{j}) is VALID")
            #neighbors.append((array[col-1+i][row-1+j],col-1+i,row-1+j))
            neighbors.append((col-1+i,row-1+j))
    return neighbors

# POPULATES ARRAY WITH ADJACENT CELLS TO GET OBSERVATIONS FOR THE GIVEN CELL
# Get observation of unit's surroundings
#   PIT (3)--> Breeze
#   WUMPUS (1)--> Stench
#   HERO (2)--> Sound
#   MAGE (0) --> Heat
def get_observations(cell, grid, maximizingPlayer):
    global D_MOD
    neighbors = []
    board_size = D_MOD * 3
    bitarr = bitarray(4)
    bitarr.setall(0)
    for j in range(3):
        for i in range(3):
            #print(f'{cell.col-1+i}, {cell.row-1+j}')

            if(i == 1 and j == 1): # the current cell is self, don't check
                continue
            if(cell.col-1+i > board_size -1 or cell.col-1+i < 0 or cell.row-1+j > board_size -1 or cell.row-1+j < 0):
                #print(f"({i},{j}) OUT OF BOUNDS")
                continue
            if(grid.grid[cell.col-1+i][cell.row-1+j].ctype == Ctype.HOLE):
                #print(f"({i},{j}) IS HOLE")
                bitarr[3] = 1
            #Check maximizingPlayer:
            # Assume player is maximizingPlayer
            type = grid.grid[cell.col-1+i][cell.row-1+j].ctype
            if maximizingPlayer:
                if 1 <= type <= 3:
                    #print(f"({i},{j}) IS A MAXimizingPlayer FRIENDLY PIECE (ignore)")
                    bitarr[type-1] = 1
            else:
                if 4 <= type <= 6:
                    #print(f"({i},{j}) IS A MINImizingPlayer FRIENDLY PIECE (ignore)")
                    bitarr[type-4] = 1
            #print(f"({i},{j}) is VALID")

            #neighbors.append(grid.grid[cell.col-1+i][cell.row-1+j])
    #print(bitarr)
    cell.set_observation(bitarr)
    return bitarr


# Performs a swap on the pieces for the scenario where coord1 moves to coord2 and beats the unit at coord2
def win_swap(coord1,coord2,array):
    array[coord2[0]][coord2[1]]=array[coord1[0]][coord1[1]]
    array[coord1[0]][coord1[1]]='-'
    return array

# Performs a swap on the pieces for the scenario where coord1 moves to coord2 and loses to the unit at coord2
def loss_swap(coord1,coord2,array):
    array[coord1[0]][coord1[1]]='-'
    return array

# Swaps coord1 and coord2
def swap(coord1,coord2,array):
    temp=array[coord1[0]][coord1[1]]
    array[coord1[0]][coord1[1]]=array[coord2[0]][coord2[1]]
    array[coord2[0]][coord2[1]]=temp
    return array

#returns the board state created by moving the piece at coord1 to coord2
def get_child_state(coord1,coord2,node,maximizingPlayer):
    array=copy.deepcopy(node[0])
    cpu_pieces=node[1]
    p_pieces=node[2]
    c1_type=array[coord1[0]][coord1[1]]
    c2_type=array[coord2[0]][coord2[1]]
    if(c2_type[0]=='-'):
        array=swap(coord1,coord2,array)
    else:
        winner=string_fight(c1_type,c2_type)
        if winner==-2:
            cpu_pieces-=1
            p_pieces-=1
            array[coord2[0]][coord2[1]]='-'
            array[coord1[0]][coord1[1]]='-'
        elif maximizingPlayer:
            if winner==1:
                p_pieces-=1
                array=win_swap(coord1,coord2,array)
            elif winner==-1:
                array=loss_swap(coord1,coord2,array)
                cpu_pieces-=1
        elif not maximizingPlayer:
            if winner==1:
                cpu_pieces-=1
                array=win_swap(coord1,coord2,array)
            elif winner==-1:
                array=loss_swap(coord1,coord2,array)
                p_pieces-=1
        else:
            print('error?')
    return (array,cpu_pieces,p_pieces)



# Simulates piece 1 landing on top of piece 2 on the string_grid
# returns 1 if piece1 wins and -1 piece 2 wins, and -2 if both die
# Returns 0 if there is an error, probably
def string_fight(piece1,piece2):
    p1_type=piece1[1]
    p2_type=piece2[1]
    if p1_type==p2_type:
        return -2
    if p1_type=='M':
        if p2_type=='K':
            return 1
        elif p2_type=='W':
            return -1
    if p1_type=='K':
        if(p2_type=='M'):
            return -1
        elif p2_type=='W':
            return 1
    if p1_type=='W':
        if p2_type=='M':
            return 1
        elif p2_type=='K':
            return -1
    print('ERROR IN STRING_FIGHT')
    return 0

def print_string_board(board):
    global D_MOD
    #print("-----------------------------------")
    #print("BOARD STATE:")
    for i in range(3 * D_MOD):
        print('\n')
        for j in range(3 * D_MOD):
            print(board[j][i], end = '\t')
    print("\n")

def print_string_state(state):
    print("-----------------------------------\nBOARD STATE:")
    print(f"HVAL: {h_val(state[1],True)}")

    print(f"PIECES: {state[1][1]},{state[1][2]}")
    print_string_board(state[1][0])
    print("-----------------------------------")




# Check if the game has ended
# Returns:
# 0 if tie
# 1 if player wins
# -1 if cpu wins
# 2 if game is still on
def check_win():
    if(PLAYER_NUM_UNITS==CPU_NUM_UNITS==0):
        print('Tie')
        return 'Tie'
    elif(PLAYER_NUM_UNITS==0):
        print('CPU Wins')
        return 'CPU Wins'
    elif(CPU_NUM_UNITS==0):
        print('Player Wins')
        return 'Player Wins'
    return "Game In Progress..."

def update_probs(grid):
    global FRESH
    test_cell = grid.grid[0][5]
    if FRESH:
        neighbors = get_neighbors(test_cell, grid, False)
        print(f"#neighbors = {len(neighbors)}")
        print(neighbors)
        for n in neighbors:
            n.p_wumpus = 1/len(neighbors)
        #FRESH = False
    else:
        pass

# TEST FUNCTION FOR PROBABILITY DIST
def prob_dist(grid):
    global FRESH
    test_cell = grid.grid[0][5]
    prob = 0
    neighbors = get_neighbors(test_cell, grid, True)

    #print(neighbors)
    prob += (1-1/6)*test_cell.p_wumpus
    for n in neighbors:
        prob += n.p_wumpus * 1/(6*len(neighbors))
        #print(n.p_wumpus)
    print(prob)
    return prob


def calculate_prob(grid):
    global D_MOD
    global FRESH
    output_grid=grid.copy()
    w_prob=0
    m_prob=0
    h_prob=0
    p_prob=0
    axis_dim = 3*D_MOD
    for i in range(axis_dim):
        for j in range(axis_dim):
            temp_cell=grid.grid[i][j]
            w_prob = (1-(1/PLAYER_NUM_UNITS)) * grid.grid[i][j].p_wumpus
            m_prob = (1-(1/PLAYER_NUM_UNITS)) * grid.grid[i][j].p_mage
            h_prob = (1-(1/PLAYER_NUM_UNITS)) * grid.grid[i][j].p_hero
            p_prob = grid.grid[i][j].p_hole
            neighbors=get_neighbors(temp_cell,grid)
            #print(neighbors)
            if temp_cell.p_wumpus==1 or temp_cell.p_mage==1 or temp_cell.p_hero==1 or temp_cell.p_hole==1:
                output_grid[i][j].set_probabilities(p_prob,w_prob,h_prob,m_prob)
                w_prob=0
                m_prob=0
                h_prob=0
                p_prob=0
                continue
            for n in neighbors:
                # if FRESH:
                #     n.p_wumpus = 1/len(neighbors)
                #     n.p_mage = 1/len(neighbors)
                #     n.p_hero = 1/len(neighbors)
                w_prob += n.p_wumpus * 1/(PLAYER_NUM_UNITS*(len(get_neighbors(n,grid))))
                m_prob += n.p_mage * 1/(PLAYER_NUM_UNITS*(len(get_neighbors(n,grid))))
                h_prob += n.p_hero * 1/(PLAYER_NUM_UNITS*(len(get_neighbors(n,grid))))
            output_grid[i][j].set_probabilities(p_prob,w_prob,h_prob,m_prob)
            w_prob=0
            m_prob=0
            h_prob=0
            p_prob=0
    FRESH = False
    #print("got to output grid")
    return output_grid

#returns array of observation probabilities for each type
# 0:Mage, 1:WUMP, 2:Hero, 3:Pit
def calculate_PO(grid,cell):
    prob_array = [0.0,0.0,0.0,0.0]
    neighbors = get_neighbors(cell, grid)
    #print(neighbors)
    for n in neighbors:
        for i in range(4):
            if i == 0:
                prob_array[i] = prob_array[i] + n.p_mage
            if i == 1:
                prob_array[i] = prob_array[i] + n.p_wumpus
            if i == 2:
                prob_array[i] = prob_array[i] + n.p_hero
            if i == 3:
                prob_array[i] = prob_array[i] + n.p_hole
    return prob_array

# 0:Mage, 1:WUMP, 2:Hero, 3:Pit
def calculate_PO2(grid,cell):
    prob_array = [0.0,0.0,0.0,0.0]
    neighbors = get_neighbors(cell, grid)
    #print(neighbors)
    for n in neighbors:
        if n.observe_array[0]==1 and 4<=n.ctype<=6:
            prob_array[0] = prob_array[0] + cell.p_mage
        elif n.observe_array[1]==1 and 4<=n.ctype<=6:
            prob_array[1] = prob_array[1] + cell.p_wumpus
        elif n.observe_array[2]==1 and 4<=n.ctype<=6:
            prob_array[2] = prob_array[2] + cell.p_hero
        elif n.observe_array[3]==1 and 4<=n.ctype<=6:
            prob_array[3] = prob_array[3] + cell.p_hole
    print(prob_array)
    return prob_array

# 0:Mage, 1:WUMP, 2:Hero,
# Currently skipping pit because the logic for pit is slightly different
def calc_po3(grid):
    pits_per_row=[grid.axis_dim/3-1]*len(grid.grid)
    pits_per_row[0]=0
    pits_per_row[len(grid.grid)-1]=0
    cpu_pieces=get_cpu_pieces(grid)
    player_pieces=[UNITS[0],UNITS[1],UNITS[2]]
    #print(player_pieces)
    all_neighbors=list()
    string_board=[['.' for _ in range(len(grid.grid))] for _ in range(len(grid.grid[0]))]
    for i in cpu_pieces:
        string_board[i.col][i.row]=i.get_type_text()
        current_neighbors=get_neighbors(i,grid)
        all_neighbors=list(set().union(all_neighbors,current_neighbors))
    #all neighbors contains list of all neighbors, removing cpu_pieces and duplicates
    for n in all_neighbors:
        string_board[n.col][n.row]='-'
    output_grid=grid
    output_grid.grid=grid.copy()
    unobserved_cells=list()
    for i in range(len(string_board)):
        for j in range(len(string_board[0])):
            if(string_board[i][j]=='.'):
                unobserved_cells.append(grid.grid[i][j])

    #create a string board with possible observations
    bit_board=observations_bit_board(output_grid,cpu_pieces)
    # print_string_board(bit_board)
    # print_string_board(string_board)
    total=calc_po3_loop1(all_neighbors,unobserved_cells,output_grid,bit_board,string_board,cpu_pieces,player_pieces,all_neighbors,pits_per_row)
    total*=multiplier(grid)
    return total


def multiplier(grid):
    global UNITS
    sums=[0,0,0,0]
    w=UNITS[1]
    m=UNITS[0]
    h=UNITS[2]
    for i in range(len(grid.grid)):
        for j in range(len(grid.grid[0])):
            sums[0]+=grid.grid[i][j].p_mage
            sums[1]+=grid.grid[i][j].p_wumpus
            sums[2]+=grid.grid[i][j].p_hero
            sums[3]+=grid.grid[i][j].p_hole
    alpha=[0,0,0,0]
    for i in range(len(sums)):
        if(sums[i]!=0):
            alpha[i]=1/sums[i]
    multiplier=math.factorial(w)*math.factorial(m)*math.factorial(h)*(alpha[0]**m)*(alpha[1]**w)*(alpha[2]**h)
    return multiplier


def observations_bit_board(grid,cpu_pieces):
    board=[['-' for _ in range(len(grid.grid))] for _ in range(len(grid.grid[0]))]
    for i in cpu_pieces:
        bits=i.observe_array
        neighbors=get_neighbors(i,grid)
        for n in neighbors:
            if(board[n.col][n.row]=='-'):
                board[n.col][n.row]=bits
            else:
                board[n.col][n.row]=board[n.col][n.row]&bits
    return board



#recursive function to iterate through observed cells
def calc_po3_loop1(neighbors,unobserved_cells,grid,bit_board,string_board,cpu_pieces,player_pieces,static_observed_cells,pits_per_row):
    if len(neighbors)==0:
        if observations_satisfied(cpu_pieces,string_board,grid):
            #print_string_board(string_board)
            observed_calculations=board_calculations(static_observed_cells,string_board)
            return observed_calculations*calc_po3_loop2(grid,string_board,player_pieces,unobserved_cells,unobserved_cells)
    else:
        total=0
        neighborsc=copy.copy(neighbors)
        cell=neighborsc.pop(0)
        bits=bit_board[cell.col][cell.row]
        #player pieces ex. =[2,2,2]
        #mage,wumpus,hero,pit
        #mage
        if bits[0] and player_pieces[0]>0 and cell.p_mage>0:
            player_pieces[0]-=1
            string_board[cell.col][cell.row]='PM'
            total+=calc_po3_loop1(neighborsc,unobserved_cells,grid,bit_board,string_board,cpu_pieces,player_pieces,static_observed_cells,pits_per_row)
            player_pieces[0]+=1
        #wumpus
        if bits[1] and player_pieces[1]>0 and cell.p_wumpus>0:
            player_pieces[1]-=1
            string_board[cell.col][cell.row]='PW'
            total+=calc_po3_loop1(neighborsc,unobserved_cells,grid,bit_board,string_board,cpu_pieces,player_pieces,static_observed_cells,pits_per_row)
            player_pieces[1]+=1
        #hero
        if bits[2] and player_pieces[2]>0 and cell.p_hero>0:
            player_pieces[2]-=1
            string_board[cell.col][cell.row]='PH'
            total+=calc_po3_loop1(neighborsc,unobserved_cells,grid,bit_board,string_board,cpu_pieces,player_pieces,static_observed_cells,pits_per_row)
            player_pieces[2]+=1
        #pit
        if bits[3] and pits_per_row[cell.row]>0:
            string_board[cell.col][cell.row]='P'
            pits_per_rowc=copy.copy(pits_per_row)
            pits_per_rowc[cell.row]-=1
            total+=calc_po3_loop1(neighborsc,unobserved_cells,grid,bit_board,string_board,cpu_pieces,player_pieces,static_observed_cells,pits_per_rowc)
        #empty
        string_board[cell.col][cell.row]='E'
        total+=calc_po3_loop1(neighborsc,unobserved_cells,grid,bit_board,string_board,cpu_pieces,player_pieces,static_observed_cells,pits_per_row)
        return total
    return 0


def observations_satisfied(cpu_pieces,string_board,grid):
    for i in cpu_pieces:
        pieces=[0,0,0,0]
        for n in get_neighbors(i,grid):
            s=string_board[n.col][n.row]
            if s=='PM':
                pieces[0]+=1
            elif s=='PW':
                pieces[1]+=1
            elif s=='PH':
                pieces[2]+=1
            elif s=='P':
                pieces[3]+=1
        bits=i.observe_array
        for j in range(4):#CHANGE BACK TO 4 WHEN PITS IS FIXED
            if bits[j]==1 and pieces[j]==0:
                #print('This Board Does Not Work')
                return False
    return True

#recusive function to iterate through unobserved cells
def calc_po3_loop2(grid,string_board,player_pieces,unobserved_cells,static_unobserved_cells):
    if(len(unobserved_cells)==0):
        if(sum(player_pieces)!=0):
            print('BIG ERROR FIX')
        return board_calculations(static_unobserved_cells,string_board)
    else:
        unobservedc=copy.copy(unobserved_cells)
        cell=unobservedc.pop(0)
        total=0
        if player_pieces[0]>0 and cell.p_mage>0:
            player_pieces[0]-=1
            string_board[cell.col][cell.row]='PM'
            total+=calc_po3_loop2(grid,string_board,player_pieces,unobservedc,static_unobserved_cells)
            player_pieces[0]+=1

        if player_pieces[1]>0 and cell.p_wumpus>0:
            player_pieces[1]-=1
            string_board[cell.col][cell.row]='PW'
            total+=calc_po3_loop2(grid,string_board,player_pieces,unobservedc,static_unobserved_cells)
            player_pieces[1]+=1

        if player_pieces[2]>0 and cell.p_hero>0:
            player_pieces[2]-=1
            string_board[cell.col][cell.row]='PH'
            total+=calc_po3_loop2(grid,string_board,player_pieces,unobservedc,static_unobserved_cells)
            player_pieces[2]+=1

        if sum(player_pieces)<len(unobserved_cells):
            string_board[cell.col][cell.row]='E'
            total+=calc_po3_loop2(grid,string_board,player_pieces,unobservedc,static_unobserved_cells)
        return total
        #Pits in unobserved cells have to be accounted for eventually


def board_calculations(cell_list,string_board):
    total=1
    for i in cell_list:
        piece_type=string_board[i.col][i.row]
        if piece_type=='PM':
            total*=i.p_mage
        if piece_type=='PW':
            total*=i.p_wumpus
        if piece_type=='PH':
            total*=i.p_hero
        if piece_type=='P':
            total*=i.p_hole
    return total


def get_cpu_pieces(grid):
    output=list()
    for i in range(len(grid.grid[0])):
        for j in range(len(grid.grid)):
            if 4<=grid.grid[i][j].ctype <=6:
                output.append(grid.grid[i][j])
    return output



def calculate_pow2(grid,cell):
    print("here?")
    new_grid=Grid(D_MOD)
    new_grid.grid=grid.copy()
    output_grid=Grid(D_MOD)
    output_grid.grid=grid.copy()
    outputs=list()
    # Keeps track of the number of each unit type ==> 0:Mage, 1:WUMP, 2:HERO (player side)
    p_w=0
    p_m=0
    p_h=0
    p_p=0
    #-----------------------------------------------------------------
    # These will be the number of each piece that the opponent has left
    # Don't know how to get this info yet
    w=UNITS[1]
    m=UNITS[0]
    h=UNITS[2]
    p=((grid.axis_dim/3)-1)#*(grid.axis_dim-2)
    #-----------------------------------------------------------------
    # T is for calculations for each of the types: pit, wumpus, hero, mage
    # This loops goes through the grid, calculates the value of the specific type for
    # all of the cells, and then repeats for every single type
    for t in range(4):
        for i in range(len(grid.grid[0])):
            for j in range(len(grid.grid)):
                if(i==cell.col and j==cell.row):
                    continue
                if t==1:
                    p_w=grid.grid[i][j].p_wumpus*(w-1)/w
                    p_m=grid.grid[i][j].p_mage*(1-cell.p_mage)
                    p_h=grid.grid[i][j].p_hero*(1-cell.p_hero)
                    p_p=grid.grid[i][j].p_hole*(1-cell.p_hole)
                elif t==0:
                    p_w=grid.grid[i][j].p_wumpus*(1-cell.p_wumpus)
                    p_m=grid.grid[i][j].p_mage*(m-1)/m
                    p_h=grid.grid[i][j].p_hero*(1-cell.p_hero)
                    p_p=grid.grid[i][j].p_hole*(1-cell.p_hole)
                elif t==2:
                    p_w=grid.grid[i][j].p_wumpus*(1-cell.p_wumpus)
                    p_m=grid.grid[i][j].p_mage*(1-cell.p_mage)
                    p_h=grid.grid[i][j].p_hero*(h-1)/h
                    p_p=grid.grid[i][j].p_hole*(1-cell.p_hole)
                elif t==3:
                    if p==0:
                        p_p=0
                    elif j==0 or j==grid.axis_dim-1:
                        p_p=0
                    elif not j==cell.row:
                        p_p=grid.grid[i][j].p_hole
                    else:
                        p_p=grid.grid[i][j].p_hole*(p-1)/p
                    p_w=grid.grid[i][j].p_wumpus*(1-cell.p_wumpus)
                    p_m=grid.grid[i][j].p_mage*(1-cell.p_mage)
                    p_h=grid.grid[i][j].p_hero*(1-cell.p_hero)
                new_grid.grid[i][j].set_probabilities(p_p,p_w,p_h,p_m)
        if t==1:
            new_grid.grid[cell.col][cell.row].set_probabilities(0,1,0,0)
            po=calc_po3(new_grid)
            outputs.append(po)
        elif t==0:
            new_grid.grid[cell.col][cell.row].set_probabilities(0,0,0,1)
            po=calc_po3(new_grid)
            outputs.append(po)
        elif t==2:
            new_grid.grid[cell.col][cell.row].set_probabilities(0,0,1,0)
            po=calc_po3(new_grid)
            outputs.append(po)
        elif t==3:
            if p==0:
                outputs.append(0)
            else:
                new_grid.grid[cell.col][cell.row].set_probabilities(1,0,0,0)
                po=calc_po3(new_grid)
                outputs.append(po)
    return outputs

def calculate_observations(grid):
    output_grid=grid.copy()
    po=calc_po3(grid)
    print('PO')
    print(po)
    for i in range (len(grid.grid[0])):
        for j in range(len(grid.grid)):
            #if grid.grid[i][j].observe_array[0]==1 or grid.grid[i][j].observe_array[1]==1 or grid.grid[i][j].observe_array[2]==1 or grid.grid[i][j].observe_array[3]==1:
            pow2=calculate_pow2(grid,grid.grid[i][j])
            p_wumpus=grid.grid[i][j].p_wumpus
            p_mage=grid.grid[i][j].p_mage
            p_hero=grid.grid[i][j].p_hero
            p_pit=grid.grid[i][j].p_hole
            if po!=0:
                p_wumpus=grid.grid[i][j].p_wumpus*pow2[1]/po
                p_mage=grid.grid[i][j].p_mage*pow2[0]/po
                p_pit=grid.grid[i][j].p_hole*pow2[3]/po
                p_hero=grid.grid[i][j].p_hero*pow2[2]/po
            output_grid[i][j].set_probabilities(p_pit,p_wumpus,p_hero,p_mage)
            #else:
                #output_grid[i][j].set_probabilities(grid.grid[i][j].p_hole,grid.grid[i][j].p_wumpus,grid.grid[i][j].p_hero,grid.grid[i][j].p_mage)
    return output_grid

# 0:Mage, 1:WUMP, 2:Hero, 3:Pit


# This function will look at the current board probabilities and will make a move
# that will maximize cpu_pieces-player_pieces.
# Similar to heuristic from assignment 2?
def cpu_make_move(grid):



    return grid




# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** UI ELEMENTS  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# button_layout_rect = pygame.Rect(0, 0, 100, 50)
# button_layout_rect.topright = (-30,70)
# hello_button = pygame_gui.elements.UIButton(relative_rect=button_layout_rect, text='Say Hello', manager=manager,
#                                              anchors={'left': 'right',
#                                              'right': 'right',
#                                              'top': 'top',
#                                              'bottom': 'top'})

cpu_score_layout = pygame.Rect(0,0,150,40)
cpu_score_layout.topright = (-138, 70)
cpu_score_text = pygame_gui.elements.UILabel(relative_rect = cpu_score_layout, text = "CPU Pieces: " + str(CPU_NUM_UNITS), manager = manager,
                                                anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'top',
                                                'bottom': 'top'})

cpu_captured_layout = pygame.Rect(0,0,150,40)
cpu_captured_layout.topright = (-138, 70)


player_score_layout = pygame.Rect(0,0,150,40)
player_score_layout.bottomright = (-138, -20)
player_score_text = pygame_gui.elements.UILabel(relative_rect = player_score_layout, text = "Player Pieces: " + str(PLAYER_NUM_UNITS), manager = manager,
                                                anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'bottom',
                                                'bottom': 'bottom'})

game_status_layout = pygame.Rect(0,0,200,40)
game_status_layout.center = (-138,30)
game_status_text = pygame_gui.elements.UILabel(relative_rect = game_status_layout, text = VICTORY_TEXT, manager = manager,
                                                anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'top',
                                                'bottom': 'bottom'})

reset_layout = pygame.Rect(0,0,150,40)
reset_layout.topright = (-70, 250)
reset_grid_button = pygame_gui.elements.UIButton(relative_rect =reset_layout, text = "Reset Board", manager = manager,
                                                anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'top',
                                                'bottom': 'top'})

toggle_layout = pygame.Rect(0,0,150,40)
toggle_layout.topright = (-70, 300)
toggle_fog_button = pygame_gui.elements.UIButton(relative_rect =toggle_layout, text = "Toggle Fog", manager = manager,
                                                anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'top',
                                                'bottom': 'top'})

generate_layout = pygame.Rect(0,0,150,40)
generate_layout.topright = (-70, 200)
generate_grid_button = pygame_gui.elements.UIButton(relative_rect =generate_layout, text = "Generate Board", manager = manager,
                                                anchors={'left': 'right',
                                                'right': 'right',
                                                'top': 'top',
                                                'bottom': 'top'})

dmod_layout = pygame.Rect(0,0,50,40)
dmod_layout.topright = (-20, 200)
dmod_text_entry = pygame_gui.elements.UITextEntryLine(relative_rect = dmod_layout, manager = manager,
                                                        anchors={'left': 'right',
                                                        'right': 'right',
                                                        'top': 'top',
                                                        'bottom': 'top'})

dmod_text_entry.set_text("2")
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** GAME LOOP ******
        # For testing purposes mainly
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
clock = pygame.time.Clock()
is_running = True
grid=Grid(D_MOD)
grid.generate_grid(D_MOD)
#print(dmod_text_entry.get_text())

# grid.init_grid()
# print(grid.grid[5][1].ctype)
grid.draw_map()

# array =[    ('Cw',  'Ch',   'Cm'),
#             ('-',   '-',    '-'),
#             ('Pw',  'Ph',   'Pm')   ]
# # print(array[0][1][0])
#
# neighbors = get_neighbors_string((2,0), array, False)
# for n in neighbors:
#     print(n)



#prob_dist(grid)

calculate_PO(grid,grid.grid[0][0])

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        player_move_unit(grid, event)

        cpu_score_text.set_text("CPU Pieces: " + str(CPU_NUM_UNITS))
        player_score_text.set_text("PLAYER Pieces: " + str(PLAYER_NUM_UNITS))
        game_status_text.set_text(f'{VICTORY_TEXT}')

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                D_MOD = int(dmod_text_entry.get_text())
                #print(f"D_MOD = {D_MOD}")
                # if event.ui_element == hello_button:
                #     print('Hello World!')
                if event.ui_element == reset_grid_button:
                    print('RESET GRID')
                    grid.reset_grid()
                if event.ui_element == generate_grid_button:
                    print('GENERATE GRID')
                    grid.generate_grid(D_MOD)
                if event.ui_element == toggle_fog_button:
                    FOG = not FOG
                    grid.draw_map()
                    print(f'TOGGLE FOG {FOG}')

        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            col, row = get_clicked_pos(grid, pos)
            if col < 3*D_MOD and row < 3*D_MOD:
                #print(get_neighbors(grid.grid[col][row],grid))
                print(grid.grid[col][row])


    manager.process_events(event)

    manager.update(time_delta)

    WINDOW.blit(background, (0, 0))
    manager.draw_ui(WINDOW)

    pygame.display.update()
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
