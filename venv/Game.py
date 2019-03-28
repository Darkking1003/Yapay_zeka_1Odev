import pygame
from pygame.locals import *
import numpy as np
newGame=True
loggedIn=False
miniGame=False
import time
import itertools

class Player:
#oyunu oynayacak olan class
    def __init__(self,x,y,Border_x,Border_y,width,height,Fruits):
        self.image = pygame.image.load("pygame.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.FruitImg=pygame.image.load("Fruit.png")
        self.FruitImg = pygame.transform.scale(self.FruitImg, (width, height))
        #player coordintları
        self.player_x=x
        self.player_y=y
        #tahtanın sınırlar
        self.X_Limit=Border_x-1
        self.Y_Limit=Border_y-1
        #meyvelerin yerleri
        self.Fruits=Fruits.copy()
        #status ve score
        self.Dead=False
        self.Finished=False
        self.Score=0
        #şuana kadar attığı adım
        self.Step=0
        #yediği meyve sayısı
        self.Eating=0

    def move_left(self):
        self.player_x-=1
    def move_right(self):
        self.player_x+=1
    def move_up(self):
        self.player_y-=1
    def move_down(self):
        self.player_y+=1

    def Move(self,Direction):
        #hareket edilen kısım
        if self.Dead==True:
            #ölüyse oynama
            return
        if Direction == 1:
            self.move_left()
        if Direction==2:
            self.move_up()
        if Direction==3:
            self.move_right()
        if Direction==4:
            self.move_down()
        self.Step+=1
        if self.player_x<0 or self.player_y<0 or self.player_x>self.X_Limit or self.player_y>self.Y_Limit:
            #öldümü diye kontrol edilmesi
            self.player_x=0
            self.player_y=0
            self.Dead=True
            return
        self.CheckIfEating()
        #meyve yedimi
        if len(self.Fruits)==0:
            #bitti mi
            self.Finished=True
            print("Bitti")

    def Convert(self):
        self.image=self.image.convert_alpha()
        self.FruitImg=self.FruitImg.convert_alpha()
    def CheckIfEating(self):
        if (self.player_y,self.player_x) in self.Fruits:
            #eğer meyve yediyse
            self.Fruits.remove((self.player_y,self.player_x))
            #meyveyi oyun tahtasından sil
            self.Eating+=1
            katsayı=0.15
            #score'u arttır
            self.Score+=1000+1000/np.exp(self.Step*katsayı)

class Game():
    #oyun tahtası
    margin=0
    xDistanceFromEdge=100
    black=(0,0,0)
    white=(255,255,255)
    greyBackground=(203, 206, 203)
    width=65
    height=65
    def __init__(self,BoardRow,BoardCol,NumberofFruits):
        self.BoardRow=BoardRow
        self.BoardCol=BoardCol
        self.Fruits=NumberofFruits
        self.gameBoard=[[None]*BoardCol for i in range(BoardRow)]
        self.BoardCoord=np.ndarray((BoardRow,BoardCol,2))
        self.windowSize=[self.BoardCol*self.width,self.BoardCol*self.height]
        self.FindRectCorrd()
        self.FruitCoords=self.DistrubuteFruits()

    def CreatePlayers(self,numPopulation):
        #oyuncuların yaratılması
        self.Player = []
        self.Pop=numPopulation
        self.Scores=[]
        self.FStatus=[]
        self.DStatus=[]
        for i in range(self.Pop):
            self.Player.append(Player(round(self.BoardCol / 2), round(self.BoardRow / 2), self.BoardCol, self.BoardRow, self.width, self.height,self.FruitCoords))

    def DistrubuteFruits(self):
        #meyvelerin yerleştirilmesi
        pairs=list(itertools.product(range(self.BoardRow),range(self.BoardCol)))
        pairs.remove((round(self.BoardRow/2),round(self.BoardCol/2)))
        np.random.shuffle(pairs)
        FruitLocation=pairs[:self.Fruits]
        return FruitLocation

    def UpdateScreen(self,Player):
        #ekranın güncellenmesi
        pygame.event.pump()
        self.screen.fill(self.greyBackground)
        self.boardGui()
        self.screen.blit(Player.image,self.BoardCoord[Player.player_y][Player.player_x])
        for fruit in Player.Fruits:
            self.screen.blit(Player.FruitImg,self.BoardCoord[fruit[0]][fruit[1]])
        pygame.display.update()
        time.sleep(0.2)

    def FindRectCorrd(self):
        for boardRow in range(self.BoardRow):
            for boardColumn in range(self.BoardCol):
                xCoordinate=((self.margin+self.width) * boardColumn + self.margin)
                yCoordinate=(self.margin+self.height) * boardRow + self.margin
                self.BoardCoord[boardRow][boardColumn]=(xCoordinate,yCoordinate)

    def boardGui(self):
        for boardRow in range(self.BoardRow):
            for boardColumn in range(self.BoardCol):
                xCoordinate = ((self.margin + self.width) * boardColumn + self.margin)
                yCoordinate = (self.margin + self.height) * boardRow + self.margin

                if boardRow%2==0 and boardColumn%2==0:
                    currentColour = self.black
                if boardRow%2!=0 and boardColumn%2==0:
                    currentColour = self.white
                if boardRow%2==0 and boardColumn%2!=0:
                    currentColour = self.white
                if boardRow%2!=0 and boardColumn%2!=0:
                    currentColour = self.black
                pygame.draw.rect(self.screen,currentColour,[xCoordinate,yCoordinate, self.width, self.height])

    def Execute(self,Directions):
        #verilen yönlere göre oyunun oynanması ve sonuçların dönürülmesi. ekranda gösterilmez
        for i in range(self.Pop):
            for move in Directions:
                self.Player[i].Move(move)
                if self.Player[i].Finished==True or self.Player[i].Dead==True:
                    break

            self.Scores.append(self.Player[i].Score)
            self.FStatus.append(self.Player[i].Finished)
            self.DStatus.append(self.Player[i].Dead)

        return (self.Scores,self.FStatus,self.DStatus,self.Player[0].Eating)


    def ShowMax(self,Directions,iter):
        #verilen directionların ekranda gösterilmesi
        pygame.init()
        self.screen = pygame.display.set_mode(self.windowSize)

        pygame.display.set_caption(str(iter))
        done = False

        self.CreatePlayers(1)
        self.Player[0].Convert()
        self.UpdateScreen(self.Player[0])

        for move in Directions:

            self.Player[0].Move(move)
            self.UpdateScreen(self.Player[0])
            if self.Player[0].Dead==True or self.Player[0].Finished==True:
                break
        pygame.quit()