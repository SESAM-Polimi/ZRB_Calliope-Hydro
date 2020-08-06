# ZRB_Calliope-Hydro
Repository of the Calliope Hydro Model of the Zambesi River Basin

## How to run
In order to run the model, run Calliope_Hydro.py 

## Overview
The model hosted in this repository consists in an integrated coupling between the energy modelling framework Calliope (For further details about Calliope, see: https://github.com/calliope-project), specifically modelled to descrcibe multiple cascade water reservoirs hydro systems, including the national loads of the modelled countries and relative other power generation technologies, and a hydrologic simulation model of the water surface evaporation and dependence of the hydro-power production from the storage level of the dams.

<img src="https://github.com/SESAM-Polimi/ZRB_Calliope-Hydro/blob/master/Multiple%20Cascade%20Water%20Reservoirs.png" width="600">

The two models are combined by an iterative process: 
- the dispatch strategy of the energy system is optimised based on a LP formulation with Dams operating with fixed timeseries of Hydraulic Head, dependent on the Storage Levels; 
- the timeseries of Storage Levels are, in turns, updated as a result of the evaporation losses from the surfaces of the basins, dependent on the surface area and hence, the Storage Level, and the optimal power dispatch of Dams operation, in response to available power, function of the Hydraulic Head and hence, the Storage Level;
- the iteration continues until reaching a Storage Level trend that is not significantly different from that calculated on the previous iteration.

<img src="https://github.com/SESAM-Polimi/ZRB_Calliope-Hydro/blob/master/Calliope%20Hydro%20Loop.png" width="600">

Further details about the methodology are reported in the related publication.

## Calliope version
To run the Calliope model in this repository without conflicts, please use the Calliope 0.6.5 version available here: https://www.callio.pe/news/2020/01/release-v0.6.5/

## License
[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-sa/4.0/)

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).
