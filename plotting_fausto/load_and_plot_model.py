import plotting
import calliope


# Load and existing model ('<name>.nc')
model = calliope.read_netcdf(
        'C:/Users/utente/Documents/CODICI di Fausto/z_ProveTesi/prova2/Config_prova_fausto/z_results/model_0.nc')

plotting.FaPlotting(model).write_excel()
plotting.FaPlotting(model).plot_storage_timeseries()  # dslice1=0, dslice2=120)
