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

        self.sites = np.arange(self.num_site, dtype=int)

        # LEF state equals 0 if LEF is unbound, 1 if bound
        self.lef_states = np.zeros(self.num_LEF, dtype=int)
        self.lef_positions = np.zeros((self.num_LEF, 2), dtype=int) - 1
        
        self.occupied = np.zeros(self.num_site, dtype=bool)
        self.stalled = np.zeros((self.num_LEF, 2), dtype=bool)

        self.occupied[0] = self.occupied[-1] = True
        

    def lef_birth(self, state_id=0):
    
        free_sites = self.sites[~self.occupied]
        binding_sites = np.random.choice(free_sites, size=self.num_LEF, replace=False)

        rng = np.random.random(self.num_LEF) < self.birth_prob[binding_sites]
        ids = np.flatnonzero(rng * (self.lef_states == state_id))
                
        if len(ids) > 0:
            self.occupied[binding_sites[ids]] = True
            self.lef_positions[ids] = binding_sites[ids, None]
        
            rng_stagger = (np.random.random(len(ids)) < 0.5) * ~self.occupied[binding_sites[ids]+1]

            self.lef_positions[ids, 1] = np.where(rng_stagger,
                                                  self.lef_positions[ids, 1] + 1,
                                                  self.lef_positions[ids, 1])
                                                  
            self.occupied[binding_sites[ids]+1] = np.where(rng_stagger,
                                                           True,
                                                           self.occupied[binding_sites[ids]+1])
                                                           
        return ids
                                                                                
        
    def lef_death(self, state_id=1):
    
        death_prob = np.where(self.stalled,
                              self.stalled_death_prob[self.lef_positions],
                              self.death_prob[self.lef_positions])
                              
        death_prob = np.max(death_prob, axis=1)
        
        rng = np.random.random(self.num_LEF) < death_prob
        ids = np.flatnonzero(rng * (self.lef_states == state_id))
        
        self.stalled[ids] = False
        self.occupied[self.lef_positions[ids]] = False
        
        self.lef_positions[ids] = -1
        
        return ids
        

    def update_LEF_states(self):
    
        ids_death = self.lef_death()
        ids_birth = self.lef_birth()

        self.lef_states[ids_death] = 0
        self.lef_states[ids_birth] = 1
        
        
    def lef_step(self, state_id=1):
    
        for i in range(self.num_LEF):
            if self.lef_states[i] == state_id:
                stall1 = self.stall_prob_left[self.lef_positions[i, 0]]
                stall2 = self.stall_prob_right[self.lef_positions[i, 1]]
                                        
                if np.random.random() < stall1:
                    self.stalled[i, 0] = True
                if np.random.random() < stall2:
                    self.stalled[i, 1] = True
                             
                cur1, cur2 = self.lef_positions[i]
                
                if not self.stalled[i, 0]:
                    if not self.occupied[cur1-1]:
                        pause1 = self.pause[cur1]
                        
                        if np.random.random() > pause1:
                            self.occupied[cur1 - 1] = True
                            self.occupied[cur1] = False
                            
                            self.lef_positions[i, 0] = cur1 - 1
                            
                if not self.stalled[i, 1]:
                    if not self.occupied[cur2 + 1]:
                        pause2 = self.pause[cur2]
                        
                        if np.random.random() > pause2:
                            self.occupied[cur2 + 1] = True
                            self.occupied[cur2] = False
                            
                            self.lef_positions[i, 1] = cur2 + 1


    def step(self):
    
        self.update_LEF_states()
        self.lef_step()
        
    
    def steps(self, N):
    
        for _ in range(N):
            self.step()
