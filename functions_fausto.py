import datetime
import smtplib
import shutil


def compare_storage_of_two_calliope_models(calliope_model_1, calliope_model_2, path_model_1, path_model_2):

    '''
    # Esempio di utilizzo della funzione:
    import calliope
    from functions_fausto import compare_storage_of_two_calliope_models
    percorso_modello_1 = 'Results/results_20220428-165545_nospillage/results_1/model.nc'
    percorso_modello_2 = 'Results/results_20220502-130204/results_1/model.nc'

    model1 = calliope.read_netcdf(percorso_modello_1)
    model2 = calliope.read_netcdf(percorso_modello_2)


    compare_storage_of_two_calliope_models(model1, model2, percorso_modello_1, percorso_modello_2)
    '''

    locs_techs_ordered = ['Zambia::storageA', 'Zambia::storageB', 'Zambia::storageC', 'Moz-North-Center::storageD']
    bool_list = []
    mex = []
    for locstech in locs_techs_ordered:
        gino1 = calliope_model_1._model_data.data_vars['storage'].loc[locstech]
        gino2 = calliope_model_2._model_data.data_vars['storage'].loc[locstech]

        if gino1.equals(gino2):
            bool_list.append(True)
            coo = ''
        else:
            bool_list.append(False)
            coo = 'NOT'
        mex.append(f"`{gino1.coords['loc_techs_store'].values}` "
                   f"of model "
                   f"`{path_model_1}` "
                   f"is {coo} EQUAL to "
                   f"`{gino2.coords['loc_techs_store'].values}` "
                   f"of model "
                   f"`{path_model_2}`.")

    print(f'{"ALL EQUAL" if all(bool_list) else "NOT ALL EQUAL"}\n', *mex, sep='\n')


def create_right_files():

    for ii in ['CB', 'ITT', 'KA', 'KG']:
        with open(f"Timeseries_original_updated_with_positives/evapLoss_{ii}.txt", "r") as testo:

            linee = testo.readlines()

            blocca_alla_riga = 10e100  # 3

            numerii, timestamps = [], []
            for numero, gee in enumerate(linee):

                if numero == 0:
                    header = gee
                    continue  # salto le intestazioni

                # print(gee[20:])
                # numerii.append(float(gee[20:-2]))

                numerii.append(gee[20:-1])
                timestamps.append(gee[:20])

                if numero == blocca_alla_riga:
                    print(numerii, timestamps, type(numerii[1]))
                    break

        listone = list(map(float, numerii))
        listariella = list(map(lambda x: str(abs(x)*10e3), listone))
        # print(listone, type(listone[0]))

        with open(f"Timeseries_original_updated_with_positives/evapLoss_{ii}.txt", "w") as testo2:

            testo2.writelines(header)

            for gino in range(len(numerii)):

                testo2.writelines(timestamps[gino] + listariella[gino] + '\n')

    shutil.copytree("Timeseries/Initialize_Loop", "PROVADIR_2", dirs_exist_ok=True)


def writing_spillage_effs():
    with open("Timeseries/evapLoss_KA.txt", "r") as testo:

        linee = testo.readlines()

        blocca_alla_riga = 10e100  # 3  # to debug

        numerii, timestamps = [], []
        for numero, gee in enumerate(linee):

            if numero == 0:
                header = gee
                continue  # salvate le le intestazioni

            timestamps.append(gee[:20])

            if numero == blocca_alla_riga:
                print(numerii, timestamps, type(numerii[1]))
                break

    for ii in ['A', 'B', 'C', 'D']:  # ci sono 4 tecnologie di spillage (A, B, C, D) tra la Zambia e il Mozambico
        with open(f"Timeseries/spillage{ii}_eff.txt", "w") as testo2:

            if ii == 'D':
                testo2.writelines(header.replace('Zambia', 'Moz-North-Center'))
            else:
                testo2.writelines(header)

            for gino in range(len(timestamps)):
                testo2.writelines(timestamps[gino] + '0' + '\n')


def get_latest_file_or_folder_from_directory(directory: str, last=-1):
    '''
    Returns the "last"th-latest file/folder (modified/created) in a directory of folders (if last=-1 is the latest)
    '''
    import glob
    import os

    list_of_folders = glob.glob(directory.strip(r"\ /") + '/*')  # * means all, if needed a specific format then *.csv

    # list_of_folders.remove('Results\\results_debug')
    # latest_folder = max(list_of_folders, key=os.path.getctime)

    latest_folder = sorted(list_of_folders, key=os.path.getctime)[last]

    return latest_folder


def apply_plot_function_to_all_results(**kwargs):
    import calliope
    from plotting_fausto import plotting
    import glob

    all_results = []
    for folders in glob.glob('Results/*'):
        if folders != 'Results\\results_debug':  # excluding the results_debug folder
            for folder in glob.glob(f'{folders}/*'):
                (all_results.append(folder) if folder[-4:] != '.txt' else None)
    for result in all_results:
        model = calliope.read_netcdf(f'{result}\\model.nc')
        plots_folder = f'{result}\\plots\\'

        plotting.FaPlotting(model).plot_storage_and_carriers(path=plots_folder, frmt='png')
        # plotting.FaPlotting(model).plot_storage_and_carriers(kwargs, path=plots_folder,)
        # break


def apply_function_to_one_result(frmt):
    from plotting_fausto import plotting
    import calliope
    import glob
    import os

    for folders in glob.glob('Results\\results_20220517-231045\\*'):
        if os.path.isdir(folders):
            model = calliope.read_netcdf(folders + '\\model.nc')
            plots_folder = f'{folders}\\plots'
            plotting.FaPlotting(model).plot_storage_and_carriers(path=plots_folder, frmt=frmt)


def compare_multiple_calliope_models(*args):
    for model in args[1:]:
        if not model.equals(args[0]):
            print('The models analyzed are NOT ALL equal.')
            break
        else:
            print('ALL models are equal.')


def get_equal_calliope_models(directory):
    import calliope
    import os
    import glob

    flag_finish = True
    some_equal = False
    mdl = '\\model.nc'
    equal_models = []
    list_results = [f for f in glob.glob(directory.strip(r"\ /") + '/*') if f != 'Results\\results_debug']
    while flag_finish:
        results_left_to_b_compared = list(filter(lambda x: x not in equal_models, list_results))
        if len(results_left_to_b_compared) > 1:
            first_to_comp = results_left_to_b_compared[0]
            first_results = [os.path.join(first_to_comp, rslt) for rslt in os.listdir(first_to_comp) if os.path.isdir(os.path.join(first_to_comp, rslt))]
            first_num_results = len(first_results)

            temporarily_equals = [first_to_comp]
            for i in results_left_to_b_compared[1:]:
                i_results = [os.path.join(i, rslt) for rslt in os.listdir(i) if os.path.isdir(os.path.join(i, rslt))]
                i_num_results = len(i_results)
                if i_num_results != first_num_results:
                    continue  # if they don't even have the same number of results (results_1, results_2..) continue
                what_to_check = [(j + mdl, u + mdl) for u in i_results for j in first_results if u.endswith(j[-9:])]
                for en, wtc in enumerate(what_to_check):
                    model1 = calliope.read_netcdf(wtc[0])
                    model2 = calliope.read_netcdf(wtc[1])
                    if not model1._model_data.equals(model2._model_data):  # TODO: maybe just compare the storage...
                        break
                    if en == len(what_to_check):
                        equal_models.append(i)
                        temporarily_equals.append(i)
            if len(temporarily_equals) > 1:
                some_equal = True
                print(f'{*temporarily_equals,} models are equal.')
            list_results.remove(first_to_comp)
        else:
            flag_finish = False

    if not some_equal:
        print(f'Results where ALL different!')


def get_equal_storage_in_results(directory):
    import calliope
    import os
    import glob

    flag_finish = True
    some_equal = False
    mdl = '\\model.nc'
    equal_models = []
    list_results = [f for f in glob.glob(directory.strip(r"\ /") + '/*') if f != 'Results\\results_debug']
    while flag_finish:
        results_left_to_b_compared = list(filter(lambda x: x not in equal_models, list_results))
        if len(results_left_to_b_compared) > 1:
            first_to_comp = results_left_to_b_compared[0]
            first_results = [os.path.join(first_to_comp, rslt) for rslt in os.listdir(first_to_comp) if
                             os.path.isdir(os.path.join(first_to_comp, rslt))]
            first_num_results = len(first_results)

            temporarily_equals = [first_to_comp]
            for i in results_left_to_b_compared[1:]:
                i_results = [os.path.join(i, rslt) for rslt in os.listdir(i) if os.path.isdir(os.path.join(i, rslt))]
                i_num_results = len(i_results)
                if i_num_results != first_num_results:
                    continue  # if they don't even have the same number of results (results_1, results_2..) continue
                what_to_check = [(j + mdl, u + mdl) for u in i_results for j in first_results if u.endswith(j[-1])]
                for en, wtc in enumerate(what_to_check):
                    model1 = calliope.read_netcdf(wtc[0])
                    model2 = calliope.read_netcdf(wtc[1])
                    if not model1._model_data['storage'].loc['Zambia::storageA'].equals(model2._model_data['storage'].loc['Zambia::storageA']):  # FIXME: comparison of the whole storage is needed
                        break
                    if en == len(what_to_check) - 1:
                        equal_models.append(i)
                        temporarily_equals.append(i)
                        some_equal = True
            if len(temporarily_equals) > 1:
                print(f'{*temporarily_equals,} models are equal.')
            list_results.remove(first_to_comp)
        else:
            flag_finish = False

    if not some_equal:
        print(f'Results where ALL different!')
