import numpy as np


class LEFTranslocator():
    
    def __init__(self,
                 numLEF,
                 birthProb,
                 deathProb,
                 stalledDeathProb,
                 pauseProb,
                 stallProbLeft,
                 stallProbRight,
                 *args):
    
        self.numSite = len(birthProb)
        self.numLEF = numLEF
        
        self.birthProb = birthProb
        self.deathProb = deathProb
        
        self.stallProbLeft = stallProbLeft
        self.stallProbRight = stallProbRight

        self.pause = pauseProb
        self.stalledDeathProb = stalledDeathProb

        self.LEFs = np.zeros((self.numLEF, 2), dtype=int) - 1
        
        self.stalled = np.zeros((self.numLEF, 2), dtype=int)
        self.occupied = np.zeros(self.numSite, dtype=int)
        
        self.occupied[0] = self.occupied[-1] = 1

        self.LEF_birth()


    def LEF_birth(self):
    
        for i in range(self.numLEF):
            if np.all(self.LEFs[i] == -1):
                while True:
                    pos = np.random.randint(1, self.numSite-1)
            
                    if self.occupied[pos] == 0:
                        if np.random.random() < self.birthProb[pos]:
                            self.LEFs[i] = pos
                            self.occupied[pos] = 1
                    
                            if (pos < (self.numSite - 2)) and (self.occupied[pos+1] == 0):
                                if np.random.random() > 0.5:
                                    self.LEFs[i, 1] = pos + 1
                                    self.occupied[pos+1] = 1
                        
                        break


    def LEF_death(self):
    
        for i in range(self.numLEF):
            if np.all(self.LEFs[i] >= 0):
                if self.stalled[i, 0] == 0:
                    deathProb1 = self.deathProb[self.LEFs[i, 0]]
                else:
                    deathProb1 = self.stalledDeathProb[self.LEFs[i, 0]]
                    
                if self.stalled[i, 1] == 0:
                    deathProb2 = self.deathProb[self.LEFs[i, 1]]
                else:
                    deathProb2 = self.stalledDeathProb[self.LEFs[i, 1]]
                
                deathProb = max(deathProb1, deathProb2)
                
                if np.random.random() < deathProb:
                    self.stalled[i] = 0
                    self.occupied[self.LEFs[i]] = 0
                    
                    self.LEFs[i] = -1
        

    def LEF_step(self):
    
        for i in range(self.numLEF):
            if np.all(self.LEFs[i] >= 0):
                stall1 = self.stallProbLeft[self.LEFs[i, 0]]
                stall2 = self.stallProbRight[self.LEFs[i, 1]]
                                        
                if np.random.random() < stall1:
                    self.stalled[i, 0] = 1
                if np.random.random() < stall2:
                    self.stalled[i, 1] = 1
                             
                cur1, cur2 = self.LEFs[i]
                
                if self.stalled[i, 0] == 0:
                    if self.occupied[cur1-1] == 0:
                        pause1 = self.pause[cur1]
                        
                        if np.random.random() > pause1:
                            self.occupied[cur1 - 1] = 1
                            self.occupied[cur1] = 0
                            
                            self.LEFs[i, 0] = cur1 - 1
                            
                if self.stalled[i, 1] == 0:
                    if self.occupied[cur2 + 1] == 0:
                        pause2 = self.pause[cur2]
                        
                        if np.random.random() > pause2:
                            self.occupied[cur2 + 1] = 1
                            self.occupied[cur2] = 0
                            
                            self.LEFs[i, 1] = cur2 + 1
            
        
    def step(self):
    
        self.LEF_death()
        self.LEF_birth()
        
        self.LEF_step()
        
    
    def steps(self, N):
    
        for _ in range(N):
            self.step()
