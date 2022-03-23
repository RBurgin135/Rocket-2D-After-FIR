import pygame
from pygame import FULLSCREEN
import random
import copy
import math
import os


#window setup
import ctypes
user32 = ctypes.windll.user32
global scr_width
global scr_height
scr_width = user32.GetSystemMetrics(0)
scr_height = user32.GetSystemMetrics(1)
window = pygame.display.set_mode((scr_width,scr_height),FULLSCREEN)
pygame.display.set_caption("ROCKET")
pygame.font.init()
from pygame.locals import *
pygame.init()

#BOARD ======================
class Board:
    def __init__(self):
        self.RUN = True
        self.g = 0.0055
        self.spawnlimit = [500,250,800]

        #particles
        self.particles = []
        self.particleshow = False
        self.failureshow = False

        #rockets
        self.rockets = []
        self.gensize = 40

        #colours
        self.backC = (33,44,48)
        self.baseC = (40,62,63)
        self.textC = (247,216,148)
        self.highC = (60,82,83)
        self.subC = (130,51,60)
        self.deadC = (193,193,193)

        #options
        OpFont = pygame.font.SysFont('', 25)
        save = [scr_width-200, 0, 200, 100]
        load = [scr_width-200, 100, 200, 100]
        hide = [scr_width-200, 200, 200, 100]
        self.optionplacement = [save,load,hide]
        self.optionstitles = [OpFont.render("SAVE", False, self.textC), OpFont.render("LOAD", False, self.textC), OpFont.render("HIDE", False, self.textC)]
        self.textbox = False
        self.textboxchoice = -1
        self.textboxtext = ""

        #hide
        self.hideamount = 0

        #subs
        self.SubFont = pygame.font.SysFont('', 25)
        self.subtexttitles = ["GENERATION: ", "EFFECTS: ", "FAILURES: "]
        self.gen = 1
        self.subcoord = [550, 0]

        #ground
        self.groundcoord = [scr_width/2, scr_height-200]

        #diag
        self.DiagFont = pygame.font.SysFont('', 24)
        X = scr_width - self.optionplacement[-1][2]/2
        Y = self.optionplacement[-1][1] + self.optionplacement[-1][3]
        self.diagcolumnsize = 20
        self.diaggap = (scr_height - Y)/self.diagcolumnsize
        self.diagstart = [X, Y]
        self.deadtext = OpFont.render("XXXX", False,  self.deadC)
        self.netstart = [self.optionplacement[0][0] - 400, 100]

    def Show(self):
        self.ShowOptions()
        self.ShowSubs()
        self.ShowDiag()
        if self.failureshow:
            self.ShowBox()
        self.ShowNet()

    def ShowOptions(self):
        #options=======
        M.highlight = -1
        #base
        for z in range(len(self.optionplacement)):
            i = self.optionplacement[z]
            
            #mouse over
            if (i[0] < M.coord[0] < i[0] + i[2]) and (i[1] < M.coord[1] < i[1] + i[3]):
                M.highlight = z
                pygame.draw.rect(window, self.highC, (i))
            else:
                pygame.draw.rect(window, self.baseC, (i))
        
            #text
            window.blit(self.optionstitles[z], (i[0]+i[2]//2-10, i[1]+i[3]//2))
        
        #texbox
        if self.textbox:
            #line
            l = self.optionplacement[0]
            coords = [[l[0]-200, l[1]+50], [l[0]-25, l[1]+50]]
            pygame.draw.line(window, self.baseC, coords[0], coords[1])

            #text
            BoxFont = pygame.font.SysFont('', 25)
            Text = BoxFont.render(self.textboxtext, False, self.baseC)
            window.blit(Text, (coords[0][0], coords[0][1]-17))

    def Textbox(self):
        act = False
        for event in pygame.event.get():
            #keys
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    act = True
                elif keys[pygame.K_BACKSPACE]:
                    self.textboxtext = self.textboxtext[:-1]
                else:
                    self.textboxtext += event.unicode

        #save + load
        if act:
            if self.textboxchoice == 0:
                neu.Write(self.gen, self.rockets, self.textboxtext)
            elif self.textboxchoice == 1:
                try:
                    self.rockets, self.gen = neu.Read(self.rockets, self.textboxtext)
                except:
                    FileNotFoundError
            elif self.textboxchoice == 2:
                try:
                    self.hideamount = int(self.textboxtext)
                    self.HideSome()
                except:
                    ValueError
            
            self.textbox = False

    def HideSome(self):
        if self.hideamount:
            for i in self.rockets:
                i.hide = True
            
            for i in range(self.hideamount):
                self.rockets[i].hide = False
        else:
            for i in self.rockets:
                i.hide = False

    def ShowSubs(self):
        X, Y = copy.deepcopy(self.subcoord)

        data = [self.gen]

        #effects
        if self.particleshow:
            data.append("ON")
        else:
            data.append("OFF")

        #lines
        if self.failureshow:
            data.append("ON")
        else:
            data.append("OFF")

        for i in range(len(self.subtexttitles)):
            text = self.SubFont.render(self.subtexttitles[i]+str(data[i]), False, self.subC)
            window.blit(text, (X, Y))
            Y += 25

    def ShowDiag(self):
        X, Y = self.diagstart
        index = 0
        for i in self.rockets:
            index += 1
            

            #review states
            s = i.Nn.state
            if s == "new":
                colour = (255,174,201)#pink
            elif s == "processing":
                colour = (255,0,0)#red
            elif s == "cloned":
                colour = (255,242,0)#yellow
            elif s == "bred":
                colour = (34,177, 76)#green
            elif s == "mutated":
                colour = (63,72,204)#blue
            pygame.draw.rect(window, colour, (X, Y, 5, self.diaggap))
            

            
            #highlight + outline
            coord = [X  + 30, Y + self.diaggap/2]
            blit = [coord[0] - i.width/2, coord[1] - i.height/2]
            self.HighlightCheck(i, blit)
            if i.highlighted:
                window.blit(i.oresult, (coord[0] - i.odim[0]/2, coord[1] - i.odim[1]/2))

            #portrait
            window.blit(i.result, (blit))

            #text
            if i.tested and not i.success:
                window.blit(self.deadtext, (X + 50, Y+10))
            else:
                text1 = self.DiagFont.render(str(round(i.disp[0]))+"m", False,  self.textC)
                text2 = self.DiagFont.render(str(round(i.disp[1]))+"m", False,  self.textC)
                window.blit(text1, (X + 50, Y+6))
                window.blit(text2, (X + 50, Y+20))
            

            #spacing
            Y += self.diaggap
            if index == self.diagcolumnsize:
                index = 0
                X -= 100
                Y = self.diagstart[1]

    def ShowNet(self):
        for i in self.rockets:
            if i.highlighted:
                X, Y = self.netstart
                net = i.Nn
                record = []
                for t in range(len(net.layers)): #cycles through topologies
                    record.append([])
                    for l in range(len(net.layers[t])): #cycles through layers
                        record[-1].append([])
                        for n in range(len(net.layers[t][l])): #cycles through neurons
                            X = self.netstart[0] + (100 * l)
                            Y = self.netstart[1] + (150 * t) + (50 * n)
                            active = net.layers[t][l][n].activated
                            record[-1][-1].append([X, Y, active, []])
                            for w in net.layers[t][l][n].weight: #cycles through weights
                                record[-1][-1][-1][-1].append(w)

                
                for t in record: #cycle through topologies
                    prevlayer = []
                    for l in t: #cycles through layers
                        thislayer = []
                        for n in l: #cycles through neurons
                            thislayer.append(n[:2])
                            if n[2]:
                                colour = (255,242,0) #yellow
                            else:
                                colour = (70, 70, 70) #grey
                            pygame.draw.circle(window, colour, (n[0], n[1]), 15)

                            if len(prevlayer) > 0:
                                for w in n[3]:
                                    #colour
                                    if w < 0:
                                        colour = (63,72,204) #blue
                                    else:
                                        colour = (255,0,0) #red

                                    p = prevlayer[n[3].index(w)]
                                    pygame.draw.line(window, colour, (n[:2]), p, round(abs(w*5)))
                        prevlayer = copy.deepcopy(thislayer)

    def ShowBox(self):
        pygame.draw.rect(window, self.deadC, self.deathbox, 2)

    def HighlightCheck(self, rocket, coord):
        mouseover = True
        for i in range(2):
            if not (coord[i] < M.coord[i] < coord[i] + rocket.dim[i]):
                mouseover = False

        if mouseover:
            rocket.highlighted = True
        else:
            rocket.highlighted = False

    def GenMonitor(self):
        query = True
        for i in self.rockets:
            if not i.tested:
                query = False

        if query:
            self.particles = []

            #review
            for i in self.rockets:
                i.scoringvalues = [[i.scoreu, i.maxu], [i.disp[0], i.startdisp[0]], i.success, i.dieearly]

            #reset rockets
            newnets = neu.Review(self.rockets)
            ##self.startdisp = [random.randint(-self.spawnlimit[0],self.spawnlimit[0]), random.randint(self.spawnlimit[1],self.spawnlimit[2])]
            self.startdisp = [-250, 500]
            for i in range(self.gensize):
                self.rockets[i].__init__(self.startdisp[0], self.startdisp[1], False)
                self.rockets[i].Nn = newnets[i]

            #deathbox
            self.deathbox = self.groundcoord[0] - abs(self.startdisp[0]) - 10, self.groundcoord[1] - abs(self.startdisp[1]) -50, abs(self.startdisp[0])*2+20, abs(self.startdisp[1])+50

            self.gen += 1

            #performance
            self.HideSome()

#MOUSE ======================
class Mouse:
    def __init__(self):
        self.coord = [0, 0]
        self.coord[0], self.coord[1] = pygame.mouse.get_pos()
        
        #buttons
        self.leftclick = False
        self.highlight = -1

    def Input(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            #mouse
            if event.type == pygame.MOUSEMOTION:
                self.coord[0], self.coord[1] = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    self.LClickDOWN()
            if event.type == pygame.MOUSEBUTTONUP:
                if self.leftclick:
                    self.LClickUP()

            #keys
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    if B.particleshow:
                        B.particles = []
                        B.particleshow = False
                    else:
                        B.particleshow = True
                if keys[pygame.K_f]:
                    if B.failureshow:
                        B.failureshow = False
                    else:
                        B.failureshow = True
                        
        if keys[pygame.K_w]:##
            R.Ignite()##
        if keys[pygame.K_a]:##
            R.Turn(True)##
        if keys[pygame.K_d]:##
            R.Turn(False)##

    def LClickDOWN(self):
        if self.highlight != -1:
            self.leftclick = True

        #exit
        if self.coord[0] > scr_width-50 and self.coord[0] < scr_width and self.coord[1] < scr_height and self.coord[1] > scr_height-50:
            B.RUN = False

        #hide
        for i in B.rockets:
            if i.highlighted and not i.tested:
                i.Eliminate()

    def LClickUP(self):
        if self.highlight != -1:
            B.textbox = True
            B.textboxchoice = copy.deepcopy(self.highlight)
            B.textboxtext = ""

        self.leftclick = False


#ENTITIES ======================
class Rocket:
    def __init__(self, disp, alt, overide):
        #simulation
        self.disp = [disp, alt]
        self.startdisp = B.startdisp
        self.coord = [B.groundcoord[0] + disp, B.groundcoord[1] - alt]

        #deg
        self.deg = 180
        self.degbounds = [120, 240]

        #states
        self.success = False #if land successfully
        self.tested = False #if able to procceed to next gen
        self.dieearly = False #is eliminated before touching the ground

        #mechanics
        self.s = [0,0]
        self.u = [0,0]
        self.a = [0,0]
        self.t = [0,0]
        self.m = 1
        self.strength = 0.006
        self.maxu = 3
        self.r = self.strength/(self.maxu**2)
        self.scoreu = 0

        #images
        self.ignite = pygame.image.load("images\\rockets\\ignite.png").convert_alpha()
        self.idle = pygame.image.load("images\\rockets\\dormant.png").convert_alpha()
        self.dead = pygame.image.load("images\\rockets\\failed.png").convert_alpha()
        self.hidden = pygame.image.load("images\\rockets\\hidden.png").convert_alpha()
        self.complete = pygame.image.load("images\\rockets\\complete.png").convert_alpha()
        self.image = self.idle
        self.result = self.image
        if overide:
            self.hide = False

        #dimensions
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.dim = [self.width, self.height]

        #smoke
        self.time = 0

        #neural networking
        if overide:
            self.Nn = neu.NeuralNet()

        #outline
        self.outline = pygame.image.load("images\\rockets\\outline.png").convert_alpha()
        self.odim = [0, 0]
        self.oblit = [0, 0]
        self.oresult = self.outline
        self.highlighted = False

    def Calc(self):
        #AI
        self.Ai()

        #process
        self.CalcSuvat()

        #rotate
        self.result = pygame.transform.rotate(self.image, self.deg)
        self.width = self.result.get_width()
        self.height = self.result.get_height()
        self.dim = [self.width, self.height]

        #highlight
        self.oresult = pygame.transform.rotate(self.outline, self.deg)
        self.odim = [self.oresult.get_width(), self.oresult.get_height()]

        #cull
        if self.disp[1] > (self.startdisp[1]+50) or abs(self.disp[0]) > abs(self.startdisp[0])+10:
            self.dieearly = True
            self.Eliminate()

    def CalcSuvat(self):
        #find resistance
        r = []
        for i in range(2):
            r.append(self.r * self.u[i] * abs(self.u[i]))

        #find f
        f = [self.t[0] - r[0], self.t[1] + B.g - r[1]]

        #find a
        for i in range(2):
            self.a[i] = f[i]/self.m

        #find s
        for i in range(2):
            self.s[i] = self.u[i] - (0.5*self.a[i])

        #displace
        self.disp[0] -= self.s[0]
        self.coord[0] -= self.s[0]
        if self.disp[1] - self.s[1] > 0:
            self.disp[1] -= self.s[1]
            self.coord[1] += self.s[1]
        else: #hit ground
            self.HitGround()

    def Reset(self):
        #find velocity used in next Calculate (v = u + at)
        for i in range (0,2):
            self.u[i] = self.u[i] + self.a[i]

            #reset values
            self.t[i] = 0
        
        if self.hide:
            self.image = self.hidden
        else:
            self.image = self.idle

    def Ai(self):
        #inputs
        rawinputs = [self.disp[0], self.disp[1], self.u[0], self.u[1], self.deg-180]
        bounds = [[-self.startdisp[0], self.startdisp[0]], [0, self.startdisp[1]], [-self.maxu, self.maxu], [-self.maxu, self.maxu], self.degbounds]

        #process
        inputs = []
        for i in range(len(rawinputs)):
            inputs.append( ((rawinputs[i] - bounds[i][0])/bounds[i][1]) -1)

        #export
        result = self.Nn.Forward([inputs])

        #outputs
        #ignition
        if result[0] > 0:
            self.Ignite()

        #turning
        if result[1] > 0:
            #turn left
            self.Turn(True)
        elif result[2] > 0:
            #turn right
            self.Turn(False)

    def Ignite(self):
        rad = math.radians(self.deg)

        opp = self.strength * math.sin(rad)
        adj = self.strength * math.cos(rad)
        self.t[0] = -opp
        self.t[1] = adj

        #show
        if not self.hide:
            self.image = self.ignite
            if B.particleshow:
                self.SmokeGen()

    def Turn(self, left):
        if left:
            self.deg += 1
        else:
            self.deg -= 1

        if self.deg < self.degbounds[0]:
            self.deg = copy.deepcopy(self.degbounds[0])
        elif self.deg > self.degbounds[1]:
            self.deg = copy.deepcopy(self.degbounds[1])

    def HitGround(self):
        if self.u[0] > 1 or self.u[1] > 1:
            #crash
            self.Eliminate()
        else:
            if P.coord[0] < self.coord[0] < P.coord[0]+P.width:
                #landed successfully
                self.Success()
            else:
                #not on platform
                self.Eliminate()
            
        self.disp[1] = 0 
        self.coord[1] = B.groundcoord[1]

    def Eliminate(self):
        self.tested = True
        self.success = False
        self.image = self.dead
        self.result = pygame.transform.rotate(self.image, self.deg)
        self.scoreu = copy.deepcopy(self.u[1])

        #effects
        if B.particleshow and not self.hide:
            self.Explosion()

    def Success(self):
        #success
        self.tested = True
        self.success = True
        self.image = self.complete
        self.scoreu = copy.deepcopy(self.u[1])
        self.u = [0, 0]
        self.deg = 180

    def Show(self): 
        #locate
        blit = [0,0]
        for i in range(2):
            blit[i] = self.coord[i] - self.dim[i]/2

        #outline
        if self.highlighted:
            self.oblit = [0,0]
            for i in range(2):
                self.oblit[i] = self.coord[i] - self.odim[i]/2

            window.blit(self.oresult, self.oblit)

        #export
        window.blit(self.result, blit)

    def SmokeGen(self):
        #smoke
        self.time += 1
        if self.time % 3 == 0:
            rad = math.radians(self.deg+180)
            change = [20 * math.sin(rad), 20 * math.cos(rad)]
            coord = [self.coord[0]+ change[0], self.coord[1]+ change[1]]
            B.particles.append(Smoke(coord, self.deg))

    def Explosion(self):
        for _ in range(20):
            B.particles.append(Smoke(self.coord, random.randint(0,360)))

class Pad:
    def __init__(self):
        #images
        self.neutral = pygame.image.load("images\\pad\\dormant.png")
        self.flash = pygame.image.load("images\\pad\\flash.png")
        self.image = self.neutral

        #details
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.coord = [B.groundcoord[0] - (self.width/2), B.groundcoord[1]]
        self.time = 300

        #rect
        self.rectC = (96,96,96)
        self.belowrect = self.coord[0], self.coord[1]+self.height/2, self.width, scr_height-self.coord[1]
    
    def Show(self):
        self.time -= 1

        if self.time < 0:
            if self.image == self.neutral:
                self.image = self.flash
                self.time = 15
            else:
                self.image = self.neutral
                self.time = 200
        window.blit(self.image, self.coord)

        pygame.draw.rect(window, self.rectC, self.belowrect)


#PARTICLES ======================
class Smoke:
    def __init__(self, coord, deg):
        coord = copy.deepcopy(coord)
        self.coord = [coord[0] + random.randint(-5, 5), coord[1] + random.randint(-5, 5)]
        self.colour = (73,73,73)
        self.size = random.randint(8,10)
        self.vel = random.uniform(0.5,1)
        self.deg = deg+180

    def Calc(self):
        #displace
        pythag = [0,0]
        rad = math.radians(self.deg)
        pythag[0] = self.vel * math.sin(rad)
        pythag[1] = self.vel * math.cos(rad)

        #export
        for i in range(2):
            self.coord[i] += pythag[i]

        #entropy
        self.size -= .1
        if self.size <= 0:
            B.particles.remove(self) 

    def Show(self):
        pygame.draw.circle(window, self.colour, (int(self.coord[0]), int(self.coord[1])), int(self.size), 0)


import neural4 as neu


B = Board()
M = Mouse()
P = Pad()


#init rockets
##B.startdisp = [random.randint(-B.spawnlimit[0],B.spawnlimit[0]), random.randint(B.spawnlimit[1],B.spawnlimit[2])]
B.startdisp = [-250, 500]
for _ in range(B.gensize):
    B.rockets.append(Rocket(B.startdisp[0], B.startdisp[1], True))
R = B.rockets[0]##
B.deathbox = B.groundcoord[0] - abs(B.startdisp[0]) - 10, B.groundcoord[1] - abs(B.startdisp[1]) -50, abs(B.startdisp[0])*2+20, abs(B.startdisp[1])+50

while B.RUN:
    pygame.time.delay(1)
    window.fill(B.backC)
    
    #input
    if B.textbox:
        B.Textbox()
    else:
        M.Input()
    for i in B.rockets:
        if not i.tested:
            i.Calc()
    if B.particleshow:
        for i in B.particles:
            i.Calc()

    #show
    P.Show()
    B.Show()
    for i in B.rockets:
        if ((B.failureshow or not i.tested) and not i.hide) or i.success:
            i.Show()
    if B.particleshow:
        for i in B.particles:
            i.Show()

    #reset
    for i in B.rockets:
        if not i.tested:
            i.Reset()
    B.GenMonitor()

    pygame.display.update()