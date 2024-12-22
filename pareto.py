import numpy as np
import pandas as pd 

def get_pareto_front(data):
    """
    Compute the Pareto front from the given data. 
    Returns the subset of solutions that form the Pareto front.
    
    Parameters:
    ----------
    data : Pandas DataFrame
        Data containing objective values.
    
    Returns:
    ----------
    pareto_front : numpy array
        Array of points that belong to the Pareto front.
    """
    # Extract objective values (skip first column if it contains metadata)
    values = data.iloc[:, 1:].values
    
    # Initialize a boolean array to track whether each point is on the Pareto front
    pareto_front = np.ones(len(values), dtype=bool)
    
    for i, point in enumerate(values):
        # Only check points that are still on the Pareto front
        if pareto_front[i]:
            # Compare current point with all other points to check if it's dominated
            for j, other_point in enumerate(values):
                if i != j:  # Ensure the point is not compared with itself
                    if np.all(other_point <= point) and np.any(other_point < point):
                        pareto_front[i] = False
                        break 
    
    return values[pareto_front]

def is_dominant(solution, others):
    """
    Check if a solution is Pareto dominant compared to a list of other solutions.
    ----------
    solution : list or numpy array
        A solution with its objective values.
    others : list of lists or list of numpy arrays
        A list of other solutions to compare against.
    """
    for other in others:
        solution = np.array(solution)
        other = np.array(other)
        
        # Check if the solution is dominated by any other solution
        if np.all(solution >= other) and np.any(solution > other):
            return False
    return True

def pareto_sort(data):
    """
    Perform Pareto sorting of solutions. Returns a list of dominant & non-dominant solutions. 
    ----------
    data : Pandas DataFrame
        DataFrame containing the solutions with their objective values.
    """
    dominant = []
    non_dominant = []
    
    # Convert the DataFrame into a list of solutions (objective values)
    data_points = data.iloc[:, 1:].values
    
    for index, row in data.iterrows(): 
        data_point = row[1:].values 
        other_points = np.delete(data_points, index, axis=0) 
        
        # Check if the current solution is dominant
        if is_dominant(data_point, other_points): 
            dominant.append(row)
        else: 
            non_dominant.append(row)
    
    # print(dominant)
    # print(non_dominant)
    
    return dominant, non_dominant

# Example Usage
# data = {
#     'name': [
#         'rawDCW_190C_1hr', 'rawDCW_190C_3hr', 'rawDCW_220C_1hr',
#         'rawDCW_220C_3hr', 'rawDCW_250C_1hr', 'rawDCW_250C_3hr',
#     ],
#     'Feedstock': [0.139794, 0.197610, 0.194290, 0.197328, 0.204882, 0.226768],
#     'Hydrochar': [0.023153, 0.021523, 0.021611, 0.023462, 0.022759, 0.023965],
#     'Hydrochar HHV': [0.814466, 0.767980, 0.747878, 0.814756, 0.756450, 0.792650],
# }
# data = pd.DataFrame(data)
# print(get_pareto_front(data))
# dominant, non_dominant = pareto_sort(data)
# print(non_dominant)
