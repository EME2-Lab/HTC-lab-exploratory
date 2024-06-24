import numpy as np
from scipy.optimize import fsolve
import math
from feedstock import Feedstock, FeedstockManager, elementary_feedstocks

def HTC_model():
    '''
    exe: x
    dmdm: x
    mddmd: x 
    Parameters
    ----------
    fig_name : str
        name of figure. It is the name of the png od pfd file to be saved
        
    '''
    
# Helper Functions 
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
    ''' 
    total_mass = feedstock.total_weight()
    percent_water = feedstock.water_added / total_mass
    percent_feedstock = feedstock.quantity / total_mass
    
    # 
    C = 4.184e-3
    
    # Assuming ambient temperature, 20°C
    water_heat = feedstock.water_added * C * (reaction_temp - 20) * percent_water
    feedstock_heat = feedstock.quantity * feedstock.hhv * percent_feedstock
    
    ramping_heat = water_heat + feedstock_heat 
    
    return ramping_heat
    
def get_ramping_time(ramping_heat: float, heating_rate: float) -> float: 
    '''
    Returns the time needed for heating in hours. 
    
    Parameters
    ramping_heat : float
        Ramping heat in megajoules (MJ)
    reaction_temp: float 
        Rate at which heat is supplied to reactor in Watts (W). 
    ''' 
    return ( ramping_heat * 3.6 ) / heating_rate

def get_electricity(feedstock: Feedstock) -> float: 
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
    rho = feedstock.density 
    mu = 0.001002
    
    R_e = N * D**2 * (rho / mu) 
    N_p = 94.043 * R_e ** -0.599

    electricity_mixing = N_p * rho * N**3 * D**5
    return electricity_mixing
    
# print(get_T_o_solution(220.0))
# print(get_heat_flux(220.0))
# print(get_reaction_heat(220.0, 1))

