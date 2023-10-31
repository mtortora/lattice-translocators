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
        
        super().__init__(num_LEF,
                         birth_prob,
                         death_prob,
                         stalled_death_prob,
                         pause_prob,
                         stall_prob_left,
                         stall_prob_right)
                         
        self.ctcf_birth_prob = ctcf_birth_prob
        self.ctcf_death_prob = ctcf_death_prob
            
        occupancy = ctcf_birth_prob / (ctcf_birth_prob + ctcf_death_prob)

        # CTCF state equals -1 if site is non-CTCF, 0 if CTCF unbound, 1 if bound
        self.ctcf_states_left = stall_prob_left > 0
        self.ctcf_states_right = stall_prob_right > 0
        
        self.num_CTCF = self.ctcf_states_left.sum() + self.ctcf_states_right.sum()
        
        rng_left = np.random.random(self.num_site) < occupancy
        rng_right = np.random.random(self.num_site) < occupancy
        
        self.ctcf_states_left = np.where(self.ctcf_states_left,
                                         self.ctcf_states_left*rng_left,
                                         -1)
        self.ctcf_states_right = np.where(self.ctcf_states_right,
                                          self.ctcf_states_right*rng_right,
                                          -1)

        self.stall_prob_left = (self.ctcf_states_left == 1)
        self.stall_prob_right = (self.ctcf_states_right == 1)
                         

    def ctcf_birth(self):
    
        rng_left = np.random.random(self.num_site) < self.ctcf_birth_prob
        rng_right = np.random.random(self.num_site) < self.ctcf_birth_prob

        ids_left = np.flatnonzero(rng_left * (self.ctcf_states_left == 0))
        ids_right = np.flatnonzero(rng_right * (self.ctcf_states_right == 0))
        
        self.stall_prob_left[ids_left] = 1
        self.stall_prob_right[ids_right] = 1
        
        return ids_left, ids_right
                
        
    def ctcf_death(self):

        rng_left = np.random.random(self.num_site) < self.ctcf_death_prob
        rng_right = np.random.random(self.num_site) < self.ctcf_death_prob

        ids_left = np.flatnonzero(rng_left * (self.ctcf_states_left == 1))
        ids_right = np.flatnonzero(rng_right * (self.ctcf_states_right == 1))
        
        lef_ids_left = np.flatnonzero(np.in1d(self.lef_positions[:, 0], ids_left))
        lef_ids_right = np.flatnonzero(np.in1d(self.lef_positions[:, 1], ids_right))

        self.stalled[lef_ids_left, 0] = 0
        self.stalled[lef_ids_right, 1] = 0
        
        self.stall_prob_left[ids_left] = 0
        self.stall_prob_right[ids_right] = 0
        
        return ids_left, ids_right

    
    def update_CTCF_states(self):
    
        ids_death = self.ctcf_death()
        ids_birth = self.ctcf_birth()

        self.ctcf_states_left[ids_death[0]] = 0
        self.ctcf_states_left[ids_birth[0]] = 1

        self.ctcf_states_right[ids_death[1]] = 0
        self.ctcf_states_right[ids_birth[1]] = 1
                                
                                
    def step(self):
    
        self.update_CTCF_states()
        super().step()
