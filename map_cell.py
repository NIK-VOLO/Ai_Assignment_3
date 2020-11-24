import pygame
from enum import IntEnum
from bitarray import bitarray

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY_light = (232, 232, 232)
GREY_dark = (128,128,128)
RED=(255,0,0)
BLUE=(0,0,255)
PURPLE=(128,0,128)
YELLOW =(255, 230, 0)
GREEN = (0, 255, 26)
class Ctype(IntEnum):
    MAGE=1
    WUMPUS=2
    KNIGHT=3
    CPUMAGE=4
    CPUWUMPUS=5
    CPUKNIGHT=6
    HOLE=7
    EMPTY=8

class Cell:
    def __init__(self, col,row,size, totalDimensions,ctype):
        self.col=col
        self.row=row
        self.size=size
        self.x=col*size
        self.y=row*size
        self.ctype=ctype
        self.selected=False
        self.select_surfaceRect=pygame.Surface((self.size-3, self.size-3))
        self.fog_surfaceRect=pygame.Surface((self.size-3, self.size-3))
        self.select_opacity = 0
        self.fog = True
        self.fog_opacity = 255
        self.innerRect=pygame.Rect(self.x+2,self.y+2,self.size-1,self.size-1)
        self.observationSurf = pygame.Surface((self.size/5, self.size-3))
        self.observe_array = bitarray(4) #CREATES A BIT ARRAY FOR OBSERVATION BOOLEANS (bit index order: 0123)
        self.observe_array.setall(0)
        #self.observe_array[0] = 1
        #print(self.observe_array)

        #self.font = pygame.font.SysFont(NONE, 12)

    def set_observation(self, bitarr):
        self.observe_array = bitarr
        #print(self.observe_array)

    def contains_piece(self,other):
        return self.ctype<7

    def __str__(self):
        return f'({self.col},{self.row}),{self.get_type_text()}'
    #Called when a cell is clicked on,
    def set_selected(self,tf):
        self.selected=tf

    def set_ctype(self,ctype):
        self.ctype=ctype

    def set_fog(self,tf):
        self.fog = tf

    #-------------------------------------------------------
    # Does not change selected (boolean) or the ctype in the cell.
    # Have to do that in grid to store information on how many of each type of piece are left
    # Returns:
    # 0 if no piece dies,
    # -1 if self piece dies,
    # 1 if cell2 dies,
    # -2 if both pieces die
    # -3 if move is not allowed
    # -4 Means that the first piece selected was not a player or cpu piece, so probably a bug with the program
    #-------------------------------------------------------
    def fight(self,cell2):
        if not (self.row in range(cell2.row-1,cell2.row+2) and self.col in range(cell2.col-1,cell2.col+2)):
            print('Invalid Move cell range')
            return -3
        #Self piece is a player piece
        if(1<=self.ctype<=3):
            if cell2.ctype==Ctype.EMPTY:
                return 0
            elif cell2.ctype==Ctype.HOLE:
                return -1
            elif (1<=cell2.ctype<=3):
                print('Invalid Move pvp')
                return -3
            else:
                id=self.ctype+3-cell2.ctype
                if(id==0):
                    print('Both die')
                    return -2
                #cell2 piece dies
                elif(id==1 or id==-2):
                    return 1
                #cell1 piece dies
                else:
                    return -1

        # Self piece is a cpu piece
        elif 4<self.ctype<=6:
            if cell2.ctype==Ctype.EMPTY:
                return 0
            elif cell2.ctype==Ctype.HOLE:
                return -1
            elif (4<=cell2.ctype<=6):
                print('Invalid Move cpu v.cpu')
                return -3
            else:
                id=self.ctype-3-cell2.ctype
                if(id==0):
                    print('Both die')
                    return -2
                #cell2 piece dies
                elif(id==1 or id==-2):
                    return 1
                #cell1 piece dies
                else:
                    return -1
        # Probably a bug
        else:
            print('BUG?')
            return -4
    def get_type_text(self):
        t=self.ctype
        if(t==Ctype.CPUKNIGHT):
            return 'CPUH'
        elif(t==Ctype.CPUMAGE):
            return 'CPUM'
        elif(t==Ctype.CPUWUMPUS):
            return 'CPUW'
        elif(t==Ctype.MAGE):
            return "PM"
        elif(t==Ctype.KNIGHT):
            return "PH"
        elif(t==Ctype.WUMPUS):
            return 'PW'
        elif(t==Ctype.HOLE):
            return 'HOLE'
        else:
            return ''
    def draw(self,win):
        selected_rec=self.select_surfaceRect
        if (self.ctype == 1):
            self.image = pygame.image.load("MageB.png")
        elif self.ctype == 2:
            self.image = pygame.image.load("WumpusB.png")
        elif self.ctype == 3:
             self.image = pygame.image.load("KnightB.png")
        elif self.ctype == 4:
             self.image = pygame.image.load("MageR.png")
        elif self.ctype == 5:
             self.image = pygame.image.load("WumpusR.png")
        elif self.ctype == 6:
            self.image = pygame.image.load("KnightR.png")
        elif self.ctype == 7:
            self.image = pygame.image.load("Hole.png")
        elif self.ctype == 8:
            self.image = pygame.image.load("Blank.png")

        #print(f"size of cell is {self.size} x {self.size}")

        if self.ctype != 8:
            if (self.size > 32):
                self.image = pygame.transform.scale(self.image, (32 * round((self.size) / 32), 32 * round((self.size) / 32)))
            else:
                if (self.size > 16):
                    self.image = pygame.transform.scale(self.image, (16, 16))
                else:
                    self.image = pygame.transform.scale(self.image, (8, 8))
        else:
            self.image = pygame.transform.scale(self.image, (2, 2))

        if(self.selected):
            selected_rec.fill(YELLOW)
            self.select_opacity = 100
            mainColor=PURPLE
        else:
            self.select_opacity = 0

        if(self.fog and not(1<=self.ctype <=3)):
            self.fog_surfaceRect.fill(GREY_dark)
            self.fog_opacity = 255
        else:
            self.fog_opacity = 0

        self.rect = self.image.get_rect(center=self.innerRect.center)
        self.innerRect = self.image.get_rect(center=self.innerRect.center)
        win.fill(WHITE, self.innerRect)
        pygame.draw.rect(win, WHITE, (self.x + 2, self.y + 2, self.size - 1, self.size - 1))
        win.blit(self.image, self.innerRect)

        selected_rec.set_alpha(self.select_opacity)
        win.blit(selected_rec,(self.x+3,self.y+3))

        if not (self.ctype == 7) and not (self.ctype == 8):
            self.observationSurf.fill(GREY_light)
            self.observationSurf.set_alpha(128)
            if self.observe_array[0] == 1:
                pygame.draw.rect(self.observationSurf, RED, pygame.Rect(0, 0, self.size/5, self.size/4))
            if self.observe_array[1] == 1:
                pygame.draw.rect(self.observationSurf, GREEN, pygame.Rect(0, (self.size/4), self.size/5, self.size/4))
            if self.observe_array[2] == 1:
                pygame.draw.rect(self.observationSurf, YELLOW, pygame.Rect(0, 2*(self.size/4), self.size/5, self.size/4))
            if self.observe_array[3] == 1:
                pygame.draw.rect(self.observationSurf, (65, 16, 92), pygame.Rect(0, 3*(self.size/4), self.size/5, self.size/4))

            win.blit(self.observationSurf,(self.x+3,self.y+3))


        self.fog_surfaceRect.set_alpha(self.fog_opacity)
        win.blit(self.fog_surfaceRect,(self.x+3,self.y+3))
