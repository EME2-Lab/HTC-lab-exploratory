import re 
import pandas as pd

class Feedstock:
    '''
    Creates a feedstock to be utilized by the hydrothermal carbonization model(s). 
    '''
    def __init__(self, name: str, hhv: float = 0.0, hhv_std: float = 0.0,
                 moisture: float = 0.0, moisture_std: float = 0.0, density: float = 0.0):
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
            
        Parameters:
        name (str): The name of the feedstock.
        hhv (float): The higher heating value (HHV) of the feedstock.
        hhv_std (float): The standard deviation of the HHV.
        moisture (float): The moisture content of the feedstock.
        moisture_std (float): The standard deviation of the moisture content.
        water_added (float): The amount of water added, in a mass measurement.
        density (float): The density of the feedstock mixture (without water) in kg/m^3.  
        quantity (float): The quantity of a feedstock or composite feedstock in a mixture. 
        '''
        self.name = name
        self.hhv = hhv
        self.hhv_std = hhv_std
        self.moisture = moisture
        self.moisture_std = moisture_std
        self.density = density
        self.water_added = 0.0
        self.quantity = 0.0

    def change_name(self, name: float):
        '''
        Setting a new name for a feedstock. 
        '''
        self.name = name
        
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

    def set_density(self, density: float):
        self.density = density
        
    def set_water_added(self, water_added: float):
        self.water_added = water_added

    def set_quantity(self, quantity: float):
        '''
        Sets quantity of feedstock without the addition of water for a feedstock with known values. 
        '''
        self.quantity = quantity

    def compute_hhv(self, feedstock_manager):
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

    def compute_density(self, feedstock_manager):
        '''Calculate and set the density for a composite feedstock.'''
        composite_density = 0.0
        feedstocks = re.findall(r'([A-Za-z]+)(\d+)', self.name)

        for feedstock_name, percent_str in feedstocks:
            percent = float(percent_str) / 100
            feedstock = feedstock_manager.get_feedstock(feedstock_name)
            composite_density += feedstock.density * percent

        self.density = composite_density
        
    def compute_moisture(self, feedstock_manager):
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
    
    def compute_quantity(self, feedstock_manager):
        '''Calculate and set the quantity for a composite feedstock.'''
        composite_quantity = 0.0
        feedstocks = re.findall(r'([A-Za-z]+)(\d+)', self.name)

        for feedstock_name, percent_str in feedstocks:
            percent = float(percent_str) / 100
            feedstock = feedstock_manager.get_feedstock(feedstock_name)
            composite_quantity += feedstock.quantity * percent

        self.quantity = composite_quantity
        
    def compute_water_added(self, ideal_mc: float):
        '''Calcuate and set the amount of water needed to reach an ideal moisture content'''
        if ideal_mc < self.moisture:
            water_needed =  (self.quantity * (1 - ideal_mc)) / (1 - self.moisture)
            self.water_added = water_needed
            return water_needed

        else: 
            return 0
    
    def get_dry_hhv(self) -> float:
        """Calculate and return the dry higher heating value (HHV)"""
        return self.hhv * (1 - self.moisture / 100)

    def total_energy_content(self) -> float:
        """Calculate and return the total energy content"""
        dry_hhv = self.get_dry_hhv()
        return dry_hhv * self.quantity

    def total_weight(self) -> float:
        """Calculate and return the total weight with added water"""
        return self.quantity + self.water_added

    def __repr__(self):
        return (f"Feedstock(name={self.name}, hhv={self.hhv}, hhv_std={self.hhv_std}, "
                f"moisture={self.moisture}, moisture_std={self.moisture_std}, density = {self.density}, "
                f"water_added={self.water_added}, quantity={self.quantity})")
    
class FeedstockManager:
    '''
    Stores all created feedstocks in a list.
    '''
    def __init__(self):
        self.feedstocks = []

    def add_feedstock(self, feedstock: Feedstock):
        self.feedstocks.append(feedstock)
        
    def delete_feedstock(self, name: str):
        if name in self.feedstocks:
            del self.feedstocks[name]
        else:
            raise ValueError(f"Feedstock with name '{name}' not found.")

    def get_feedstock(self, name: str) -> Feedstock:
        for feedstock in self.feedstocks:
            if feedstock.name == name:
                return feedstock
        raise ValueError(f"Feedstock with name '{name}' not found.")

    def __repr__(self):
        return f"FeedstockManager(feedstocks={self.feedstocks})"    
      
 
# Create Feedstock objects
elementary_feedstocks = FeedstockManager()
df = pd.read_excel('experimental-data/HTC_yield_HHV.xlsx', sheet_name='FeedsProperties')

for index, row in df.iterrows():
    name = 'raw' + row['Feed']
    hhv = row['HHV']
    hhv_std = row['HHV_std']
    moisture = row['moisture']
    moisture_std = row['moisture_std']
    density = row['density']

    # Create a Feedstock object
    feedstock = Feedstock(name=name, hhv=hhv, hhv_std=hhv_std, moisture=moisture, moisture_std=moisture_std, density=density)
    
    # Add to elementary_feedstocks 
    elementary_feedstocks.add_feedstock(feedstock)

print(elementary_feedstocks)

# # Creating stdSRU & stdBSG 
# def create_standard_feedstock(name, feedstock_manager): 

#     feedstocks = re.findall(r'([A-Za-z]+)(\d+)', name)

#     for feedstock_name in feedstocks:
#         feedstock = feedstock_manager.get_feedstock(feedstock_name)
#         new_feedstock = feedstock
#         new_feedstock.change_name('std' + feedstock_name)
#         new_feedstock.compute_moisture()     