import numpy as np

from . import SymmetricExtruder

        
class SymmetricExtruderDynamicBoundary(SymmetricExtruder.SymmetricExtruder):
     
    def __init__(self,
                 num_LEF,
                 birth_prob,
                 death_prob,
                 stalled_death_prob,
                 pause_prob,
                 stall_prob_left,
                 stall_prob_right,
                 ctcf_birth_prob,
                 ctcf_death_prob,
                 *args):
        
        self.ctcf_birth_prob = ctcf_birth_prob
        self.ctcf_death_prob = ctcf_death_prob

        self.stall_prob_left_init = np.copy(stall_prob_left)
        self.stall_prob_right_init = np.copy(stall_prob_right)

        super().__init__(num_LEF,
                         birth_prob,
                         death_prob,
                         stalled_death_prob,
                         pause_prob,
                         stall_prob_left,
                         stall_prob_right)


    def ctcf_birth(self):
    
        for i in range(self.num_site):
            if self.stall_prob_left[i] != self.stall_prob_left_init[i]:
                if np.random.random() < self.ctcf_birth_prob[i]:
                    self.stall_prob_left[i] = self.stall_prob_left_init[i]
                    
            if self.stall_prob_right[i] != self.stall_prob_right_init[i]:
                if np.random.random() < self.ctcf_birth_prob[i]:
                    self.stall_prob_right[i] = self.stall_prob_right_init[i]
                    
                    
    def ctcf_death(self):
    
        for i in range(self.num_site):
            if self.stall_prob_left[i] != 0:
                if np.random.random() < self.ctcf_death_prob[i]:
                    self.stall_prob_left[i] = 0
                    
                    for j in range(self.num_LEF):
                        if i == self.lef_positions[j, 0]:
                            self.stalled[j, 0] = 0
                    
            if self.stall_prob_right[i] != 0:
                if np.random.random() < self.ctcf_death_prob[i]:
                    self.stall_prob_right[i] = 0
                    
                    for j in range(self.num_LEF):
                        if i == self.lef_positions[j, 1]:
                            self.stalled[j, 1] = 0
                        
                                
    def step(self):
    
        self.ctcf_death()
        self.ctcf_birth()
        
        super().step()
