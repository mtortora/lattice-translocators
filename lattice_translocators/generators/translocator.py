from . import arrays


def make_translocator(extrusion_engine,
                      site_types,
                      CTCF_left_positions,
                      CTCF_right_positions,
                      **kwargs):

    LEF_separation = kwargs['LEF_separation']
    velocity_multiplier = kwargs['velocity_multiplier']
        
    number_of_replica = kwargs['number_of_replica']
    monomers_per_replica = kwargs['monomers_per_replica']

    sites_per_monomer = kwargs['sites_per_monomer']
    sites_per_replica = monomers_per_replica*sites_per_monomer

    number_of_monomers = number_of_replica * monomers_per_replica
    number_of_LEFs = number_of_monomers // LEF_separation
    
    assert len(site_types) == sites_per_replica, ("Site type array (%d) doesn't match replica lattice size (%d)"
                                                  % (len(site_types), sites_per_replica))

    # Create arrays
    LEF_arrays = arrays.make_LEF_arrays(site_types, **kwargs)
    CTCF_arrays = arrays.make_CTCF_arrays(site_types, CTCF_left_positions, CTCF_right_positions, **kwargs)
    
    if ('CTCF_offtime' in kwargs) & ('CTCF_lifetime'  in kwargs):
        CTCF_dynamic_arrays = arrays.make_CTCF_dynamic_arrays(site_types, **kwargs)
        LEF_trans = extrusion_engine(number_of_LEFs, *LEF_arrays, *CTCF_arrays, *CTCF_dynamic_arrays)
        
    else:
        LEF_trans = extrusion_engine(number_of_LEFs, *LEF_arrays, *CTCF_arrays)

    if not hasattr(LEF_trans, 'ctcfDeathProb'):
        LEF_trans.stallProbLeft = 1 - (1 - LEF_trans.stallProbLeft) ** (1. / velocity_multiplier)
        LEF_trans.stallProbRight = 1 - (1 - LEF_trans.stallProbRight) ** (1. / velocity_multiplier)

    return LEF_trans


def get_bound_LEFs(translocator):

    LEF_positions = translocator.LEFs.copy()
    
    bound_LEF_positions = LEF_positions[LEF_positions >= 0]
    bound_LEF_positions = bound_LEF_positions.reshape((-1, 2))
    
    return bound_LEF_positions.tolist()
