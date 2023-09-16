import numpy as np


class SymmetricExtruder():
    
    def __init__(self,
                 num_LEF,
                 birth_prob,
                 death_prob,
                 stalled_death_prob,
                 pause_prob,
                 stall_prob_left,
                 stall_prob_right,
                 *args):
    
        self.num_site = len(birth_prob)
        self.num_LEF = num_LEF
        
        self.birth_prob = birth_prob
        self.death_prob = death_prob
        
        self.stall_prob_left = stall_prob_left
        self.stall_prob_right = stall_prob_right

        self.pause = pause_prob
        self.stalled_death_prob = stalled_death_prob

        self.lef_positions = np.zeros((self.num_LEF, 2), dtype=int) - 1
        
        self.stalled = np.zeros((self.num_LEF, 2), dtype=int)
        self.occupied = np.zeros(self.num_site, dtype=int)
        
        self.occupied[0] = self.occupied[-1] = 1

        self.lef_birth()


    def lef_birth(self):
    
        for i in range(self.num_LEF):
            if np.all(self.lef_positions[i] == -1):
                while True:
                    pos = np.random.randint(1, self.num_site-1)
            
                    if self.occupied[pos] == 0:
                        if np.random.random() < self.birth_prob[pos]:
                            self.lef_positions[i] = pos
                            self.occupied[pos] = 1
                    
                            if (pos < (self.num_site - 2)) and (self.occupied[pos+1] == 0):
                                if np.random.random() > 0.5:
                                    self.lef_positions[i, 1] = pos + 1
                                    self.occupied[pos+1] = 1
                        
                        break


    def lef_death(self):
    
        for i in range(self.num_LEF):
            if np.all(self.lef_positions[i] >= 0):
                if self.stalled[i, 0] == 0:
                    death_prob1 = self.death_prob[self.lef_positions[i, 0]]
                else:
                    death_prob1 = self.stalled_death_prob[self.lef_positions[i, 0]]
                    
                if self.stalled[i, 1] == 0:
                    death_prob2 = self.death_prob[self.lef_positions[i, 1]]
                else:
                    death_prob2 = self.stalled_death_prob[self.lef_positions[i, 1]]
                
                death_prob = max(death_prob1, death_prob2)
                
                if np.random.random() < death_prob:
                    self.stalled[i] = 0
                    self.occupied[self.lef_positions[i]] = 0
                    
                    self.lef_positions[i] = -1
        

    def lef_step(self):
    
        for i in range(self.num_LEF):
            if np.all(self.lef_positions[i] >= 0):
                stall1 = self.stall_prob_left[self.lef_positions[i, 0]]
                stall2 = self.stall_prob_right[self.lef_positions[i, 1]]
                                        
                if np.random.random() < stall1:
                    self.stalled[i, 0] = 1
                if np.random.random() < stall2:
                    self.stalled[i, 1] = 1
                             
                cur1, cur2 = self.lef_positions[i]
                
                if self.stalled[i, 0] == 0:
                    if self.occupied[cur1-1] == 0:
                        pause1 = self.pause[cur1]
                        
                        if np.random.random() > pause1:
                            self.occupied[cur1 - 1] = 1
                            self.occupied[cur1] = 0
                            
                            self.lef_positions[i, 0] = cur1 - 1
                            
                if self.stalled[i, 1] == 0:
                    if self.occupied[cur2 + 1] == 0:
                        pause2 = self.pause[cur2]
                        
                        if np.random.random() > pause2:
                            self.occupied[cur2 + 1] = 1
                            self.occupied[cur2] = 0
                            
                            self.lef_positions[i, 1] = cur2 + 1
            
        
    def step(self):
    
        self.lef_death()
        self.lef_birth()
        
        self.lef_step()
        
    
    def steps(self, N):
    
        for _ in range(N):
            self.step()
