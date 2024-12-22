import openpyxl

class HydrocharLCIA: 
    '''
    Stores Life Cycle Impact Assessment (LCIA) results for producing hydrochar from food waste
    for different feedstock names & conditions. 
    '''
    def __init__(self, name):
        self.name = name
        self.water_use = self.create_impact_dict()
        self.energy_resources = self.create_impact_dict()
        self.acidification = self.create_impact_dict()
        self.climate_change = self.create_impact_dict()
        self.ecotoxicity_freshwater = self.create_impact_dict()
        self.eutrophication = self.create_impact_dict()
        self.human_toxicity_carcinogenic = self.create_impact_dict()
        self.human_toxicity_noncarcinogenic = self.create_impact_dict()
        self.ozone_depletion = self.create_impact_dict()
        self.particulate_matter_formation = self.create_impact_dict()
        self.photochemical_oxidant_formation = self.create_impact_dict()
        
    def create_impact_dict(self):
        '''Creates impact dictioniary with process categories.'''
        categories = ['Water', 'Electricity - HTC', 'Heat-HTC', 'CO2 - HTC', 'Wastewater', 'Electricity - Post-Processing']
        return {category: {'score': 0.0, 'unit': ''} for category in categories}

    def set_impact_score(self, impact_category, process_category, score, unit):
        '''
        Sets an impact score given a LCIA category, process category, and score.
        Parameters: 
            impact_category: str
            process_category: str
            score: float
            unit: float
        '''
        if hasattr(self, impact_category):
            impact_data = getattr(self, impact_category)
            if process_category in impact_data:
                impact_data[process_category]['score'] = score
                impact_data[process_category]['unit'] = unit
            else:
                impact_data[process_category] = {'score': score, 'unit': unit}
        else:
            raise ValueError(f"Impact category '{impact_category}' does not exist.")

    def get_impact_score(self, impact_category, process_category):
        '''
        Gets an impact score given a LCIA category and process category. 
        '''
        if hasattr(self, impact_category):
            impact_data = getattr(self, impact_category).get(process_category, None)
            if impact_data:
                return impact_data['score']
            else:
                return None
        else:
            raise ValueError(f"Impact category '{impact_category}' does not exist.")
    
    def get_impact_unit(self, impact_category, process_category):
        if hasattr(self, impact_category):
            impact_data = getattr(self, impact_category).get(process_category, None)
            if impact_data:
                return impact_data['unit']
            else:
                return None
        else:
            raise ValueError(f"Impact category '{impact_category}' does not exist.")
        
    def get_total_impact_score(self, impact_category):
        '''
        Gets a total impact score given a LCIA category. 
        '''
        if hasattr(self, impact_category):
            impact_dict = getattr(self, impact_category)
            return sum(impact['score'] for impact in impact_dict.values())
        else:
            raise ValueError(f"Impact category '{impact_category}' does not exist.")
    
    def get_impact_categories(self):
        '''Returns a list of available impact categories.'''
        return [attr for attr in self.__dict__ if attr != 'name']

    def get_process_categories(self):
        '''Returns a list of available process categories.'''
        if self.__dict__:
            first_impact_category = self.get_impact_categories()[0]
            return list(getattr(self, first_impact_category).keys())
        return []

class HydrocharLCIAManager:
    '''
    Stores all created hydrochar LCIA objects in a list.
    '''
    def __init__(self):
        self.hydrochar_lcias = []

    def add_hydrochar(self, hydrochar: HydrocharLCIA):
        '''Adds a feedstock to Hydrochar LCIA Manager'''
        self.hydrochar_lcias.append(hydrochar)

    def delete_hydrochar(self, name):
        self.hydrochar_lcias = [hydrochar_lcia for hydrochar_lcia in self.hydrochar_lcias if hydrochar_lcia.name != name]

    def get_hydrochar(self, name):
        for hydrochar_lcia in self.hydrochar_lcias:
            if hydrochar_lcia.name == name:
                return hydrochar_lcia
        return None
    
