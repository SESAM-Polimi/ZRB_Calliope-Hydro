

def arrange_techs_properly(model_data):
    locs_techs_ordered = ['Zambia::storageA', 'Zambia::storageB', 'Zambia::storageC', 'Moz-North-Center::storageD']
    coords_list = model_data.data_vars['storage'].coords['loc_techs_store'].values.tolist()
    locs_techs_indexes = [coords_list.index(x) for x in locs_techs_ordered]
    return locs_techs_indexes
