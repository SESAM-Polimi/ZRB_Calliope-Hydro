from plotting_fausto.functions import check_folder, check_if_model_calliope, to_excel, plot_storage, plot_storage_and_carriers_and_eff
from plotting_fausto import exceptions


class FaPlotting:
    def __init__(self, model):
        check_if_model_calliope(model)
        self.model = model
        self._model_data = model._model_data

    def write_excel(self, *args, **kwargs):
        to_excel(self._model_data, *args, **kwargs)

    def plot_in(self, path, excel_name='Results without timesteps.xlsx'):
        # check_folder(path)
        # save_excel(path, excel_name, self.variables_not_to_plot, self.model)
        # # savefig...path
        pass

    def info(self):
        pass  # dà info sulle coordinate e sulle variabili presenti nei risultati del modello di calliope

    def plot_storage_timeseries(self, *args, **kwargs):
        # write_excel()
        plot_storage(self._model_data, *args, **kwargs)

    def plot_storage_and_carriers(self, *args, **kwargs):
        plot_storage_and_carriers_and_eff(self._model_data, *args, **kwargs)
