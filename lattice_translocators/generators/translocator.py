from . import arrays


def make_translocator(extrusion_engine,
                      type_list,
                      site_types,
                      CTCF_left_positions,
                      CTCF_right_positions,
                      **kwargs):

    sites_per_replica = kwargs['monomers_per_replica'] * kwargs['sites_per_monomer']
    number_of_LEFs = (kwargs['number_of_replica'] * kwargs['monomers_per_replica']) // kwargs['LEF_separation']
    
    assert len(site_types) == sites_per_replica, ("Site type array (%d) doesn't match replica lattice size (%d)"
                                                  % (len(site_types), sites_per_replica))

    # Create arrays
    LEF_arrays = arrays.make_LEF_arrays(type_list, site_types, **kwargs)
    CTCF_arrays = arrays.make_CTCF_arrays(type_list, site_types, CTCF_left_positions, CTCF_right_positions, **kwargs)
    
    if ('CTCF_offtime' in kwargs) & ('CTCF_lifetime' in kwargs):
        CTCF_dynamic_arrays = arrays.make_CTCF_dynamic_arrays(type_list, site_types, **kwargs)
        translocator = extrusion_engine(number_of_LEFs, *LEF_arrays, *CTCF_arrays, *CTCF_dynamic_arrays)
        
    else:
        translocator = extrusion_engine(number_of_LEFs, *LEF_arrays, *CTCF_arrays)

    if not hasattr(translocator, 'ctcfDeathProb'):
        translocator.stallProbLeft = 1 - (1-translocator.stallProbLeft) ** (1./kwargs['velocity_multiplier'])
        translocator.stallProbRight = 1 - (1-translocator.stallProbRight) ** (1./kwargs['velocity_multiplier'])

    return translocator
    
    
def run_translocator(translocator,
                     steps,
                     dummy_steps,
                     sites_per_monomer,
                     **kwargs):

    LEF_positions = []
    translocator.steps(dummy_steps*sites_per_monomer)
    
    for _ in range(steps):
        translocator.steps(sites_per_monomer)
        
        bound_LEF_positions = get_bound_LEFs(translocator)
        LEF_positions.append(bound_LEF_positions)
        
    return LEF_positions


def get_bound_LEFs(translocator):

    LEF_positions = translocator.LEFs
    
    bound_LEF_positions = LEF_positions[LEF_positions >= 0]
    bound_LEF_positions = bound_LEF_positions.reshape((-1, 2))
    
    return bound_LEF_positions.tolist()


def get_bound_CTCFs(translocator):

    CTCF_left_positions = translocator.stallProbLeft
    CTCF_right_positions = translocator.stallProbRight

    CTCF_left_positions = CTCF_left_positions.nonzero()[0]
    CTCF_right_positions = CTCF_right_positions.nonzero()[0]
    
    return CTCF_left_positions.tolist(), CTCF_right_positions.tolist()
