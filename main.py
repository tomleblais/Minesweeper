from tkinter import *
from random import random

class Minesweeper(object):
    def __init__(self, root, proba, w, h):
        self.w = w
        self.h = h
        self.c = 30
        self.proba = proba
        self.bombs = 0
        self.returnedCases = 0
        self.cases = self.w * self.h
        self.elementsToReturn = []
        self.lost = None
        self.can = Canvas(fen, width=self.w * self.c, height=self.h * self.c)
        self.W = int(self.can["width"]) + 2
        self.H = int(self.can["height"]) + 2
        self.can.pack()
        self.grid = []
        self.createGrid()
        self.can.bind("<Button-1>", self.a)
        self.can.bind("<Button-3>", self.b)

        def c(e):
            case = self.getCaseEvent(e)
            returnable = True
            if case.returned:
                cases = [case]
                cases += self.getNeighbours(case.x, case.y)
                for i in range(len(cases)):
                    c = cases[i]
                    if c.bomb:
                        if not c.defused:
                            returnable = False
                            break
                if returnable:
                    for i in range(len(cases)):
                        c = cases[i]
                        if not c.returned and not c.defused and c.x > 0 and c.x <= self.w and c.y > 0  and c.y < self.h + 1:
                            self.switchActions(c.x, c.y)
            
            
        self.can.bind("<Button-2>", c)

    def createGrid(self):
        self.grid = [0] * (self.h + 2)
        self.grid = [[Case(i, j, self.c, 0) for i in range(self.w + 2)] for j in range(self.h + 2)]

        # Set Bombs
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[y]) - 1):
                if random() < self.proba:
                    self.case(x, y).value = "B"
                    self.case(x, y).bomb = 1
                    self.bombs += 1
                else:
                    self.case(x, y).value = 0
                    self.case(x, y).bomb = 0

        # Set Numbers
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[y]) - 1):
                if not self.case(x, y).bomb:
                    self.case(x, y).value = self.getNumbersBombsAround(x, y)

        # Show grid
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[y]) - 1):
                self.refreshCase(x, y)
        
    
    def switchActions(self, x, y):
        case = self.case(x, y)
        if case.bomb:
            self.showCase(x, y)
            self.lost = True
            self.can.after(1500, self.lose)
            self.can.unbind("<Button-3>")
            self.can.bind("<Button-3>", self.b)
        else:
            if case.value == 0:
                self.returnZero(x, y)
                for i in self.elementsToReturn:
                    self.case(i[0], i[1]).returned = True
                    self.refreshCase(i[0], i[1])
                    self.returnedCases += 1
                self.elementsToReturn = []
            else:
                self.showCase(x, y)
                self.returnedCases += 1
            if self.w*self.h-self.returnedCases == self.bombs:
                self.won()

    def returnZero(self, x, y):
        if self.case(x, y).value == 0:
            if not [x, y] in self.elementsToReturn:
                self.elementsToReturn.append([x, y])
            neighbours = self.getNeighbours(x, y)
            for k in neighbours:
                currentCoords = [k.x, k.y]
                if not currentCoords in self.elementsToReturn and not k.x <= 0 and not k.y <= 0 and not k.x >= self.w + 1 and not k.y >= self.h + 1:
                    self.elementsToReturn.append(currentCoords)
                    if self.case(currentCoords[0], currentCoords[1]).value == 0:
                        self.returnZero(currentCoords[0], currentCoords[1])
    def refreshCase(self, x, y):
        case = self.case(x, y)
        if case.image:
            self.can.delete(case.image)
    
        if case.returned:
            case.defused = False
            case.image = PhotoImage(file="images/" + str(case.value) + ".gif")
        else:
            if case.defused:
                case.image = PhotoImage(file="images/flag.gif")
            else:
                case.image = PhotoImage(file="images/back.gif")
        self.can.create_image(case.gx, case.gy, image=case.image)
        return False
    
    def showCase(self, x, y):
        if not self.case(x, y).returned:
            self.case(x, y).returned = True
            self.refreshCase(x, y)

            
    def dropFlag(self, x, y):
        case = self.case(x, y)
        case.defused = False

    def defuseBomb(self, x, y):
        self.case(x, y).defused = True

    def a(self, e):
        case = self.getCaseEvent(e)
        if not case.defused and not case.returned:
            self.switchActions(case.x, case.y)

    def b(self, e):
        case = self.getCaseEvent(e)
        if not case.returned:
            if not case.defused:
                self.defuseBomb(case.x, case.y)
            else:
                self.dropFlag(case.x, case.y)
            self.refreshCase(case.x, case.y)
        
    
    def getCaseEvent(self, e):
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[y]) - 1):
                if e.x >= self.case(x, y).mingx and e.x <= self.case(x, y).maxgx and e.y >= self.case(x, y).mingy and e.y <= self.case(x, y).maxgy:
                    return self.case(x, y)

    def won(self):
        text = self.can.create_text(self.W // 2, self.H // 2, text="Game Won", font=("Terminal", self.c, "bold"), fill="green")
        self.can.create_rectangle(0, self.H // 2 - self.c // 2 - 10, self.W, self.H // 2 + self.c // 2 + 10, fill="white")
        self.can.lift(text)
        self.can.unbind("<Button-3>")
        self.can.unbind("<Button-1>")
        self.can.unbind("<Button-2>")
    
    def lose(self):
        text = self.can.create_text(self.W // 2, self.H // 2, text="Game Over", font=("Terminal", self.c, "bold"), fill="red")
        self.can.create_rectangle(0, self.H // 2-self.c // 2 - 10, self.W, self.H // 2 + self.c // 2 + 10, fill="white")
        self.can.lift(text)
        self.can.unbind("<Button-3>")
        self.can.unbind("<Button-1>")
        self.can.unbind("<Button-2>")

    def getNumbersBombsAround(self, x, y):
        bombs = 0
        for i in self.getNeighbours(x, y):
            bombs += i.bomb
        return bombs
                              
    def getNeighbours(self, x, y):
        neighbours = []
        for k in self.getCoordsAround(x, y):
            neighbours.append(self.case(k[0], k[1]))
        return neighbours
            

    def getCoordsAround(self, x, y):
        return [
                (x - 1, y - 1),
                (x, y - 1),
                (x + 1, y - 1),
                
                (x - 1, y),
                (x + 1, y),
                
                (x - 1, y + 1),
                (x, y + 1),
                (x + 1, y + 1),
            ]
    
    def case(self, x, y):
        return self.grid[y][x]
    
    def coords(self, case):
        return case.coords

        
class Case(object):
    def __init__(self, x, y, c, value, returned=False, defused=False, bomb=0):
        self.x = x
        self.y = y
        self.coords = [x, y]
        self.c = c
        self.value = value
        self.bomb = bomb
        self.returned = returned
        self.defused = defused
        self.fileName = None
        self.image = None
        
        self.mingx = self.c * x - self.c
        self.mingy = self.c * self.y - self.c
        self.maxgx = self.c * self.x
        self.maxgy = self.c * self.y
        self.gx = self.c * self.x - self.c // 2
        self.gy = self.c * self.y - self.c // 2

if __name__ == "__main__":
    fen = Tk()
    fen.title("Démineur")
    dem = Minesweeper(fen, 0.15, 15, 15)
    def showResponseGrid():
        for i in range(1, len(dem.grid) - 1):
            for j in range(1, len(dem.grid[i]) - 1):
                element = dem.grid[i][j]
                print(element.value, end=" ")
            print("")
    fen.mainloop()
