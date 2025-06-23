# HTC Lab Exploratory: Ogunnaike <i>et al.</i> (2025); in prep
<b>Environmental Trade-offs in Hydrothermal Carbonization Process Selection Determined via Attributional Life Cycle Assessment and Multi-Criteria Decision Making</b>

Ogunnaike, Demola<sup>1</sup>, Srikrishnan, Vivek<sup>1,2</sup>, Goldfarb, Jillian L.<sup>1,2,3*</sup>

<sup>1</sup> Systems Engineering, Cornell University, Ithaca, New York 14853, USA <br>
<sup>2</sup> Biological & Environmental Engineering Department, Cornell University, Ithaca, NY, 14853, USA <br>
<sup>3</sup> Robert Frederick Smith School of Chemical and Biomolecular Engineering, Cornell University, Ithaca, NY, 14853, USA <br>

\* corresponding author: [goldfarb@cornell.edu](mailto:goldfarb@cornell.edu) 

# Abstract
Hydrothermal  carbonization (HTC) is a thermochemical process that upgrades wet agro-industrial and food waste feedstocks into a solid hydrochar with coal-like properties. Despite its ability to mitigate environmental impacts from food waste and produce a bioenergy resource, HTC integrated biorefineries have not progressed beyond pilot scale. Identifying favorable reaction conditions that can simultaneously reduce environmental externalities and improve economic performance can enhance viability.   Here we conduct a prospective lab scale gate-to-gate attributional life cycle assessment (ALCA) of an HTC-based biorefinery based on the three largest food waste sources subject to the 2022 New York State Food Donation and Food Scraps Recycling Law  . We demonstrate how process details in HTC, including feedstock choice and reaction condition choice, affect environmental impacts. Using multi-objective systems optimization and multi-criteria decision making to consider trade-offs in HTC’s functionality, we identify that mixtures of food waste source feedstocks have smaller environmental impacts than any individual food waste source feedstock. 

# Acknowledgements 
DO was partially funded by the the National GEM Consortium and Robert F. Smith Fellowship at Cornell University and the National Science Foundation CBET Grant 2144862. VS was partially funded by the Biological and Environmental Research Program. JLG was partially funded by the National Science Foundation CBET Grant 2144862. This research was conducted with support from the Cornell University Center for Advanced Computing.

## Data References & Dependencies 

Before using this repository, ensure you meet the following requirements:

1. **Brightway2.5 Environment**:
   - This repository assumes the use of **Brightway 2.5** for Life Cycle Assessment (LCA) calculations. Ensure your Python and pip version is compatible with Brightway 2.5. For more information, see [Brightway2 Documentation](https://brightway.dev). This analysis was conducted using Python 3.10.0 and pip 24.3.1.

2. **Datasets**:
   - You must have ecoinvent datasets compatible with Brightway 2.5. These should include the required Life Cycle Inventory (LCI) databases.
   - While impact assessment and other results can be downloaded, the analyis cannot be run without ecoinvent. 
   - Place these datasets in a folder that can be accessed from the location of the cloned repository. For example:
     ```
     .
     ├── ecoinvent_v3.10
     │   ├── cutoff 
     │      ├── relevant datasets and MasterData compatible with Brightway 2.5. 
     ├── main folder 
     │   ├── HTC-lab-exploratory

Access to a cluster for high-performance computing is highly recommended, though this script can be run on a local desktop in a reasonable timeframe, if needed. Here are some helpful resources that may be helpful for comprehending key components  
- [Industrial Ecology Open Online Course](https://www.industrialecology.uni-freiburg.de/teaching): Foundations of Industrial Ecology.  
- [Brightway LCA Software Framework](https://docs.brightway.dev/en/latest/index.html): Brightway 2.5 Python Documentation.  
- [Brightway Tutorials](https://learn.brightway.dev/en/latest/content/home.html): “Learn Brightway” Book.  
- [Additional Brightway Resources](https://wiki.ubc.ca/Documentation:Brightway_Tutorials): Documentation: Brightway Tutorials.  
- [LCA Textbook](https://app.boxcn.net/s/5mnzyq1y3gcyjrveubf4/folder/52228826119).  
- [Ecoinvent Database](https://ecoquery.ecoinvent.org/3.10/cutoff/search): Requires a license to view data.  

## Folder Structure

This repository includes the following main folders:

- **`experimental-data`**: Contains experimental data from the studies:
  - [Pecchi *et al.* (2022)](https://www.sciencedirect.com/science/article/pii/S0960852422001286?via%3Dihub)
  - [Kassem *et al.* (2022)](https://pubs.acs.org/doi/10.1021/acssuschemeng.2c04188)
- **`results`**: Contains Life Cycle Impact Assessment (LCIA) results and data on TOPSIS scores and uncertainty analysis relevant to the project.

Analysis was mainly done in the Jupyter notebook, `HTC-Uncertainty.ipynb`. Other Python files in the repository include helper functions designed for organizational purposes and to support the main analyses.

## Reproduction

### 1. Setting up your virtual environment
We assume that you have seen and used virtualenv, but if not, go [here](https://docs.python.org/3/library/venv.html) to install. 

```bash
# Create a new python3 virtualenv named venv.
virtualenv -p python3 venv
# Activate the environment
source venv/bin/activate
venv\Scripts\activate # for Windows

# Install all requirements
pip install -r requirements.txt
```
### 2. Running Jupyter Notebook 
Select the virtual environment kernel and run the cells in the Jupyter notebook, `HTC-Uncertainty.ipynb`.

### Troubleshooting

In the example above, we created a virtual environment for a Python 3 environment and installed the necessary requirements based on the current setup. While I don't *anticipate* issues running the script in a newly created environment, there have been [reported issues](https://brightway.groups.io/g/development/topic/brightway2_io_bw2io/94865283?p=,,,20,0,0,0::recentpostdate/sticky,,,20,2,0,94865283,previd%3D1667841452571356602,nextid%3D1637964654927686290&previd=1667841452571356602&nextid=1637964654927686290) in Brightway 2.5 when using newer versions of ecoinvent. Here are some troubleshooting tips to help ensure a smooth setup: 

1. **Create a Virtual Environment**:
   - Follow standard instructions to create a virtual environment for Python 3.

2. **Installing Dependencies**:
   - If the `requirements.txt` file does not work:
     - On Windows:
       ```bash
       pip uninstall -r requirements.txt -y
       ```
     - On Linux or macOS:
       ```bash
       pip freeze | xargs pip uninstall -y
       ```

3. **Install Basic Python Libraries**:
   - Install key libraries & initialize the Jupyter Notebook kernel:
     ```bash
     pip install ipykernel matplotlib pandas seaborn 
     ```

4. **Resolve Version Conflicts**:
   - Brightway 2.5 is not compatible with `numpy-2.0.1`, which may be automatically installed with `matplotlib`. To fix this:
     ```bash
     pip install numpy==1.26.4
     ```

5. **Install Brightway2 Core Packages**:
   - Install Brightway2 and initialize the project:
     ```bash
     pip install brightway2
     ```
   - Set up the project and initialize the biosphere flows.

6. **Install Brightway 2.5 and Supporting Libraries**:
   - Restart the Python environment (e.g., restart Jupyter Notebook or your terminal session) before proceeding.
   - Install the necessary dependencies for importing the ecoinvent database by running:
     ```bash
     pip install -r requirements.txt 
     ```
    Upon successful installation, skip the `bi.bw2setup()` codeblock, as the biosphere has been initalized using Brightway2. Prior to conducting LCA calculations, the project will be upgraded to a Brightway 2.5 environment that's compatible with the Brightway 2.5 package. 
    
    ⚠️ Note: Directly installing `brightway25 pypardiso` may cause import errors when working with the ecoinvent database due to ongoing development of the Brightway package. The `requirements.txt` file includes tested dependencies for this project’s environment. 

### Alternative Package Management

For better package control, consider using [Anaconda](https://www.anaconda.com) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html). These tools allow you to manage dependencies more effectively in isolated environments.

For trouble-shooting, general questions, or other inquiries, contact the developer, Demola Ogunnaike, at **dko22[at]cornell.edu**
