import numpy as np

from . import LEFTranslocator

        
class LEFTranslocatorDynamicBoundary(LEFTranslocator.LEFTranslocator):
     
    def __init__(self,
                 numLEF,
                 birthProb,
                 deathProb,
                 stalledDeathProb,
                 pauseProb,
                 stallProbLeft,
                 stallProbRight,
                 ctcfBirthProb,
                 ctcfDeathProb,
                 *args):
        
        self.ctcfBirthProb = ctcfBirthProb
        self.ctcfDeathProb = ctcfDeathProb

        self.stallProbLeft_init = np.copy(stallProbLeft)
        self.stallProbRight_init = np.copy(stallProbRight)

        super().__init__(numLEF,
                         birthProb,
                         deathProb,
                         stalledDeathProb,
                         pauseProb,
                         stallProbLeft,
                         stallProbRight)


    def CTCF_birth(self):
    
        for i in range(self.numSite):
            if self.stallProbLeft[i] != self.stallProbLeft_init[i]:
                if np.random.random() < self.ctcfBirthProb[i]:
                    self.stallProbLeft[i] = self.stallProbLeft_init[i]
                    
            if self.stallProbRight[i] != self.stallProbRight_init[i]:
                if np.random.random() < self.ctcfBirthProb[i]:
                    self.stallProbRight[i] = self.stallProbRight_init[i]
                    
                    
    def CTCF_death(self):
    
        for i in range(self.numSite):
            if self.stallProbLeft[i] != 0:
                if np.random.random() < self.ctcfDeathProb[i]:
                    self.stallProbLeft[i] = 0
                    
                    for j in range(self.numLEF):
                        if i == self.LEFs[j, 0]:
                            self.stalled[j, 0] = 0
                    
            if self.stallProbRight[i] != 0:
                if np.random.random() < self.ctcfDeathProb[i]:
                    self.stallProbRight[i] = 0
                    
                    for j in range(self.numLEF):
                        if i == self.LEFs[j, 1]:
                            self.stalled[j, 1] = 0
                        
                                
    def step(self):
    
        self.CTCF_death()
        self.CTCF_birth()
        
        super().step()
