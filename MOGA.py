#------------------------------------------------------------------------------+
#   CHIA E TUNGOM
#   Genetic Algorithm for TSA 
#   March, 2020
#------------------------------------------------------------------------------+

import random
import numpy as np
import time

def Initialize(pop, dim):
    
    population = []
    i = 0
    
    while len(population) < pop and i < 100:       # i helps to terminate while loops if population keeps repeating:
        chromosome = []
        
        while len(chromosome) < dim:
            a = int(random.uniform(0,dim))
            
            if a not in chromosome:
                chromosome.append(a)
                
        # dont allow repetition of same chromosome        
        if chromosome in population:
            print("IGNORING......: ", chromosome)
            i += 1
        else:
            population.append(chromosome)
        
        
    return population

# calculate cost of each route
def Cost(Pop, Cmatrix):
    Cvector = []
    
    for i in range(len(Pop)):
        route = Pop[i]
        cost = 0
        
        for j in range(len(route)-1):
            cost += Cmatrix[route[j]][route[j+1]]
        cost += Cmatrix[route[0]][route[len(route)-1]]   
        Cvector.append(cost)
        
    return Cvector

# Sort Chromosomes from Best to Worst
def Sortpop(Pop, Cmatrix):
    cost = Cost(Pop, Cmatrix)
    ans = [ x for _,x in sorted(zip(cost, Pop))]
    #cost = [ _ for _,x in sorted(zip(cost, Pop))]  # need be to use the true cost
    return ans


# fitness function 1
def F1(sortedpop):
    bb= 0.3
    
    F = []   
    for i in range(1,len(sortedpop)+1):
        F.append( bb * ( (1-bb)**(i-1) ) )
        
    return F

# fitness function 1
def F2(sortedpop):
    n = len(sortedpop)
    
    F = []
    for i in range(1,n+1):
        F.append( (n-i+1)/n )
        
    return F

# Calculate the probability 
def Pi(fitness):
    n = len(fitness)
    ans = []
    
    for i in range(n):
        ans.append( fitness[i]/sum(fitness) )
        
    return ans

# Calculate cumulative sum for roulette wheel 
def PPi(pi):
    n = len(pi)
    ans = []
    
    for i in range(n):
        ans.append( sum([i for i in pi[:i+1]]) )
    return ans 

# Roulette Wheel 
def Roulette(ppi, Pop):
    n = len(ppi)
    ra = random.random()
    
    for i in range(n):
        if i == 0 :
            if ra > 0 and ra < ppi[i]:
                return Pop[i]
        else:
            if ra > ppi[i-1] and ra < ppi[i]:
                return Pop[i]
            
# Select 2 Intersection points 
def p1p2(chromosome):
    n= len(chromosome)
    P1, P2 = 0, 0
    
    while P1 == P2 or P2 - P1 < 1:  # can allow us to also set a minimum space between two points (here its 2)
        P1 = random.randint(1,n) #only n-2 slicing spaces available 
        P2 = random.randint(1,n)
        
        if P1>P2:
            P1, P2 = (P2, P1)
        
        #print("Running")
    return (P1, P2)   


# CrossOver
def Crossover(Pop, PPi):
    
    p1, p2 = p1p2(Pop[0])
    #A, B = 0,0
    #while A == B:
    A = Roulette(PPi, Pop) ; B = Roulette(PPi, Pop)
    
    fA = A[ :p1] ; mA = A[p1:p2] ; lA = A[p2: ]
    fB = B[ :p1] ; mB = B[p1:p2] ; lB = B[p2: ]
    
    # rotate 3rd section to beginning 
    Ao = lA + A[ :p2] ; Bo = lB + B[ :p2] 
    
    # Delete middles from other chromosomes
    [Ao.remove(i) for i in mB] ; [Bo.remove(i) for i in mA]
    
    fAo = Ao[:len(lA)] ; fBo = Bo[:len(lB)]
    
    # Take first k elements where k is the length of the last section in the start, 
    # move them to end of list. Bring the middle of B
    # to Ao  and verse vers, Produce first set of offsprings

    oA = Ao[len(fAo):] + mB + fAo ; oB = Bo[len(fBo):] + mA + fBo
    
    # Nother set of 2 More offsprings
    # Exchange section 1 and 2 of A, do same for B

    Ao1 = mA + fA + lA ; Bo1 = mB + fB + lB
    
    # Delete middles from other chromosomes
    [Ao1.remove(i) for i in lB] ; [Bo1.remove(i) for i in lA]
    # Exchange the 3rd sections of both A and B
    oA1 = Ao1[:p2] + lB ; oB1 = Bo1[:p2] + lA 
    
    #print([oA, oB, oA1, oB1])
    return [oA, oB, oA1, oB1]

def Mutation(offsprings, pm):
    # an offspring is mutated with probability pm
    # To mutate, select mutation points same as p1 and p2 and flip the order 
    
    
    Mutated = []
    for i in offsprings:
        if random.random() < pm:
            p1, p2 = p1p2(i)
            moA = i[p1:p2]
            moA.reverse()
            Mi = i[ :p1] + moA + i[p2: ]
        
            Mutated.append(Mi)
        else:
            Mutated.append(i)
        
    return Mutated


def GA(population, dimension, CM, runs = 50):
    
    Start = time.time()
    
    X = Initialize(population, dimension)
    
    pm = 0.3
    k = 5                 # number of elites
    lim = 150
    
    l=0
    i = 0
    while i < runs:
        
        sX = Sortpop(X, CM)
        elites = sX[:k]
        sX = sX[ :population]
        
        if i%2 == 0:
            f1 = F2(sX)
        else:
            f1 = F1(sX)
            
        P = Pi(f1)
        PP = PPi(P)
        X = []
        
        cost1 = Cost(sX, CM)[0]
        for j in range(int(len(sX)/2)):
            OV = Crossover(sX, PP)
            OM = Mutation(OV, pm)
            #X += OM
            for _ in OM:
                X.append(_)
        i += 1
        X += elites
        
        X = Sortpop(X, CM)
        cost2 = Cost(X, CM)[0]
        if cost1 <= cost2:
            l += 1
            if l == lim:
                #print(time.time() - Start, "seconds")
                return cost1, i , time.time() - Start
        else:
            l = 0
            
    #print(time.time() - Start, "seconds")
    
    sX = Sortpop(X, CM)
    cost = Cost(sX, CM)
    return cost[0], i, time.time() - Start