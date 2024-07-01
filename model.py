import numpy as np
from scipy.optimize import fsolve
import math
import pandas as pd
from feedstock import Feedstock, FeedstockManager, create_elementary_feedstocks

# Feedstock Quantity 
def get_feedstock_quantity(yield_HC: float, feedstock: Feedstock):
    feedstock_quantity =  1 / (yield_HC * (1 - feedstock.moisture)) 
    feedstock.quantity = feedstock_quantity
    return feedstock_quantity


# Water Quantity 
def get_water_quantity(yield_HC: float, feedstock: Feedstock): 
    feedstock_quantity =  1 / (yield_HC * (1 - feedstock.moisture)) 
    feedstock.quantity = feedstock_quantity
    
    ideal_mc = feedstock.moisture_content_target
    if ideal_mc > feedstock.moisture:
        water_needed =  (feedstock.quantity * (1 - ideal_mc)) / (1 - feedstock.moisture)
        feedstock.water_added = water_needed
        # feedstock.water_added = water_needed
        feedstock.moisture = ideal_mc
        return water_needed
    else: 
        # Returns default value of 0
        return feedstock.water_added
        # raise ValueError(
        #     f"Feedstock with name '{feedstock.name}' has an ideal_mc of {feedstock.moisture_content_target} 
        #         but a moisture of {feedstock.moisture}"
        # )
    
    # water_quantity = feedstock.compute_water_added()
    # return water_quantity


# Heat Needed 
def get_T_o_solution(reaction_temp: float) -> float :
    '''
    Returns To in Kelvin (K) based on eqn (6) in this paper: 
        https://pubs.rsc.org/en/content/articlelanding/2012/ee/c2ee22180b#cit31.
    See ChatGPT prompt for reference: 
        https://chatgpt.com/share/a6681217-0c12-45c9-99a5-5869e7da6a56
    
    Parameters: 
    reaction_temp: float 
        Reaction temperature in °C
        
    Other Variables & Constants: 
    Assuming a Parr 4523 reactor: https://www.parrinst.com/products/stirred-reactors/series-4520-1-2l-bench-top-reactors/specifications/
    r_s: float 
        Non-insulated tank radius in meters (m)
    r_o: float 
        Outer tank radius in meters (m)
    r_i: float  
        Inner tank radius in meters (m)
    k_1: float 
        Thermal conductivity of insulation in Watts per meter per Kelvin (W⋅m-1⋅K-1)
    k_s: float 
        Thermal conductivity of steel in Watts per meter per Kelvin (W⋅m-1⋅K-1)
    h: float 
        Convention coefficient, assumed to equal 20 W per meter squared per Kelvin (W⋅m-2⋅K-1)
    epsilon: float 
        Emissivity of insulation (unitless)
    sigma: float 
        Stefan-Boltzmann constant in Watts per meter squared per Kelvin to the fourth (W⋅m-2⋅K-4)
    T_A: float 
        ambient temperature or room temperature in Kelvin (K)
    '''
    r_s = 5.08e-2
    r_o = 7.62e-2 
    r_i = 4.76e-2
    k_1 = 0.058 
    k_s = 16.25
    
    # Define constants
    C = 1 / (r_i * (np.log(r_o / r_s) / k_1) * (np.log(r_s / r_i) / k_s))
       
    h = 20  
    epsilon = 0.050
    sigma = 5.67e-8 
    T_R = reaction_temp + 273.15
    T_A = 20 + 273.15 

    # Initial guess for T_O
    T_O_initial_guess = (T_R + T_A) / 2
    
    # Define the function to solve
    def equation(T_O):
        return C * T_R - T_O * (C + h) + h * T_A + epsilon * sigma * (T_O**4 - T_A**4)

    # Solve for T_O
    get_T_o_solution = fsolve(equation, T_O_initial_guess)
    return get_T_o_solution[0]

def get_heat_flux(reaction_temp: float) -> float:
    ''''
    Returns the heat flux in W per meters squared (W⋅m-2) based on eqn (5) in this paper: 
        https://pubs.rsc.org/en/content/articlelanding/2012/ee/c2ee22180b#cit31
    
    Parameters: 
    reaction_temp: float 
        Reaction temperature in °C
        
    Other Variables & Constants: 
    h: float 
        Convention coefficient, assumed to equal 20 W per meter squared per Kelvin (W⋅m-2⋅K-1)
    T_O: float 
        Outside temperature of tank in Kelvin (K)
    T_A: float 
        ambient temperature or room temperature in Kelvin (K)
    epsilon: float 
        Emissivity of insulation (unitless)
    sigma: float 
        Stefan-Boltzmann constant in Watts per meter squared per Kelvin to the fourth (W⋅m-2⋅K-4)
    '''
    
    h = 20  
    T_O = get_T_o_solution(reaction_temp)
    epsilon = 0.050
    sigma = 5.67e-8 
    T_A = 20 + 273.15 
    
    return h * (T_O - T_A) + epsilon*sigma *(T_O**4 - T_A**4) 

def get_reaction_heat(reaction_temp: float, residence_time: float) -> float: 
    '''
    Returns the heat needed to maintain reaction temperature, based on heat losses in megajoules (MJ). 

    Parameters: 
    reaction_temp: float 
        Reaction temperature in °C
    residence_time: float 
        Time for reaction in hours
        
    Other Variables & Constants: 
    r_o: float 
        Outer tank radius in meters (m)
    pi: float 
        Constant; imported from math 
    h: float 
        Height of tank in meters (m)
    '''
    r_o = 7.62e-2 
    h = 0.6096 
    
    # Surface Area of Cylinder 
    SA = 2*math.pi*r_o*h + 2*math.pi*r_o**2
    # SA * heat flux *residencce time = Watt hours
    # Multiplying by 0.001 for kWh; multiplying by 3.6 for MJ
    reaction_heat = SA * get_heat_flux(reaction_temp) * residence_time * 0.001 * 3.6
    return reaction_heat

def ramping_heat(feedstock: Feedstock, reaction_temp: float) -> float:
    '''
    Returns the heat needed to reach the reaction temperature in megejoules (MJ). 
    
    Parameters
    feedstock: Feedstock 
        Feedstock object. See feedstock.py for additional information. 
    reaction_temp: float 
        Reaction temperature in °C
    C: float
        Specific Heat Capacity of Water in MJ / kg °C
    C_biomass: float
        Specific Heat Capacity of Biomass in MJ / kg° C
        Follows eqn (3) from this paper: https://www.sciencedirect.com/science/article/pii/S0016236113006856
    ''' 
    total_mass = feedstock.total_weight()
    percent_water = feedstock.water_added / total_mass
    percent_feedstock = feedstock.quantity / total_mass
    
    C_water = 4.184e-3
    C_biomass = (
        1e-6 * (5.340 * (reaction_temp + 273.15) - 299) * (1 - feedstock.moisture_content_target) + 
        C_water * feedstock.moisture_content_target
    )
        
    # Assuming ambient temperature, 20°C
    water_heat = feedstock.water_added * C_water * (reaction_temp - 20) * percent_water
    feedstock_heat = feedstock.quantity * C_biomass * (reaction_temp - 20) * percent_feedstock
    
    ramping_heat = water_heat + feedstock_heat 
    
    return ramping_heat

def get_heat_needed(feedstock: Feedstock, reaction_temp: float, residence_time: float) -> float:
    '''Returns total heat needed in kWh'''
    return (get_reaction_heat(reaction_temp, residence_time) + ramping_heat(feedstock, reaction_temp))/3.6    


# Electricity Needed  
def get_electricity_rate(feedstock: Feedstock) -> float: 
    '''
    Returns the electricity from mixing in kW based on eqn (7) in this paper & supplementary information in this paper: 
        https://pubs.rsc.org/en/content/articlelanding/2012/ee/c2ee22180b#cit31
    Also utilizes appendix data in this paper to compute Np: 
        https://www.mdpi.com/1996-1073/10/2/211#app1-energies-10-00211
    Parameters based on Parr reactor and conditions stated in this paper: 
        https://www.sciencedirect.com/science/article/pii/S0960852422001286?via%3Dihub
        https://www.parrinst.com/products/stirred-reactors/series-4520-1-2l-bench-top-reactors/specifications/
    
    Parameters: 
    feedstock: Feedstock 
        Feedstock object. See feedstock.py for additional information. 
        
    Other Variables & Constants: 
    N: float 
        Impeller speed in revolutions per second (rps)
    D: float 
        Impeller diameter in meters (m)
    rho: float 
        Mixture density in kilograms per cubic meters (kg⋅m-3)
    mu: float 
        Mixture viscosity in kilograms per meter per second (kg⋅m-1⋅s-1); assumed to be equivalent to water 
    sigma: float 
        Stefan-Boltzmann constant in Watts per meter squared per Kelvin to the fourth (W⋅m-2⋅K-4)
    '''

    N = 6.67
    D = 0.057912 
    total_mass = feedstock.total_weight()
    percent_water = feedstock.water_added / total_mass
    percent_feedstock = feedstock.quantity / total_mass
    feedstock.density = percent_feedstock * feedstock.density + percent_water * 1000
    rho = feedstock.density 
    mu = 1.002e-3
    
    R_e = N * D**2 * (rho / mu) 
    N_p = 94.043 * R_e ** -0.599

    electricity_mixing = N_p * rho * N**3 * D**5
    return electricity_mixing
    
def get_ramping_time(ramping_heat: float, heating_rate: float) -> float: 
    '''
    Returns the time needed for heating in hours. 
    
    Parameters
    ramping_heat : float
        Ramping heat in megajoules (MJ)
    reaction_temp: float 
        Rate at which heat is supplied to reactor in Watts (W). 
    ''' 
    return ( ramping_heat / 3.6 ) / (heating_rate * 1e-3)

def get_electricity_needed(feedstock: Feedstock, residence_time: float, reaction_temp: float, heating_rate = 1500) -> float:
    '''
    Returns total electricity needed in kWh
    '''
    electricity_rate = get_electricity_rate(feedstock)
    time = get_ramping_time(ramping_heat(feedstock, reaction_temp), heating_rate) + residence_time
    return electricity_rate * time


# CO2 Emissions 
def get_co2_emissions(yield_HC: float, gas_yield: float, feedstock: Feedstock): 
    if feedstock.moisture != feedstock.moisture_content_target: 
        get_feedstock_quantity(yield_HC, feedstock)
        get_water_quantity(feedstock)
    return feedstock.total_weight() * (1-feedstock.moisture) * gas_yield

# PW Generated 
def get_pw(yield_HC: float, gas_yield: float, feedstock: Feedstock, hc_placeholder: float): 
    return feedstock.total_weight() - (hc_placeholder + get_co2_emissions(yield_HC, gas_yield, feedstock))

# Post-Processing 
def get_post_processing(hc_placeholder: float):
    '''
    Returns electricity used for post-processing in kWh
    Utilizing this paper for reference: https://www.mdpi.com/1996-1944/16/20/6653
    '''
    # Unit: W⋅h
    vacuum_filtration = 60 * 0.25 
    drying = 1200 * 24 * hc_placeholder 
    
    return (vacuum_filtration + drying) / 1000
    
    
    

# Converting Name into relevant parameters
def get_parameter(reaction_conditions: str, parameter: str) -> float: 
    '''
    Returns a value for a parameter of interest based on the reaction conditions. 
    
    Parameters: 
    reaction_conditions: str 
        Conditions for a reaction (feedstock, temp, time)
    parameter: str
        Parameter of interest (gas yield, HC yield, HHV_HC)

    '''
    reaction_conditions = reaction_conditions.split('hydrochar production, ')[1]
    feedstock, temp, time = reaction_conditions.split('_')
    temp = int(temp.split('C')[0])
    time = int(time.split('hr')[0])
    
    if parameter == 'gas_yield': 
        df = pd.read_excel('experimental-data/HTC_yield_HHV.xlsx',sheet_name='Yield_Gas', engine='openpyxl')
    elif parameter == 'HC_yield': 
        df = pd.read_excel('experimental-data/HTC_yield_HHV.xlsx',sheet_name='Yield_HC', engine='openpyxl')
    elif parameter == 'HHV_HC': 
        df = pd.read_excel('experimental-data/HTC_yield_HHV.xlsx',sheet_name='HHV_HC', engine='openpyxl')
    else: 
        raise ValueError(f"Parameter '{parameter}' is not valid.")
                
    filtered_df = df[df.iloc[:, 0] == str(feedstock) ]
    return filtered_df[filtered_df['hours'] == int(time)][int(temp)].iloc[0]

feedstock_condition = 'hydrochar production, stdSRU_220C_1hr'
print(get_parameter(feedstock_condition, 'HHV_HC'))  

# print(get_T_o_solution(220.0))
# print(get_heat_flux(220.0))
# print(get_reaction_heat(220.0, 1))

# elementary_feedstocks = create_elementary_feedstocks()
# excluded_feedstocks = {"rawSRU", "rawBSG"}
# for attr, feedstocks in elementary_feedstocks.__dict__.items():
#     for feedstock in feedstocks:
#         if feedstock.name not in excluded_feedstocks:
#             yield_HC = get_parameter(f"hydrochar production, {feedstock.name}_{feedstock.temp}C_{feedstock.time}hr", 'HC_yield')
#             get_feedstock_quantity(yield_HC, feedstock)
#             get_water_quantity(yield_HC, feedstock)
            
#             print(f"{feedstock.name} has a quantity of {feedstock.quantity}")
#             print(f"{feedstock.name}_{feedstock.temp}C_{feedstock.time}hr ramp heat:", ramping_heat(feedstock, feedstock.temp))
#             print()
