import numpy as np


def make_site_array(type_list,
                    site_types,
                    value_dict,
                    at_ids=None,
                    number_of_replica=1,
                    **kwargs):
    
    assert len(type_list) == len(value_dict), ('Number of values (%d) incompatible with number of site types (%d)'
                                            % (len(value_dict), len(type_list)))
    
    prop_array = np.zeros(len(site_types), dtype=np.double)
    
    for i, name in enumerate(type_list):
        prop_array[site_types == i] = value_dict[name]
        
    if isinstance(at_ids, np.ndarray):
        mask = np.zeros(len(site_types), dtype=bool)
        mask[at_ids] = True
        
        prop_array[~mask] = 0
        
    return np.tile(prop_array, number_of_replica)


def make_CTCF_arrays(type_list,
                     site_types,
                     CTCF_left_positions,
                     CTCF_right_positions,
                     CTCF_facestall,
                     CTCF_backstall,
                     **kwargs):
    
    stall_left_array = make_site_array(type_list, site_types, CTCF_facestall, at_ids=CTCF_left_positions, **kwargs)
    stall_right_array = make_site_array(type_list, site_types, CTCF_facestall, at_ids=CTCF_right_positions, **kwargs)
    
    stall_left_array += make_site_array(type_list, site_types, CTCF_backstall, at_ids=CTCF_right_positions, **kwargs)
    stall_right_array += make_site_array(type_list, site_types, CTCF_backstall, at_idsids=CTCF_left_positions, **kwargs)
    
    return [stall_left_array, stall_right_array]


def make_CTCF_dynamic_arrays(type_list,
                             site_types,
                             CTCF_offtime,
                             CTCF_lifetime,
                             sites_per_monomer,
                             velocity_multiplier,
                             **kwargs):
    
    CTCF_offtime_array = make_site_array(type_list, site_types, CTCF_offtime, **kwargs)
    CTCF_lifetime_array = make_site_array(type_list, site_types, CTCF_lifetime, **kwargs)
    
    CTCF_birth_array = 1./ CTCF_offtime_array / (velocity_multiplier * sites_per_monomer)
    CTCF_death_array = 1./ CTCF_lifetime_array / (velocity_multiplier * sites_per_monomer)

    return [CTCF_birth_array, CTCF_death_array]
    

def make_LEF_arrays(type_list,
                    site_types,
                    LEF_offtime,
                    LEF_lifetime,
                    LEF_stalled_lifetime,
                    LEF_pause,
                    sites_per_monomer,
                    velocity_multiplier,
                    **kwargs):
    
    offtime_array = make_site_array(type_list, site_types, LEF_offtime, **kwargs)
    lifetime_array = make_site_array(type_list, site_types, LEF_lifetime, **kwargs)
    stalled_lifetime_array = make_site_array(type_list, site_types, LEF_stalled_lifetime, **kwargs)
    
    birth_array = 1./ offtime_array / (velocity_multiplier * sites_per_monomer)
    death_array = 1./ lifetime_array / (velocity_multiplier * sites_per_monomer)
    stalled_death_array = 1./ stalled_lifetime_array / (velocity_multiplier * sites_per_monomer)

    pause_array = make_site_array(type_list, site_types, LEF_pause, **kwargs)

    return [birth_array, death_array, stalled_death_array, pause_array]
