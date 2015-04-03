# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pandas as pd
import intervals
import yaml
import itertools

# <codecell>

c=yaml.load(open('VaccinationStrategies.yaml','rb'))

def iterconvert_dict(d, key_func=None, val_func=None):
    """ yields iterator over dict items where the key and value
    are optionally converted to a type by the functions or function
    objects passed as arguments
    """
    for k, v in d.items():
        yield (
            k if key_func is None else key_func(k),
            v if val_func is None else val_func(v))

def build_strategies(internal_coverage_map):
    ivl_list = []
    vacs_list = []
    for ivl, par in interval_coverage_map.items():
        available_vaccines = [v for v in par['proportions'].keys() \
                              if is_needle_sparing(v)] + ['BASE']
        ivl_list.append(ivl)
        vacs_list.append(available_vaccines)
    strategies = itertools.product(*vacs_list)
    for vaccine in strategies:
        yield {ivl: dict(choice=vac) \
               for ivl, vac in zip(ivl_list, vaccine)}
               
ns_relative = c['properties']['needle-sparing']['relative']

interval_coverage_map = c['coverage']

def is_needle_sparing(vac):
    for vaccine_dict in c['vaccines']:
        if vac == vaccine_dict['vaccine']:
            if 'properties' in vaccine_dict:
                return True
            else:
                return False
        elif vac == 'BASE':
            return False
    raise Exception('could not find vaccine %s' % vac['vaccine'])
    
def update_proportions(base_overall_coverage, overall_coverage,
                        base_proportions, choice_vaccine):
    proportions = {}
    for v in [i['vaccine'] for i in c['vaccines']]:
        proportions[v] = 0.00
    if choice_vaccine is 'BASE':
        proportions.update(base_proportions)
    else:
        assert(is_needle_sparing(choice_vaccine))
        coverage_increase = overall_coverage - base_coverage
        assert(coverage_increase > 0)
        new_non_nsp = 0.0
        for v, p in base_proportions.items():
            if not is_needle_sparing(v):
                new_p = (base_overall_coverage * p) / overall_coverage
                new_non_nsp += new_p
                proportions[v] = new_p
        proportions[choice_vaccine] = 1.0 - new_non_nsp
        
    return proportions

exp_list = []
exp_id = 0
for mult in c['properties']['needle-sparing']['multipliers']:
    for strategy in build_strategies(interval_coverage_map):
        exp_dicts = []
        for ivl, vac_dict in strategy.items():
            base_overall_coverage = interval_coverage_map[ivl]['overall']
            overall_coverage = base_overall_coverage
            if is_needle_sparing(vac_dict['choice']):
                overall_coverage += (mult * ns_relative[ivl])
                
            vac_dict.update(update_proportions(base_overall_coverage,
                                                overall_coverage,
                                                interval_coverage_map[ivl]['proportions'],
                                                vac_dict['choice']
                                                ))
            vac_dict['multiplier'] = mult
            vac_dict['age_group'] = ivl
            vac_dict['base_overall_coverage'] = base_overall_coverage
            vac_dict['overall_coverage'] = overall_coverage
            
            exp_dicts.append(vac_dict)
        for d in exp_dicts:
            d['exp_id'] = exp_id
        exp_id += 1
        exp_list.extend(exp_dicts)
        
exp_df= pd.DataFrame(exp_list)
exp_df.to_csv('dat/2005_2009_ver2_11_choice_experiment_table.csv')

