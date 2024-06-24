import re 
import os
import pandas as pd

class Feedstock:
    '''
    Creates a feedstock to be utilized by the hydrothermal carbonization model(s). 
    '''
    def __init__(self, name: str, hhv: float = 0.0, hhv_std: float = 0.0,
                 moisture: float = 0.0, moisture_std: float = 0.0, density: float = 0.0,
                time: int = 1, temp: int = 190):
        '''
        Initializes a feedstock with default values set to 0 unless otherwise specified. As all feedstocks are 
        either a standard misture or a combination of feedstocks, the naming conventions are as follows: 
        
        1) Raw mixtures are pre-defined as SRU, DCW, and BSG. These are indicated with a raw starting. (i.e. rawSRU)
        2) Standard mixtures are defined as raw mixtures with water to reach an 85% moisture content, incidated with a std starting. 
            a. For example, after adding water to SRU, the name will be stdSRU.
            b. As DCW is already above 85%, there will be no stdDCW. 
        3) All other mixtures are a combination of (1) & (2) with percentages after the name, separated by underscores. 
            a. For example, stdBSG50_rawSRU50 or rawBSG40_rawDCW30_rawSRU30. 
            b. For cleaner naming conventions, this analysis will not use decimals after the decimal point.  
            c. stdSRU_stdBSG_rawDCW is the combination of all three feedstocks.  
        4) To prevent the complexity of names, each feedstock has individual properties that differ based on reaction conditions. 
            
        Parameters:
        name (str): The name of the feedstock.
        hhv (float): The higher heating value (HHV) of the feedstock.
        hhv_std (float): The standard deviation of the HHV.
        moisture (float): The moisture content of the feedstock.
        moisture_std (float): The standard deviation of the moisture content.
        water_added (float): The amount of water added, in a mass measurement.
        density (float): The density of the feedstock mixture (without water) in kg/m^3.  
        quantity (float): The quantity of a feedstock or composite feedstock in a mixture. 
        temp (int): The temperature of the feedstock in an HTC reaction in °C 
        time (int): The residence time for the feedstock in an HTC reaction in hrs.
         
        '''
        self.name = name
        self.hhv = hhv
        self.hhv_std = hhv_std
        self.moisture = moisture
        self.moisture_std = moisture_std
        if self.moisture >= 0.85: 
            self.moisture_content_target = moisture 
        else: 
            self.moisture_content_target = 0.85 
        self.density = density
        self.water_added = 0.0
        self.quantity = 0.0
        self.temp = temp
        self.time = time
        
    def set_hhv(self, hhv: float, hhv_std: float):
        '''
        Setting HHV mean and std for a feedstock with known values. 
        '''
        self.hhv = hhv
        self.hhv_std = hhv_std

    def set_moisture(self, moisture: float, mc_std: float):
        '''
        Setting moisture content mean and std for a feedstock with known values. 
        '''
        self.moisture = moisture
        self.moisture_std = mc_std
        
    def compute_hhv(self, feedstock_manager: object):
        '''Calculate and set the higher heating value (HHV) for a composite feedstock.'''
        composite_hhv = 0.0
        composite_hhv_std = 0.0
        feedstocks = re.findall(r'([A-Za-z]+)(\d+)', self.name)

        for feedstock_name, percent_str in feedstocks:
            percent = float(percent_str) / 100
            feedstock = feedstock_manager.get_feedstock(feedstock_name)
            composite_hhv += feedstock.hhv * percent
            composite_hhv_std += (feedstock.hhv_std * percent) ** 2

        self.hhv = composite_hhv
        self.hhv_std = composite_hhv_std ** 0.5

    def compute_density(self, feedstock_manager: object):
        '''Calculate and set the density for a composite feedstock.'''
        composite_density = 0.0
        feedstocks = re.findall(r'([A-Za-z]+)(\d+)', self.name)

        for feedstock_name, percent_str in feedstocks:
            percent = float(percent_str) / 100
            feedstock = feedstock_manager.get_feedstock(feedstock_name)
            composite_density += feedstock.density * percent

        self.density = composite_density
        
    def compute_moisture(self, feedstock_manager: object):
        '''Calculate and set the moisture content for a composite feedstock.'''
        composite_moisture = 0.0
        composite_mc_std = 0.0
        feedstocks = re.findall(r'([A-Za-z]+)(\d+)', self.name)

        for feedstock_name, percent_str in feedstocks:
            percent = float(percent_str) / 100
            feedstock = feedstock_manager.get_feedstock(feedstock_name)
            composite_moisture += feedstock.moisture * percent
            composite_mc_std += (feedstock.moisture_std * percent) ** 2

        self.moisture = composite_moisture
        self.moisture_std = composite_mc_std ** 0.5
    
    def compute_quantity(self, feedstock_manager: object):
        '''Calculate and set the quantity for a composite feedstock.'''
        composite_quantity = 0.0
        feedstocks = re.findall(r'([A-Za-z]+)(\d+)', self.name)

        for feedstock_name, percent_str in feedstocks:
            percent = float(percent_str) / 100
            feedstock = feedstock_manager.get_feedstock(feedstock_name)
            composite_quantity += feedstock.quantity * percent

        self.quantity = composite_quantity
        
    def compute_water_added(self):
        '''Calcuate and set the amount of water needed to reach an ideal moisture content for feedstocks'''
        ideal_mc = self.moisture_content_target
        if ideal_mc > self.moisture:
            water_needed =  (self.quantity * (1 - ideal_mc)) / (1 - self.moisture)
            self.water_added = water_needed
            self.moisture = ideal_mc
            return water_needed

        else: 
            return self.water_added
    
    def get_wet_hhv(self) -> float:
        """Calculate and return the wet higher heating value (HHV)"""
        return self.hhv * (1 - self.moisture / 100)

    def total_energy_content(self) -> float:
        """Calculate and return the total energy content"""
        dry_hhv = self.get_dry_hhv()
        return dry_hhv * self.quantity

    def total_weight(self) -> float:
        """Calculate and return the total weight with added water"""
        return self.quantity + self.water_added

    # def get_BW_parameters(self) -> dict:
    #     """Create a dictionary with keys 'name' and 'amount' for float attributes."""
    #     result = []
    #     for attr, value in self.__dict__.items():
    #         if isinstance(value, float):
    #             result.append({'name': attr, 'amount': value})
    #     return result
        
    def __repr__(self):
        return (f"Feedstock(name={self.name}, hhv={self.hhv}, hhv_std={self.hhv_std}, "
                f"moisture={self.moisture}, moisture_std={self.moisture_std}, density = {self.density}, "
                f"moisture_target={self.moisture_content_target}, water_added={self.water_added}, quantity={self.quantity}, "
                f"temp={self.temp}C, time={self.time}hr)")
    
class FeedstockManager:
    '''
    Stores all created feedstocks in a list.
    '''
    def __init__(self):
        self.feedstocks = []

    def add_feedstock(self, feedstock: Feedstock):
        '''Adds a feedstock to Feedstock Manager'''
        self.feedstocks.append(feedstock)
        
    def delete_feedstock(self, name: str):
        '''Deletes a feedstock from Feedstock Manager'''
        if name in self.feedstocks:
            del self.feedstocks[name]
        else:
            raise ValueError(f"Feedstock with name '{name}' not found.")

    def get_feedstock(self, name: str, temp: int, time: int) -> Feedstock:
        '''Returns a Feedstock object, given a valid feedstock name, reaction temp, and reaction time'''
        for feedstock in self.feedstocks:
            if feedstock.name == name and feedstock.temp == temp and feedstock.time == time:
                return feedstock
        raise ValueError(f"Feedstock with name '{name}' not found.")
    
    def duplicate_feedstock(self, original_name: str, new_name: str, temp: int, time: int):
        '''Duplicates a feedstock based on name & returns the new feedstock'''
        original_feedstock = self.get_feedstock(original_name, temp, time)
        new_feedstock = Feedstock(
            name=new_name,
            hhv=original_feedstock.hhv,
            hhv_std=original_feedstock.hhv_std,
            moisture=original_feedstock.moisture,
            density= original_feedstock.density, 
            moisture_std=original_feedstock.moisture_std, 
        )
        
        new_feedstock.temp = original_feedstock.temp
        new_feedstock.time = original_feedstock.time
        new_feedstock.water_added = original_feedstock.water_added
        new_feedstock.quantity = original_feedstock.quantity
        
        self.add_feedstock(new_feedstock)
        return new_feedstock

    def __repr__(self):
        return f"FeedstockManager(feedstocks={self.feedstocks})"    
      

def create_elementary_feedstocks() -> object:
    '''
    Returns initial feedstocks for use
    '''     
    elementary_feedstocks = FeedstockManager()
    df = pd.read_excel('experimental-data/HTC_yield_HHV.xlsx',sheet_name='FeedsProperties', engine='openpyxl')
    HTC_temp = [190, 220, 250]
    HTC_reaction_time = [1,3]
    
    for index, row in df.iterrows():
        for temp in HTC_temp: 
            for time in HTC_reaction_time: 
                name = 'raw' + row['Feed']
                hhv = row['HHV']
                hhv_std = row['HHV_std']
                moisture = row['moisture']
                moisture_std = row['moisture_std']
                density = row['density']

                # Create a Feedstock object
                feedstock = Feedstock(name=name, hhv=hhv, hhv_std=hhv_std, moisture=moisture, 
                                      moisture_std=moisture_std, density=density)         
                feedstock.temp = temp
                feedstock.time = time
                
                # Add to elementary_feedstocks 
                elementary_feedstocks.add_feedstock(feedstock)
                
                # Setting up infrastructure for standard feedstocks 
                if feedstock.name == "rawBSG" or feedstock.name == "rawSRU": 
                    new_feedstock = elementary_feedstocks.duplicate_feedstock(feedstock.name, "std" + feedstock.name[3:], 
                                                                              feedstock.temp, feedstock.time)
                    new_feedstock.temp = temp
                    new_feedstock.time = time
                    
    return elementary_feedstocks

# excluded_feedstocks = {"rawSRU", "rawBSG"}
# for attr, feedstocks in elementary_feedstocks.__dict__.items():
#     for feedstock in feedstocks:
#         if feedstock.name not in excluded_feedstocks:
#             print(feedstock.name, feedstock.time, feedstock.temp)


# # Creating stdSRU & stdBSG 
# def create_standard_feedstock(name, feedstock_manager): 

#     feedstocks = re.findall(r'([A-Za-z]+)(\d+)', name)

#     for feedstock_name in feedstocks:
#         feedstock = feedstock_manager.get_feedstock(feedstock_name)
#         new_feedstock = feedstock
#         new_feedstock.change_name('std' + feedstock_name)
#         new_feedstock.compute_moisture()     