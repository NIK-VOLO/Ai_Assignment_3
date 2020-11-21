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
CLICKED_POS = (-1, -1)
LAST_CLICKED = CLICKED_POS
NUM_SELECTED = 0
# QUEUE TO KEEP TRACK OF CONSECUTIVE SELECTS
PLAYER_SELECTIONS = queue.Queue(3)
PLAYER_NUM_UNITS = 0
CPU_NUM_UNITS = 0
VICTORY_TEXT = "Game In Progress..."
D_MOD = 2
p_queue = []
heapq.heapify(p_queue)
FOG = True


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ***** GAME GRID FUNCTIONS  ******
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Grid:
    def __init__(self, dimension_mod):
        self.axis_dim = 3*dimension_mod
        self.grid = [[None for _ in range(
            self.axis_dim)] for _ in range(self.axis_dim)]

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
        PLAYER_NUM_UNITS=0
        CPU_NUM_UNITS=0
        self.axis_dim=3*dimension_mod
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
    print(f"SELECTED CELL :: {CLICKED_POS}  {cell.get_type_text()})")


def player_move_unit(grid, event):
    global LAST_CLICKED
    global CLICKED_POS
    global NUM_SELECTED
    global PLAYER_SELECTIONS
    global PLAYER_NUM_UNITS
    global CPU_NUM_UNITS
    global VICTORY_TEXT
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
                if NUM_SELECTED == 0 and (1 <= cell.ctype <= 3):
                    update_selected(cell)
                    #get_neighbors(cell,grid, True)
                elif NUM_SELECTED == 0 and (4 <= cell.ctype <= 8):
                    print("Please select a friendly piece first!")
                elif NUM_SELECTED > 0 and (4 <= cell.ctype <= 8):
                    update_selected(cell)
            print(f"Num selected = {NUM_SELECTED}")


            if NUM_SELECTED == 2:
                print("CONFIRMED MOVE")
                #cell.draw(background)
                # Get the two cells from the queue
                p_piece = PLAYER_SELECTIONS.get()
                p_piece.selected = False
                NUM_SELECTED -=1
                t_piece = PLAYER_SELECTIONS.get()
                t_piece.selected = False
                NUM_SELECTED -=1

                code=p_piece.fight(t_piece)
                print(f'Code:{code}')
                # No battle, swap swap cells
                if code==0:
                    temp_type = t_piece.ctype
                    t_piece.ctype = p_piece.ctype
                    p_piece.ctype = temp_type
                # Invalid move
                if code==-3:
                    pass
                # both pieces die
                elif code==-2:
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
                    print('here')
                    p_piece.ctype=Ctype.EMPTY
                    print(p_piece)
                    PLAYER_NUM_UNITS -= 1
                elif code==-4:
                    print('Probably a bug?')



                t_piece.draw(background)
                p_piece.draw(background)

                str_board=grid.gen_string_board()
                grid.convert_string_board(str_board)
                pygame.display.update()
                print(f'cpu pieces:{PLAYER_NUM_UNITS}')
                print(f'player pieces:{CPU_NUM_UNITS}')


                print(f"PLAYER PIECES ({PLAYER_NUM_UNITS}) ---- CPU PIECES ({CPU_NUM_UNITS})")


                VICTORY_TEXT = check_win()



                 # A method to check if the player or the cpu won should go here
                str_board=grid.gen_string_board()
                #print_string_board(str_board)

                #----- TESTING OBSERVATION ---------

                #-----------------------------------

                grid.draw_map()

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


                return
            else:
                print("select another to move")

def is_terminal(node):
    if(node[1]==0):
        return True
    elif(node[2]==0):
        return True
    return False


# Returns the heuristic value that is used to sort the board states in the priority queue

def h_val(node,maximizingPlayer):
    #return h_sum_dist(node, maximizingPlayer)
    if node[2]==0:
        return 10000
    elif node[1]==0:
        return -10000

    if node[2]==0:
        return 10000
    if node[1] == 0:
        return -10000

    diff = h_val1(node,maximizingPlayer)
    strength = h_p_value(node,maximizingPlayer)
    print(strength)
    result = 0

    if diff > 0:
        result += h_sum_dist(node, maximizingPlayer) * 20
    elif diff < 0:
        result += h_sum_dist(node, maximizingPlayer)
    elif diff == 0:
        if node[2] == 1:
            result += h_sum_dist(node, maximizingPlayer) * 50
        else:
            result += h_val4(node,maximizingPlayer) + h_sum_dist(node,maximizingPlayer)
    result += diff*50 + h_val2(node,maximizingPlayer) + h_val3(node,maximizingPlayer) + strength

    return result


#Calculates the relative value of the pieces --> Which side has stronger units
def h_p_value(node, maximizingPlayer):
    p_list=get_piece_list(node[0],False)
    cp_list =get_piece_list(node[0], True)
    board=node[0]
    strength = 0
    for cp in cp_list:
        cp_unit = board[cp[0]][cp[1]]
        for p in p_list:
            p_unit = board[p[0]][p[1]]
            if cp_unit == "CM":
                if p_unit == "PW":
                    strength -= 1
                elif p_unit == "PK":
                    strength += 1
            elif cp_unit == "CW":
                if p_unit == "PK":
                    strength -= 1
                elif p_unit == "PM":
                    strength += 1
            elif cp_unit == "CK":
                if p_unit == 'PM':
                    strength -= 1
                elif p_unit == "PW":
                    strength += 1
    return strength
#difference in # of pieces, makes it more aggressive
def h_val1(node,maximizingPlayer):
    return (node[1]-node[2])

#number of different neighbor enemy pieces
def h_val2(node,maximizingPlayer):
    p_list=get_piece_list(node[0],True)
    vals=[0]*len(p_list)
    for i in range(len(p_list)):
        current=p_list[i]
        neighbors=get_neighbors_string(current,node[0],True)
        for j in neighbors:
            if node[0][j[0]][j[1]][0]!='-':
                f=string_fight(node[0][current[0]][current[1]],node[0][j[0]][j[1]])
                if(f==1):
                    vals[i]+=1
                elif(f==-1):
                    vals[i]-=1
    return sum(vals)

# Number of friendly neighbor pieces, makes it cluster more
def h_val3(node,maximizingPlayer):
    p_list=get_piece_list(node[0],True)
    vals=[1]*len(p_list)
    for i in range(len(p_list)):
        current=p_list[i]
        neighbors=get_neighbors_string(current,node[0],True)
        friendlyNeighbors=get_neighbors_string(current,node[0],not True)
        for j in neighbors:
            if node[0][j[0]][j[1]][0]!='-':
                f=string_fight(node[0][current[0]][current[1]],node[0][j[0]][j[1]])
                if(f==1):
                    vals[i]+=1
                elif(f==-1):
                    vals[i]-=1
        for k in friendlyNeighbors:
            if node[0][k[0]][k[1]][0]!='-':
                vals[i]+=1
    return sum(vals)/len(p_list)

#Row #,makes it more aggressive
def h_val4(node,maximizingPlayer):
    global D_MOD
    p_list=get_piece_list(node[0],True)
    total=0
    for i in p_list:
        #print(i[1])
        if(True):
            total+=i[1]
        else:
            total+=(3*D_MOD)-1+i[1]
    return total/len(p_list)

def row_dif(node):
    global D_MOD
    board=node[0]
    return h_val4(node,True)-h_val4(node,False)

# Calculates the average 'unit position' for each player, then calculates the MANHATTAN distance
def h_distance_avg(node, maximizingPlayer):
    global D_MOD
    p_list=get_piece_list(node[0],not maximizingPlayer)
    cp_list =get_piece_list(node[0], maximizingPlayer)
    average_dist = 0
    #print(p_list)
    #print(cp_list)
    avg_p_point_x = 0
    avg_p_point_y = 0
    avg_cp_point_x = 0
    avg_cp_point_y = 0
    avg_p_point = (0,0)
    avg_cp_point = (0,0)
    for i in range(len(p_list)):
        avg_p_point_x += p_list[i][0]
        avg_p_point_y += p_list[i][1]
        pass
    for j in range(len(cp_list)):
        avg_cp_point_x = cp_list[j][0]
        avg_cp_point_y = cp_list[j][1]
        # print(f"{p_list[i]} -- {cp_list[j]}")
        pass
    if(len(p_list) > 0):
        avg_p_point = (avg_p_point_x/len(p_list),avg_p_point_y/len(p_list))
    if(len(cp_list) > 0):
        avg_cp_point = (avg_cp_point_x/len(cp_list),avg_cp_point_y/len(cp_list))
    #print(f"PLAYER {avg_p_point} -- CPU {avg_cp_point}")

    #MANHATTAN DISTACE:
    result = round(math.sqrt(pow(avg_p_point[0] - avg_cp_point[0],2) + pow(avg_p_point[1] - avg_cp_point[1],2)), 2)
    #print(f"MANHATTAN DISTANCE OF AVERAGE PTS --> {result}")


    board_size=D_MOD*3
    return board_size/result

# Sum of the distances of each piece
def h_sum_dist(node, maximizingPlayer):
    global D_MOD
    base = 2 * D_MOD
    p_list=get_piece_list(node[0],False)
    cp_list =get_piece_list(node[0], True)
    dist_sum = 0
    #print(p_list)
    for p in p_list:
        #print(p, end = "\t")
        for cp in cp_list:
            #print(cp, end = ', ')
            dist_sum += distance_manhat(p,cp)
    #print(f"DIST_SUM = {dist_sum}")
    result = dist_sum / (1 + (len(p_list) + (len(cp_list)))*(3 * D_MOD))
    diff = h_val1(node, maximizingPlayer)
    modifier = 1/(1 + abs(diff))
    #print(f"MODIFIER = {modifier}")
    if diff >= 0:
        #return base - (result * modifier)
        return -result
    else:
        #return base + result * modifier
        return result

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

def distance_manhat(p1, p2):
    return round(abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]), 2)
# Gets the cells around the piece that have valid moves
# --> If the cell has a pit, we assume that it's a bad move and don't add it to the list
# --> Depending on if the turn is maximizingPlayer or not, add cells containing enemy units but ignore friendly units
def get_neighbors(cell, grid, maximizingPlayer):
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
            if(grid.grid[cell.col-1+i][cell.row-1+j].ctype == Ctype.HOLE):
                #print(f"({i},{j}) IS A HOLE")                                        #------------- THIS MIGHT NEED OPTIZING ------------------
                continue
            #Check maximizingPlayer:
            # Assume player is maximizingPlayer
            if not maximizingPlayer:
                if 1 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 3:
                    #print(f"({i},{j}) IS A MAXimizingPlayer FRIENDLY PIECE (ignore)")
                    continue
            else:
                if 4 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 6:
                    #print(f"({i},{j}) IS A MINImizingPlayer FRIENDLY PIECE (ignore)")
                    continue
            #print(f"({i},{j}) is VALID")
            neighbors.append(grid.grid[cell.col-1+i][cell.row-1+j])
    return neighbors


# def get_neighbors_string(pair, array, maximizingPlayer):
#     global D_MOD
#     col = pair[0]
#     row = pair[1]
#     neighbors = []
#     board_size = D_MOD * 3
#     for j in range(3):
#         for i in range(3):
#             #print(f'{cell.col-1+i}, {cell.row-1+j}')
#             if(i == 1 and j == 1): # the current cell is self, don't check
#                 continue
#             if(col-1+i > board_size -1 or col-1+i < 0 or row-1+j > board_size -1 or row-1+j < 0):
#                 #print(f"({i},{j}) OUT OF BOUNDS")
#                 continue
#             if(array[col-1+i][row-1+j] == 'H'):
#                 #print(f"({i},{j}) IS A HOLE")                                        #------------- THIS MIGHT NEED OPTIZING ------------------
#                 continue
#             #Check maximizingPlayer:
#             # Assume player is maximizingPlayer
#             if not maximizingPlayer:
#                 #if 1 <= array[cell.col-1+i][cell.row-1+j].ctype <= 3:
#                 if array[col-1+i][row-1+j][0] == 'P':
#                     #print(f"({i},{j}) IS A MAXimizingPlayer FRIENDLY PIECE (ignore)")
#                     continue
#             else:
#                 #if 4 <= grid.grid[cell.col-1+i][cell.row-1+j].ctype <= 6:
#                 if array[col-1+i][row-1+j][0] == 'C':
#                     #print(f"({i},{j}) IS A MINImizingPlayer FRIENDLY PIECE (ignore)")
#                     continue
#             #print(f"({i},{j}) is VALID")
#             #neighbors.append((array[col-1+i][row-1+j],col-1+i,row-1+j))
#             neighbors.append((col-1+i,row-1+j))
#     return neighbors

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


#Get observation of unit's surroundings
#   PIT --> Breeze
#   WUMPUS --> Stench
#   HERO --> Sound
#   MAGE --> Heat
def observe(pair, array, player):
    neighbors = get_neighbors_string(pair, array, player)
    print(neighbors)


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


def alphabeta(node,depth,alpha,beta,maximizingPlayer):
    #return #TEMPORARY
    #global p_queue
    #p_queue=[]
    if depth==0 or is_terminal(node):
        return (h_val(node,maximizingPlayer),node)
    str_grid=node[0]
    best_move=None #this will be used to return the string_grid of the best move that the computer calculated
    if maximizingPlayer:
        value=float('-inf')
        p_queue=[]
        heapq.heapify(p_queue)
        #------------------------------------------------
        #create the childs of the current board state
        pieces = get_piece_list(str_grid, maximizingPlayer)
        game_states=list()
        for i in pieces:
            neighbors=get_neighbors_string(i,node[0],True)
            for size in range(len(neighbors)):
                game_states.append(get_child_state(i,neighbors[size],node,maximizingPlayer))
        #------------------------------------------------
        # Get neighbors of
        for child in game_states:

            heapq.heappush(p_queue,(h_val(child,maximizingPlayer),child))
        #print('length')
        #print(len(p_queue))
        while len(p_queue)>0:
            child=heapq.heappop(p_queue)
            #print_string_state(child)
            alphabeta_results=alphabeta((child[1][0],child[1][1],child[1][2]),depth-1,alpha,beta,False)
            if alphabeta_results[0]>value:
                value=alphabeta_results[0]
                best_move=(child[1][0],child[1][1],child[1][2])
            #I don't know if the next line should be part of the above if statement
                alpha=max(alpha,value)
            if(alpha>=beta):
                continue
        return (value,best_move)
    else:
        value=float('inf')

        p_queue=[]
        heapq.heapify(p_queue)
        #------------------------------------------------
        #create the childs of the current board state
        pieces=get_piece_list(str_grid,maximizingPlayer)
        game_states=list()
        for i in pieces:
            neighbors=get_neighbors_string(i,node[0],False)
            for size in range(len(neighbors)):
                game_states.append(get_child_state(i,neighbors[size],node,maximizingPlayer))
        #------------------------------------------------
        for child in game_states:
            heapq.heappush(p_queue,(0-h_val(child,maximizingPlayer),child))
            #add child to queue
        while len(p_queue)>0:
            child=heapq.heappop(p_queue)
            alphabeta_results=alphabeta((child[1][0],child[1][1],child[1][2]),depth-1,alpha,beta,True)
            if alphabeta_results[0]<value:
                value=alphabeta_results[0]
                best_move=(child[1][0],child[1][1],child[1][2])
                beta=min(beta,value)
            if(alpha>=beta):
                continue
        return (value,best_move)
#structure of node: (cell, grid,cpunumpieices,playernumpieces)



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


    manager.process_events(event)

    manager.update(time_delta)

    WINDOW.blit(background, (0, 0))
    manager.draw_ui(WINDOW)

    pygame.display.update()
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
