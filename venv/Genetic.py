import numpy as np
from Game import Game
import random
#Tahtanın boyutları
Border_X=10
Border_Y=10
#kaç tane meyve var
FruitNum=10
#popülasyon boyutu
PopulationSize=200
#bireylerin adım sayıları
StepSize=100
#mutasyon şansı
MutationChance=0.1
#Selectionda alacağımız iyi birey yüzdesi
SelectedSize=0.2
#kaç tane elit birey bir sonraki generasyona aktarılacak
Elite_number=2


class Chromosome:
    # Her bir bireyi gösteren class
    def __init__(self,Direction,Game):
        self.Game=Game
        #bu bireyin temsil ettiği yol
        self.Direction=Direction.copy()
        #oyuncuların yaratılması
        self.Game.CreatePlayers(1)
        #Kullanılan yolun döndürdüğü sonuçlar
        Scores, FStatus, DStatus,eaten = self.Game.Execute(Direction)
        self.Score=Scores[0]
        #Oyunu oynarken öldü mü
        self.Dead=DStatus[0]
        #Oyunu bitirdi mi
        self.FStatus=FStatus[0]
        #Oyun sırasında kaç tane meyve yedi
        self.Eaten=eaten


class Population:
    #Bütün Bireyleri temsil eden class
    def __init__(self,Directions,Game):
        self.Game=Game
        self.Chromosomes=[]
        for i in range(PopulationSize):
            self.Chromosomes.append(Chromosome(Directions[i],self.Game))
        self.Chromosomes.sort(key=lambda x: x.Score,reverse=True)
    def _printPop(self):
        #Popülasyonun en iyi 5 üyesinin yazdırılması
        count=0
        for chromo in self.Chromosomes:
            print("Chromosome: ",count," Score: ",chromo.Score," Eaten: ",chromo.Eaten," Finished: ",chromo.FStatus," Dead: ",chromo.Dead)
            count+=1
            if count==5:
                break
    def anyFinished(self):
        #bu popülasyondan kimse oyunu bitirdi mi
        for chro in self.Chromosomes:
            if chro.FStatus==True:
                return True
        return False

def Selection(Population):
    #Popülasyondaki en iyi %SelectedSize'ın seçilmesi
    Directions=[]
    Fittest=Population.Chromosomes[0:int(PopulationSize*SelectedSize)]
    for fit in Fittest:
        #Bu seçilen bireylerin sadece yön bilgisini alıyorum
        Directions.append(fit.Direction.copy())
    return Directions


def CrossOver(directions):
    #Selectionda seçilen bireylerden popülasyonun geri kalanının oluşturulması
    offspring = []
    tmp = int(SelectedSize * PopulationSize)
    for _ in range(int((PopulationSize-tmp-Elite_number)/2)):
        #random bir parent seçiliyor
        parent1_ind=np.random.randint(0,tmp,1)[0]
        parent1 =directions[parent1_ind]
        parent2_ind=np.random.randint(0,tmp,1)[0]
        #ikinci parent birinci parentla aynı olmadığı kontrol ediliyor
        while parent1_ind==parent2_ind:
            parent2_ind = np.random.randint(0, tmp, 1)[0]
        parent2 = directions[parent2_ind]
        child1 = []
        child2 = []
        #bu iki parent'ın birleşmesini istediğimiz bir split noktası seçiliyor
        split = np.random.randint(1,StepSize-5,1)[0]
        child1 =np.concatenate((parent1[:split].copy(),parent2[split:].copy()),0)
        child2 = np.concatenate((parent2[:split].copy(), parent1[split:].copy()))
        #ve enson bu çocuklar saklanıyor
        offspring.append(child1)
        offspring.append(child2)
    directions.extend(offspring)
    return directions

def Mutation(directions):
    #belirli bir oran için mutasyon gerçekleştirilmesi
    for direction in directions:
        #bir bireyin bütün yönleri için mutasyon ihtimali var
        for i in range(len(direction)):
            if random.uniform(0.0, 1.0) <= MutationChance:
                Value=random.randint(1, 4)
                if i != 0:
                    #mutasyonda yeni çıkacak olan bireyin hem orijinaldeğerle aynı olmaması hemde bir önceki adımdan geri dönmemesi sağlanıyor.
                    while Value == direction[i] or (Value - 2) % 4 == direction[i - 1] % 4:
                        Value = random.randint(1, 4)
                    direction[i] = Value
                else:
                    while Value == direction[i]:
                        Value = random.randint(1, 4)
                    direction[i] = Value
    return directions

def FindOddOnes(Directions):
    #bir yön arrayinde ileri geri hareketin olup olmadığının kontrol edilmesi ve bunun giderilmesi
    for direction in Directions:
        for i in range(1,StepSize):
            if (direction[i] - 2) % 4 == direction[i - 1] % 4:
                tmp=np.random.randint(1,5,1)[0]
                while tmp==direction[i]:
                    tmp = np.random.randint(1, 5, 1)[0]
                direction[i]=tmp


def Genetic(game):
    #algoritmanın çalıştırıldığı function
    Directions=np.random.randint(1,5,(PopulationSize,StepSize))
    #direction random olarak init ediliyor
    FindOddOnes(Directions)
    #bu random matriste ileri geri hareket siliniyor
    Pop = Population(Directions, game)
    count=1
    while Pop.anyFinished()==False:
        #Popülasyonda bitiren olmadığı sürece devam ediyor
        new_Directions=Selection(Pop)
        new_Directions=CrossOver(new_Directions)
        FindOddOnes(new_Directions)
        #cross over sonucunuda ileri geri hareket için kontrol ediyoruz
        new_Directions=Mutation(new_Directions)
        for i in range(Elite_number):
            #belirlenen elite_number için şu anki popülasyonun en iyilerinin hiç bir işleme sokmadan bir sonraki generasyona atıyoruz
            new_Directions.append(Pop.Chromosomes[i].Direction)

        Pop=Population(new_Directions,game)
        #Popülasyonu yazdırıyoruz
        print("===========",count,"===========")
        count+=1
        Pop._printPop()
        if count%25 ==0:
            #her 50 adımda oyun üzerinden en iyi bireyin hareketlerini gösteriyoruz
            game.ShowMax(Pop.Chromosomes[0].Direction,count)
    for chro in Pop.Chromosomes:
        #bir birey bitirdiğinde bitiren bireyin oyununu gösteriyoruz
        if chro.FStatus==True:
            game.ShowMax(Pop.Chromosomes[0].Direction,0)
            break

    return count



if __name__=="__main__":
    game=Game(Border_Y,Border_X,FruitNum)
    Genetic(game)