import numpy as np

from . import SymmetricExtruder


class MultistateSymmetricExtruder(SymmetricExtruder.SymmetricExtruder):
    
    def __init__(self,
                 num_LEF,
                 birth_prob,
                 death_prob,
                 stalled_death_prob,
                 pause_prob,
                 stall_prob_left,
                 stall_prob_right,
                 transition_prob_list,
                 *args, **lef_transition_dict):
    
        super().__init__(num_LEF,
                         birth_prob,
                         death_prob,
                         stalled_death_prob,
                         pause_prob,
                         stall_prob_left,
                         stall_prob_right)
        
        self.state_dict = lef_transition_dict["LEF_states"]
        self.transition_dict = lef_transition_dict["LEF_transitions"]
        

    def lef_transitions(self, unbound_state_id):
        
        ids_list = []
        products_list = []
            
        for state_id in self.state_dict.values():
            state_list = []
            transition_list = []
            
            for ids, transition_prob in self.transition_dict.items():
                if state_id == int(ids[0]):
                    state_list.append(int(ids[1]))
                    transition_list.append(transition_prob[self.lef_positions].max(axis=1))
                    
            if state_id == max(self.state_dict.values()):
                death_prob = np.where(self.stalled,
                                      self.stalled_death_prob[self.lef_positions],
                                      self.death_prob[self.lef_positions])
                                      
                state_list.append(unbound_state_id)
                transition_list.append(death_prob.max(axis=1))

            rng = np.random.random(self.num_LEF)
            cumul_prob = np.cumsum(transition_list, axis=0)
            
            rng1 = (rng < cumul_prob[0])
            rng2 = ~rng1 * (rng < cumul_prob[-1])
            
            product_states = np.where(rng1, state_list[0], state_list[-1])
        
            ids = np.flatnonzero((rng1 + rng2) * (self.lef_states == state_id))
            products = product_states[ids]
            
            ids_list.append(ids)
            products_list.append(products)
            
        return ids_list, products_list
            
        
    def update_LEF_states(self, unbound_state_id, bound_state_id):
        
        ids_list, products_list = self.lef_transitions(unbound_state_id)
        ids_birth = self.lef_birth(unbound_state_id)
        
        self.lef_states[ids_birth] = bound_state_id
        
        for ids, products in zip(ids_list, products_list):
            self.lef_states[ids] = products
            
        ids_death = ids_list[-1][products_list[-1] == unbound_state_id]
        
        self.update_LEF_arrays(ids_death)


    def step(self):
    
        super().step(active_state_id=self.state_dict['RN'])
