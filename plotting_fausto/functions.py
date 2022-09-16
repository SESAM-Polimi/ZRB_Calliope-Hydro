import os
import calliope
import pandas as pd
import openpyxl
import xarray as xr
from plotting_fausto import exceptions
from plotting_fausto.hydro_specific_functions import arrange_techs_properly
import matplotlib.pyplot as plt


# Fa
def check_folder(path):
    if os.path.isdir(path):
        return
    elif not os.path.exists(path):
        os.makedirs(path)
        return
    elif os.path.isfile(path):
        raise ValueError(f'Path \'{path}\' points to a file. Please specify the path to a folder (either empy or not) '
                         f'in order to save the plots.')
    else:
        raise ValueError(f'The path \'{path}\' does not point to a folder (already existing or not) or a file. '
                         f'Please specify the path to a folder (already existing or not)'
                         f' in which the plots are going to be saved.')


# Fa
def check_if_model_calliope(model):
    if isinstance(model, calliope.core.model.Model):
        return
    else:
        raise TypeError(f'Specified model \'{model}\' is not a Calliope model type (it is a \'{type(model)}\').')


# Fa
def to_excel(model_data, path='Results', excel_name='Results(non time-varying).xlsx', exist_ok=True):

    # a MILP model which optimises to within the MIP gap, but does not fully
    # converge on the LP relaxation, may return as 'feasible', not 'optimal'
    if "termination_condition" not in model_data.attrs or model_data.attrs[
       "termination_condition"] in ["optimal", "feasible"]:
        data_vars = model_data.filter_by_attrs(is_result=1).data_vars  # plotto solo i risultati, ometto gli inputs
    else:
        # data_vars = model_data.filter_by_attrs(is_result=0).data_vars
        raise ValueError("Model termination condition was not optimal, only inputs would be safe to save but"
                         "I decided not to save them anyway.")

    os.makedirs(path, exist_ok=exist_ok)

    writer = pd.ExcelWriter(os.path.join(path, excel_name), engine='openpyxl')
    for var in data_vars:  # qui vanno tolte le variabili che non voglio mettere (quelle che non hanno timeseries)
        dims = data_vars[var].dims
        if any(x in dims for x in ['timesteps', 'datesteps']):
            continue
        series = split_loc_techs(model_data[var], return_as="Series").dropna()
        series.to_excel(writer, sheet_name=f'{var[:31]}', startrow=0, index=True, header=True)  # massimo 31 caratteri per lo sheet's name
    writer.save()


# Fa
def plot_storage(model_data, lslice=None, rslice=None, show_storage_cap_max=True, frmt='png', show=False, save=True,
                 path='Results', exist_ok=True, show_spillage_line=True, spillage_coeff=0.95, create_subplots=True,
                 show_subs=False):
    # TODO: check if 'storage' is present, otherwise don't even plot
    # TODO: # useful link for plot size etc:
    #  https://stackoverflow.com/questions/9651092/my-matplotlib-pyplot-legend-is-being-cut-off
    locs_techs = len(model_data.data_vars['storage'].coords['loc_techs_store'])
    for loc_tech in range(locs_techs):
        plt.figure()
        len_timesteps = len(model_data.data_vars['storage'].coords['timesteps'])
        if isinstance(lslice and rslice, int) and lslice != rslice:
            if lslice < 0 or lslice > len_timesteps or rslice < 0 or rslice > len_timesteps:
                raise ValueError(f'Idexes out of bounds: they go from 0 to {len_timesteps}')

            model_data.data_vars['storage'][loc_tech, lslice:rslice].plot(label='Storage')

        elif lslice is None and rslice is None:
            model_data.data_vars['storage'][loc_tech, :].plot(label='Storage')

        elif lslice is not None and rslice is not None and lslice == rslice:
            raise ValueError(f'Same indexes (lslice: \'{lslice}\', rslice: \'{rslice}\') to slice with,'
                             f' change one at least.')

        # elif isinstance(lslice and rslice, str):
        #     loc_tech_string = model_data.data_vars['storage'].coords['loc_techs_store'][loc_tech].values
        #     model_data.data_vars['storage'].iloc[loc_tech_string, lslice:rslice].plot(label='Storage')

        else:
            raise ValueError(f'Indexes used to slice the timeframe have both to be type "int" or both "None" for now, '
                             f'try with integers in the range of the timesteps (0 to {len_timesteps}) '
                             f'or leave these kwargs blank to have all the timesteps plotted.')

        if show_storage_cap_max:
            plt.axhline(y=model_data.data_vars['storage_cap_max'][loc_tech].values,
                        color='k', linestyle='-', label='Storage_cap_max')  # if 'inf' it doesn't show
            plt.axhline(y=model_data.data_vars['storage_cap'][loc_tech].values,
                        color='r', linestyle='-', label='Storage_cap')

        if show_spillage_line:
            plt.axhline(y=spillage_coeff * model_data.data_vars['storage_cap'][loc_tech].values,
                        color='magenta', linestyle='--', label='Spillage_threshold')

        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

        if save:
            os.makedirs(path, exist_ok=exist_ok)
            loc_tech_string = str(model_data.data_vars['storage'].coords['loc_techs_store'][loc_tech].values)
            plt.savefig(f'{path}/{loc_tech_string.replace(r"::", "_")}_storageplot.{frmt}', bbox_inches='tight',
                        format=f'{frmt}', dpi=300)
        if show:
            plt.tight_layout()
            plt.show()
        plt.close()

    if create_subplots:
        colors = ['orange', 'blue', 'cyan', 'green']
        # Get the right number of cols and rows in the subplot
        nrows = int(locs_techs ** 0.5)
        ncols = (nrows if nrows == locs_techs ** 0.5 else int(locs_techs / nrows) + 1)  # nrows*ncols >= locs_techs <-- minimum product greater than locs_techs
        fig2, axes = plt.subplots(nrows=nrows, ncols=ncols, constrained_layout=True)
        # fig2.set_size_inches(12, 14)
        locs_techs_new = arrange_techs_properly(model_data)  # FIXME: this function is very specific to the Calliope_Hydro project, delete it if wanting to generalize this code
        plot_index = 0
        for loc_tech in locs_techs_new:
            if isinstance(lslice and rslice, int) and lslice != rslice:
                model_data.data_vars['storage'][loc_tech, lslice:rslice].plot(color=colors[plot_index],
                                                                              ax=axes.flatten()[plot_index])
            elif lslice is None and rslice is None:
                model_data.data_vars['storage'][loc_tech, :].plot(color=colors[plot_index],
                                                                  ax=axes.flatten()[plot_index])
            axes.flatten()[plot_index].axhline(y=model_data.data_vars['storage_cap_max'][loc_tech].values,
                                             color='k', linestyle='-', label='Storage_cap_max')
            axes.flatten()[plot_index].axhline(y=model_data.data_vars['storage_cap'][loc_tech].values,
                                             color='r', linestyle='-', label='Storage_cap')
            axes.flatten()[plot_index].axhline(y=spillage_coeff * model_data.data_vars['storage_cap'][loc_tech].values,
                                             color='magenta', linestyle='--', label='Spillage_threshold')
            # titolo? axes.flatten()[loc_tech].set_title('titolo')
            # if loc_tech == locs_techs:
                # fig2.delaxes(axes[2, 1])  # FIXME: although it's looping on the real loc_tech present, plt.subplot creates also the other plots not needed (nrows*ncols - locs_techs)
            plot_index += 1

        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        fig2.set_size_inches(12, 9)
        # fig2.tight_layout(pad=0.01)
        # fig2.tight_layout()
        # plt.subplots_adjust(wspace=0.3, hspace=0.38)

        if save:
            plt.savefig(f'{path}/Summary_storageplot.{frmt}', format=f'{frmt}', dpi=300,)

        if show_subs:
            # plt.tight_layout()
            plt.show()
        plt.close()


# Fa
def plot_storage_and_carriers_and_eff(model_data, lslice=None, rslice=None, frmt='png', save=True, path='Results',
                                      exist_ok=True, spillage_coeff=0.95, show=False, sharexaxis=True):
    plt.rcParams['axes.grid'] = True
    plt.rc('grid', color='#686868', linestyle='--', linewidth=0.5)
    colors = ['orange', 'blue', 'cyan', 'green']
    colors_2 = ['#46FF28', '#000000']  # acid green, black
    eff_color = '#FF0000'  # red
    markersize_eff = 1

    nrows = 2
    ncols = 4
    fig2, axes = plt.subplots(nrows=nrows, ncols=ncols, constrained_layout=True, sharex=sharexaxis,)
    # fig2.set_size_inches(12, 14)
    locs_techs_new = arrange_techs_properly(model_data)
    plot_index = 0
    lines2d_1 = []
    for loc_tech in locs_techs_new:
        if isinstance(lslice and rslice, int) and lslice != rslice:
            lines2d_1.append(model_data.data_vars['storage'][loc_tech, lslice:rslice].rename('').plot(color=colors[plot_index],
                                                                                           ax=axes.flatten()[plot_index])[0])
        elif lslice is None and rslice is None:
            lines2d_1.append(model_data.data_vars['storage'][loc_tech, :].rename('').plot(color=colors[plot_index],
                                                                                          ax=axes.flatten()[plot_index])[0])
        lines2d_1.append(axes.flatten()[plot_index].axhline(y=model_data.data_vars['storage_cap_max'][loc_tech].values,
                                                            color='k', linestyle='-', label='Storage_cap_max'))
        lines2d_1.append(axes.flatten()[plot_index].axhline(y=model_data.data_vars['storage_cap'][loc_tech].values,
                                                            color='r', linestyle='-', label='Storage_cap'))
        lines2d_1.append(axes.flatten()[plot_index].axhline(y=spillage_coeff * model_data.data_vars['storage_cap'][loc_tech].values,
                                                            color='magenta', linestyle='--', label='Spillage_threshold'))
        new_title = axes.flatten()[plot_index].get_title().split(' = ')[1]
        axes.flatten()[plot_index].set_title(new_title)
        plot_index += 1

    carriers_indexes = [('Zambia::spillageA::waterB', 'Zambia::spillageA::waterA', 'Zambia::spillageA'),  # (carrier_prod, carrier_con, eff) coordinates
                        ('Zambia::spillageB::waterD', 'Zambia::spillageB::waterB', 'Zambia::spillageB'),
                        ('Zambia::spillageC::waterD', 'Zambia::spillageC::waterC', 'Zambia::spillageC'),
                        ('Moz-North-Center::spillageD::waterE', 'Moz-North-Center::spillageD::waterD', 'Moz-North-Center::spillageD')]

    lines2d_2 = []
    for indx in carriers_indexes:
        carrier_prod = model_data.carrier_prod.loc[indx[0]]
        carrier_con = model_data.carrier_con.loc[indx[1]]
        tech_eff = model_data.energy_eff.loc[indx[2]]

        lines2d_2.append(carrier_con.rename('').plot(color=colors_2[0], ax=axes.flatten()[plot_index], label='Carrier_con')[0])
        y_min_con, y_max_con = carrier_con.min().values, carrier_con.max().values

        lines2d_2.append(carrier_prod.rename('').plot(color=colors_2[1], ax=axes.flatten()[plot_index], label='Carrier_prod')[0])
        y_min_prod, y_max_prod = carrier_prod.min().values, carrier_prod.max().values

        if abs(max(y_max_con, y_max_prod)) != abs(min(y_min_con, y_min_prod)):
            rescaled_unitary_eff = (max(y_max_con, y_max_prod) + min(y_min_con, y_min_prod)) / 2
        else:
            rescaled_unitary_eff = min(y_min_con, y_min_prod) / 2
        tech_eff *= rescaled_unitary_eff
        lines2d_2.append(tech_eff.rename('').plot(color=eff_color, ax=axes.flatten()[plot_index], label='Eff_scaled',
                                                  markersize=markersize_eff, linestyle='', marker='*')[0])
        new_title = axes.flatten()[plot_index].get_title().split(' = ')[1]
        axes.flatten()[plot_index].set_title(new_title)
        plot_index += 1

    legend1 = plt.legend(lines2d_1[1:4], [l1.get_label() for l1 in lines2d_1[1:4]], bbox_to_anchor=(1.01, 2.1),
                         loc="upper left",)
    legend2 = plt.legend(lines2d_2[:3], [l2.get_label() for l2 in lines2d_2[:3]], bbox_to_anchor=(1.01, 0.97),
                         loc="upper left",)
    # plt.gca().add_artist(legend1)
    fig2.add_artist(legend1, legend2)

    # plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    # fig2.supylabel(None)
    # plt.subplots_adjust(hspace=.0)  # delete vertical space between plots
    fig2.set_size_inches(18, 11)

    if save:
        os.makedirs(path, exist_ok=exist_ok)
        plt.savefig(f'{path}/Summary_storage_carriers.{frmt}', format=f'{frmt}', dpi=300, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()


# Fa
def check_spillage():
    pass


# Calliope
def split_loc_techs(data_var, return_as="DataArray"):  # (model_data[var], return_as="Series") <-- model_data = model._model_data (c'è un for per questo c'è '[var]')
    """
    Get a DataArray with locations technologies, and possibly carriers
    split into separate coordinates.

    Parameters
    ----------
    data_var : xarray DataArray
        Variable from Calliope model_data, to split loc_techs dimension
    return_as : string
        'DataArray' to return xarray DataArray, 'MultiIndex DataArray' to return
        xarray DataArray with loc_techs as a MultiIndex,
        or 'Series' to return pandas Series with dimensions as a MultiIndex

    Returns
    -------
    updated_data_var : xarray DataArray of pandas Series
    """

    # Separately find the loc_techs(_carriers) dimension and all other dimensions
    loc_tech_dim = [i for i in data_var.dims if "loc_tech" in i]  # se loc_tech è presente come dimensione allora avrà sia una coordinata 'loc' che 'tech'
    if not loc_tech_dim:
        loc_tech_dim = [i for i in data_var.dims if "loc_carrier" in i]

    if not loc_tech_dim:  # se a questo punto è vuoto loc_tech_dim entra qui
        if return_as == "Series":
            return data_var.to_series()
        elif return_as in ["DataArray", "MultiIndex DataArray"]:
            return data_var
        else:
            raise ValueError(f"`return_as` must be `DataArray`, `Series`, or`MultiIndex DataArray`, "
                             f"but `{return_as}` given")

    elif len(loc_tech_dim) > 1:
        e = exceptions.ModelError
        raise e(f"Cannot split loc_techs or loc_tech_carriers dimension for DataArray {data_var.name}")

    loc_tech_dim = loc_tech_dim[0]  # prende l'unico valore
    # xr.Datarray -> pd.Series allows for string operations
    data_var_idx = data_var[loc_tech_dim].to_index()
    index_list = data_var_idx.str.split("::").tolist()

    # carrier_prod, carrier_con, and carrier_export will return an index_list
    # of size 3, all others will be an index list of size 2
    possible_names = ["loc", "tech", "carrier"]
    names = [i + "s" for i in possible_names if i in loc_tech_dim]

    data_var_midx = pd.MultiIndex.from_tuples(index_list, names=names)

    # Replace the Datarray loc_tech_dim with this new MultiIndex
    updated_data_var = data_var.copy()
    updated_data_var.coords[loc_tech_dim] = data_var_midx

    if return_as == "MultiIndex DataArray":
        return updated_data_var

    elif return_as == "Series":
        return reorganise_xarray_dimensions(updated_data_var.unstack()).to_series()

    elif return_as == "DataArray":
        return reorganise_xarray_dimensions(updated_data_var.unstack())

    else:
        raise ValueError(f"`return_as` must be `DataArray`, `Series`, or "
                         f"`MultiIndex DataArray`, but `{return_as}` given")


# Calliope
def reorganise_xarray_dimensions(data):
    """
    Reorganise Dataset or DataArray dimensions to be alphabetical *except*
    `timesteps`, which must always come last in any DataArray's dimensions
    """

    if not (isinstance(data, xr.Dataset) or isinstance(data, xr.DataArray)):
        raise TypeError("Must provide either xarray Dataset or DataArray to be reorganised")

    steps = [i for i in ["datesteps", "timesteps"] if i in data.dims]

    if isinstance(data, xr.Dataset):
        new_dims = (sorted(list(set(data.dims.keys()) - set(steps)))) + steps
    elif isinstance(data, xr.DataArray):
        new_dims = (sorted(list(set(data.dims) - set(steps)))) + steps

    updated_data = data.transpose(*new_dims).reindex({k: data[k] for k in new_dims})

    return updated_data
