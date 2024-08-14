import json
import csv
import numpy as np
import ROOT
import os

# The module shows the JSON file and return the corresponding python dictionary with its dimension (i.e. # of modules inspected) and the dimension of the first key (i.e. # of channels)
def display_json(file_path):
    # Open JSON file in reading mode
    with open(file_path, 'r', encoding='utf-8') as file:
        # convert json obj into python dict (data)
        data = json.load(file)
        # Show the dict
        print(json.dumps(data, indent=4))
        
    return data, len(data) , len(data[f"{Module_name}5"]["Channel"])

# This module creates CSV files (Channel, ADC_ped) corresponding to the number of modules inspected
def CSV_hexaplot(data,Num_modules,filename = "input_hexaplot_"):

		if not os.path.exists("csv_files"):
			os.makedirs("csv_files")
			
		
		for i in range(Num_modules):
		     # Extract the channel and Pedestal lists
		     Channel = data[f"{Module_name}{i}"]["Channel"]
		     ADC_ped = data[f"{Module_name}{i}"]["ADC_ped"]

		     # Prepare the rows for CSV
		     rows = list(zip(Channel, ADC_ped))

		     # Write to CSV file
		     with open(f'csv_files/{filename}{i}.csv', 'w', newline='') as csvfile:
		     		csvwriter = csv.writer(csvfile)
		     		# Write the header
		     		csvfile.write('channel ADC_ped\n')
		     		# Write the data rows
		     		for row in rows:
		     			csvfile.write(f'{row[0]} {row[1]}\n')
			  

		 

def TTreeMaker(data, Num_modules, Num_channels):
		file = ROOT.TFile("ModulesData.root", "RECREATE")
		
		module = np.zeros(1, dtype=np.int32)
		v1 = np.zeros(1, dtype=np.int64)
		v2 = np.zeros(1, dtype=np.float64)
		v3 = np.zeros(1, dtype=np.float64)
		v4 = np.zeros(1, dtype=np.float64)
		v5 = np.zeros(1, dtype=np.float64)

		for m in range(Num_modules):
                        tree = ROOT.TTree(f"Module_{m}_TTree", f"Module_{m}_TTree")
                        tree.Branch("Channel", v1, "Channel/I")
                        tree.Branch("ADC_ped", v2, "ADC_ped/D")
                        tree.Branch("CM_ped", v3, "CM_ped/D")
                        tree.Branch("CM_slope", v4, "CM_slope/D")
                        tree.Branch("Noise", v5, "Noise/D")
                        
                        mod_data = data[f"{Module_name}{m}"]
                        #forse qui devo definire le liste channel ecc e convertire con np.array
                        
                        for i in range(Num_channels):
                                module[0] = m
                                v1[0] = mod_data["Channel"][i]  # e qui scrivere Channel[i]
                                v2[0] = mod_data["ADC_ped"][i]
                                v3[0] = mod_data["CM_ped"][i]
                                v4[0] = mod_data["CM_slope"][i]
                                v5[0] = mod_data["Noise"][i]
                                tree.Fill()
                        tree.Write()
		file.Close()
    		
				    
		
# Constants, filename ecc
file_path = '/afs/cern.ch/user/a/alderobe/HGCalCommissioning/LocalCalibration/Pedestals/Run1722725783/pedestals_160fC.json'
CSV_filename = "input_hexaplot"
Module_name = "ML_F3WX_IH000"

def main():
		data, Num_Modules, Num_channels = display_json(file_path)
		print("------------CSV files have been created successfully.-----------/n")
		CSV_hexaplot(data, Num_Modules)
		TTreeMaker(data,Num_Modules,Num_channels)
		print(Num_channels)
		
if __name__ == "__main__":
		main()
		
