# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 01:55:06 2018

@author: Kieran
"""

#cockroach card game simulator

#cards are 0-7, deck has 64 cards (8 each)
#Decision: start - player chooses card in hand, passes to other player with hidden card type and bluff
#Then either pass card to next player with bluff
#or assert true or falsity of statement, guessing correctly gives card back
#play begins again with person who took card
#having no card to play or 4 of a kind is a loss

#hypotheses: There is little information given in the game, odds are always basically 50/50
#If players gang up on another and always give them cards or call their bluff, that person will lose in short order
#number of cards in player's hand and cards in their  inventory are useful information, bluffs contain no information
#If a player has 3 of a card, bluffs of that card should always be yessed
#prioritize playing cards that others have and you do not have
#no player should play a card they own 3 of, therefore if someone bluffs this always no the bluff

#playstyles: Always call yes, always call no, always call random
#always lie (random/specific), always tell the truth, 50/50 true/random, pure random
#always pass (when possible) or random pass or call
#pass to random player, or specific player

#sanity check: all players being random, each should win 1/n

#classes: player

import numpy as np
import time
import random

class Player(object):
    opt = ['pass','call']
    
    def __init__(self, num, hand, playstyle):
        """ p_decide (0 50/50) (1 always pass) (2 always call)
        p_call   (0 50/50) (1 always yes) (2 always no)
        p_bluff  (0 pure random) (1 50/50 true/random) (2 always true) 
                 (3 always lie random) (4 always lie specific)
        p_target (0 random) (1 specific)
        p_pass   (0 random) (1 prefer not in inventory)
                 (2 prefer in inv of others) (3 rule 1 then rule 2)
                 (4 rule 2 then rule 1) """
        self.num = num
        #self.inventory = np.array([0]*8)
        self.hand = np.array(hand)
        
        #playstyles
        self.p_decide = playstyle[0]
        self.p_call = playstyle[1]
        self.p_bluff = playstyle[2]
        self.p_target = playstyle[3]
        self.p_pass = playstyle[4]

    def bluff(self, to_pass):
        
        #pure random
        if (self.p_bluff == 0):
            return int(np.random.rand()*8)
        
        #50/50 true/random
        elif (self.p_bluff == 1):
            if (int(np.random.rand()*2) == 0):
                bluff = int(np.random.rand() * 7)
                bluff = 7 if bluff==to_pass else bluff
            else:
                bluff = to_pass
            return bluff
            
        else:
            print('unimplemented playstyle')
        
    def Pass(self, card, invs): 
        #choose a card in inventory to pass
        #call bluff with passed card
        #return bluff and card and target
        target = None  
        
        if (card == None):
            if (self.hand.size > 1):
                
                #random
                if (self.p_pass == 0):
                    card, self.hand = self.hand[-1], self.hand[:-1]
               
                #prefer not in hand
                if (self.p_pass == 1):
                    min_inv = 4
                    for c in self.hand:
                        if invs[self.num,c] < min_inv:
                            min_inv = invs[self.num,c]
                            card = c
                            if min_inv == 0: break  #unsure this makes a difference
                    
                #prefer in others inv
                if (self.p_pass == 2):
                    u_hand = np.unique(self.hand)
                    max_inv = 0
                    card = u_hand[0]
                    for c in u_hand:
                        for i in random.sample(range(0,8),(8 - 0)):
                            if (i != self.num and invs[i,c] > max_inv):
                                max_inv = invs[i,c]
                                card = c
                                target = i
                                if max_inv == 3: break
                        if max_inv == 3: break
                    
            else:
                card = self.hand
                self.hand = []
                
        bluff = self.bluff(card)
        return target, card, bluff
        
    def target(self,target_list,card,invs): #valid targets how?
        target, card, bluff = self.Pass(card, invs)
        
        if (target == None):   #allows override for some passing playstyles
            #random
            if (self.p_target == 0):
                target = target_list[int(np.random.rand() * target_list.size)]
                
            elif (self.p_target == 1) :
                if np.in1d(0,target_list):
                    target = 0
                else:
                    target = target_list[int(np.random.rand() * target_list.size)]
                
            else:
                print('unimplemented playstyle')
        
        return target, card, bluff
        
    def call(self,bluff):
        
        #50/50
        if (self.p_call == 0):
            return int(np.random.rand()*2)
    
        #always yes
        elif (self.p_call == 1):
            return 1
        
        #always no
        elif (self.p_call == 2):
            return 0
        
        else:
            print('unimplemented playstyle')
        
    def decide(self,bluff):  #returns 'call' or 'pass'
        
        #50/50
        if (self.p_decide == 0):
            return self.opt[int(np.random.rand()*2)]
        
        #always pass
        elif (self.p_decide == 1):
            return self.opt[0]
        
        #always call
        elif (self.p_decide == 2):
            return self.opt[1]
        
        else:
            print('unimplemented playstyle')
        #implement pass
        
        
    
def simulate(conditions):
    #make hands
    hands = np.arange(8).repeat(8)
    invs = np.zeros((8,8))
    np.random.shuffle(hands)
    hands = hands.reshape(8,8)
    
    players = []
    for i in range(8):
        players.append(Player(i,hands[i],conditions[i]))
        
    #keep bluff history
    #make sure you can't pass at the end
        
    start = int(np.random.rand() * 8)
    target_list = np.append(np.arange(0,start),np.arange(start+1,8))
    card = None
    while(True):
        
        target, card, bluff = players[start].target(target_list,card,invs)
        if (target_list.size == 1):
            choice = 'call'
        else:
            choice = players[target].decide(bluff)
            
        if (choice == 'call'):  #given yes/no call
            call = players[target].call(bluff)
            if (call == 0 and bluff == card or call == 1 and bluff != card):
                invs[target,card] += 1
                if (invs[target,card] == 4 or len(players[target].hand) == 0): #game over
                    return target #the loser
                start = target
                target_list = np.append(np.arange(0,start),np.arange(start+1,8))
                card = None
            else:
                invs[start,card] += 1
                if (invs[start,card] == 4 or len(players[start].hand) == 0): #game over
                    return start #the loser
                #start stays the same
                target_list = np.append(np.arange(0,start),np.arange(start+1,8))
                card = None
                
        elif (choice == 'pass'):
            target_list = np.delete(target_list,np.where(target_list==target))
            #call next thing being passed with card
            start = target
            

if __name__ == '__main__':
    """ p_decide (0 50/50) (1 always pass) (2 always call)
        p_call   (0 50/50) (1 always yes) (2 always no)
        p_bluff  (0 pure random) (1 50/50 true/random) (2 always true) 
                 (3 always lie random) (4 always lie specific)
        p_target (0 random) (1 specific)
        p_pass   (0 random) (1 prefer not in inventory)
                 (2 prefer in inv of others) (3 rule 1 then rule 2)
                 (4 rule 2 then rule 1) """
    losses = np.zeros(8)
    t = time.time()
    
    #players = [2,0,0,0]*8  #initial conditions
    #players = [[2,0,0,0]]*4+[[2,0,0,1]]*4  #half pure random, half 50/50 true/random
    players = [[1,0,1,0,1]]*4+[[1,0,1,0,2]]*4
    
    p = '[[1,0,1,0,1]]*4+[[1,0,1,0,2]]*4' + '\n'
    
    for i in range(10000):
        losses[simulate(players)] += 1
    print(p, losses, '\n', time.time() - t)
    
    
    
    
    
    
    
    
    
    
    