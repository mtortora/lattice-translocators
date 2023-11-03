from . import arrays


class Translocator():

    def __init__(self,
                 extrusion_engine,
                 type_list,
                 site_types,
                 ctcf_left_positions,
                 ctcf_right_positions,
                 **kwargs):

        sites_per_replica = kwargs['monomers_per_replica'] * kwargs['sites_per_monomer']
        number_of_LEFs = (kwargs['number_of_replica'] * kwargs['monomers_per_replica']) // kwargs['LEF_separation']
        
        assert len(site_types) == sites_per_replica, ("Site type array (%d) doesn't match replica lattice size (%d)"
                                                      % (len(site_types), sites_per_replica))

        lef_arrays = arrays.make_LEF_arrays(type_list, site_types, **kwargs)
        lef_transition_dict = arrays.make_LEF_transition_dict(type_list, site_types, **kwargs)

        ctcf_arrays = arrays.make_CTCF_arrays(type_list, site_types, ctcf_left_positions, ctcf_right_positions, **kwargs)
        ctcf_dynamic_arrays = arrays.make_CTCF_dynamic_arrays(type_list, site_types, **kwargs)
        
        engine = extrusion_engine(number_of_LEFs,
                                  *lef_arrays, *ctcf_arrays, *ctcf_dynamic_arrays,
                                  **lef_transition_dict)
        
        self.lef_trajectory = []
        self.ctcf_trajectory = []
        self.state_trajectory = []

        self.engine = engine
        self.params = kwargs
    
    
    def run(self, period=None):

        period = int(period) if period else self.params['sites_per_monomer']
        self.engine.steps(self.params['dummy_steps'] * period)
    
        for _ in range(self.params['steps']):
            self.engine.steps(period)
        
            bound_LEF_positions = self.get_bound_LEFs()
            bound_CTCF_positions = self.get_bound_CTCFs()
            
            self.lef_trajectory.append(bound_LEF_positions)
            self.ctcf_trajectory.append(bound_CTCF_positions)
            self.state_trajectory.append(self.engine.lef_states.copy())


    def get_bound_LEFs(self):

        lef_positions = self.engine.lef_positions
    
        bound_LEF_ids = (lef_positions >= 0).all(axis=1)
        bound_LEF_positions = lef_positions[bound_LEF_ids]
    
        return bound_LEF_positions.tolist()


    def get_bound_CTCFs(self):

        ctcf_left_positions = self.engine.stall_prob_left
        ctcf_right_positions = self.engine.stall_prob_right

        bound_left_positions, = ctcf_left_positions.nonzero()
        bound_right_positions, = ctcf_right_positions.nonzero()
    
        return bound_left_positions.tolist() + bound_right_positions.tolist()
