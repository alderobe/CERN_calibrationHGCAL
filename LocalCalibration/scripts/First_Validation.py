
import ROOT
import pandas as pd
import json
import numpy as np
import csv
from scipy.stats import chi2
from math import sqrt

'''
Ora sto pensando i moduli come diversi, l'idea è di avere un file JSON simile per tutti i moduli e poi fare un confronto
 con le constanti di calibrazione ottenute al passaggio di calibrazione precedente
'''


def fillHexPlot(ch_values,flag_name,up, low, moduletype='LD_full'):

	"""
    this method takes care of instatiating a hexplot for a given module type and fill it with the values for the required channels
    ch_values is a dict of (channel number, value)
    module_type is a string with the module type to be used in the hexplot.
    flag_name is a string and denotes the variable according to which we want to reject or accept the single channel of the module
    up and low determine the range of the flag variable
    
	"""
	
	from array import array

	# Create a custom color palette
	ncolors = 100

	# Define the RGB points for the color palette
	stops = [0.0, 0.5, 1.0]
	red = [0.0, 1.0, 1.0]
	green = [0.0, 1.0, 0.0]
	blue = [1.0, 1.0, 0.0]

	# Create the color palette
	ROOT.TColor.CreateGradientColorTable(len(stops), array('d', stops), array('d', red), array('d', green), array('d', blue), ncolors)
	ROOT.gStyle.SetNumberContours(ncolors)
	#create the hexplot
	hex_plot = ROOT.TH2Poly()
	hex_plot.SetDirectory(0)
	fgeo=ROOT.TFile.Open(f'/eos/cms/store/group/dpg_hgcal/comm_hgcal/ykao/geometry_{moduletype}_wafer_20230919.root','R')
	i=0
	for key in fgeo.GetListOfKeys():
		obj = key.ReadObj()
		if not obj.InheritsFrom("TGraph") : continue
		hex_plot.AddBin(obj)
        
		idx = int(i - (i / 39) * 2);
		#isCM = i%39 in [37,38]
		if idx in ch_values:
			hex_plot.SetBinContent(i+1,ch_values[idx])
		
		i+=1
	
	hex_plot.GetZaxis().SetRangeUser(low, up)
	fgeo.Close()
	#ROOT.gStyle.SetPalette("kBird")
	c1 = ROOT.TCanvas()
	hex_plot.SetStats(0)
	hex_plot.Draw("colz")
	c1.Draw()
	c1.SaveAs(f"scripts/Hexplots/flag_{flag_name}.png")
  


def chi2_confidence_interval_std(n, sample_std, confidence_level=0.40):
	''' 
	This module returns the confidence interval for the rms 
	n is the number of measurements
	sample_std is the estimator of the std
	the confidence level could be changed to increase or decrease the "flag" range
	'''

	# Degree of freedom
	df = n - 1
	    
	# evaluation of percentiles fro the chi2 distribution
	alpha = 1 - confidence_level
	chi2_lower = chi2.ppf(alpha / 2, df)
	chi2_upper = chi2.ppf(1 - alpha / 2, df)
	    
	# confidence interval for the variance
	lower_bound_variance = (df * (sample_std)**2) / chi2_upper
	upper_bound_variance = (df * (sample_std)**2) / chi2_lower
	    
	# confidence interval for the std
	lower_bound_std = np.sqrt(lower_bound_variance)
	upper_bound_std = np.sqrt(upper_bound_variance)
	    
	return lower_bound_std, upper_bound_std
	

def JSONtoPandasDataframe(JSON_fileDirectory):
	'''
	This module converts the JSON file  { "Module1": {"ADC_ped": [120, ...], "Noise": [...], ...}, "Module2": ...} 
	into a list of Pandas DataFrame (the index of the list represents the number of the module)
	'''
	# Load the JSON file
	with open(f'{JSON_fileDirectory}') as file:
		data = json.load(file)
	# Initialize an empty list to store DataFrames
	df_list = []

	# Iterate over each module
	for module, record in data.items():
		# Create a DataFrame from the record
		df = pd.DataFrame(record)
		# Add a column to identify the module
		#df['Module'] = module    #maybe we can just consider the index of the list as our module index
		# Append the DataFrame to the list
		df_list.append(df)
	
	# I think that the following is not necessary since we want different dataframes for each modules Or we can do pd.concat but every time we need to count the number of channel and stop when this number is a multiple of a specific number of channels in the module
	
	# Concatenate all DataFrames into a single DataFrame
	#combined_df = pd.concat(df_list, ignore_index=True)

	# Display the combined DataFrame
	# print(combined_df)
	
	return df_list

def RefMeanRMSPed(df_list, FlaggedModules):
	'''
	This module returns the reference value of the Ped and the RMS at the beginning of the validation step
	FlaggedModules is a list of indexes related to each module flagged in the previous validation. At the beginning, 
	should it be initialised (or it should be empty?)
	'''
	ref_mean_ped = 0
	ref_rms_ped = 0
	cont = 0
	i = 0
	for i, df in enumerate(df_list):
	
	# I want to compute the reference values as the mean among "good" modules.
	
		if i not in FlaggedModules: 
			cont += 1
			ref_mean_ped += np.mean(df["ADC_ped"])
			ref_rms_ped += np.std(df["ADC_ped"])
		else: continue
			
	# Each channel has an average pedestal, I am taking the mean among all channels in the same module so that each module is characterized by a single pedestal value. Then, among the "good" module I am taking the mean. The latter represents the reference Pedestal of the full set of module which I am looking at 
	
	ref_mean_ped = ref_mean_ped/cont 
	ref_rms_ped = ref_rms_ped/cont
	
	return ref_mean_ped, ref_rms_ped
	


def Mean_RMS_selection(mean_ped,ref_mean_ped, rms_ped, ref_rms_ped, lower_bound_std, upper_bound_std,alpha = 0.5):
	'''
	This module returns cont_mean = False if the channel/module is "good" cont_mean = True if it is bad. The same for cont_rms.
	mean_ped could be the mean pedestal of the module or the pedestal of the single channel.
	lower_bound_std, upper_bound_std and alpha define the "rejection" region. These parameters should be decreased in order to have a more strict selection or should be increased when, for instance we want to reset the system. In the latter case if alpha is sufficiently high we could empty the FlaggedModules in the subsequent validation
	
	'''
	cont_mean = False
	cont_rms = False
	
	if mean_ped < (ref_mean_ped - alpha*ref_rms_ped) or mean_ped > (ref_mean_ped + alpha*ref_rms_ped):
		cont_mean = True
	if rms_ped < lower_bound_std or rms_ped > upper_bound_std:
		cont_rms = True
	#print(f"{ref_mean_ped}+/-{alpha*ref_rms_ped}")
	#print(f"{ref_rms_ped}  [{lower_bound_std},{upper_bound_std}]")
	return cont_mean, cont_rms
		
	


def ValidationModule_ped(df_list,ref_mean_ped, ref_rms_ped):
	'''
	This module returns the list of indexes associated to flagged modules. There are two type of flagging. One module is flagged if it has a very different average pedestal (among the average pedestals of each channel) compared to the previous "good" one or if it has a very different RMS among avg pedestals compared to the previous "good" one.
	'''
	# Lists which contain the indexes of "bad" modules
	flagged_modules_mean = []
	flagged_modules_rms = []
	
	#Setting the rejection area
	lower_bound_std, upper_bound_std = chi2_confidence_interval_std(NumModules-len(FlaggedModules), ref_rms_ped, confidence_level=0.4)
	alpha = 0.5
	
	# iteration over modules
	for i,df in enumerate(df_list):
	
		# mean ped of the module
		mean_ped = np.mean(df["ADC_ped"])
		
		# rms of the module (statistically this quantity should be rougly equal to sqrt(NumChannels)*(mean of the channel noise of the module))
		rms_ped = np.std(df["ADC_ped"])
		
		#Checking if the mean_ped or the rms_ped are good or not
		test_mean, test_rms = Mean_RMS_selection( mean_ped,ref_mean_ped, rms_ped, ref_rms_ped , lower_bound_std, upper_bound_std, alpha)
		if test_mean:
			flagged_modules_mean.append(i)
		if test_rms:
			flagged_modules_rms.append(i)
			
	return flagged_modules_mean, flagged_modules_rms 
	#oppure si potrebbe fare un dizionario con due key una per i flag dei ped e una per i flag dei rms
	
def ValidationChannels_ped(df_list, ref_mean_ped, ref_rms_ped, Modlist_flag):
	'''
	For each flagged module we want to inspect further what has caused the issue. Channel by channel
	'''
	# Lists which contain the indexes of "bad" channels
	#flagged_channels_mean = []
	#flagged_channels_rms = []
	NumChannels = 222
	
	filename1 = "Delta_ped_MOD"
	filename2 = "Delta_noise_MOD"
	
	ref_rms_ped_channels = ref_rms_ped/sqrt(NumChannels) #This could be a trick to evaluate the mean of the noise per each channel
	
	#iteration over "bad" modules
	for i,df in enumerate(df_list):
		if i in Modlist_flag:
			# aggiungo al dataframe 2 colonne che corrispondono a Delta_ped (la differenza tra il piedistallo di riferimento per il seguente ciclo di calibrazione e il piedistallo del singolo canale) e analogamente Delta_noise
			# definition of two new coulumns. Delta_ped represents the difference between the ref_ped and the channel ped. Delta_noise is the difference between the ref rms (channel) and the channel noise
			df["Delta_ped"] = ref_mean_ped - df["ADC_ped"]
			df["Delta_noise"] = ref_rms_ped_channels - df["Noise"]
			
			#here I should insert the part where I am rejecting the "bad" channels
			
			# plotting to visualize which are the "strange" channels
			fillHexPlot(df["Delta_ped"].to_dict(),f"Delta_ped_MOD{i}",up = 120, low = -120)
			fillHexPlot(df["Delta_noise"].to_dict(),f"Delta_noise_MOD{i}",up = 2, low = -2)
			
			
	#return flagged_channels_mean, flagged_channels_rms  questo lo aggiungi poi considerando di restituire anche una lista per tutti quei canali non funzionanti. dovrei anche restituire cosa non funziona? piedistallo troppo alto troppo basso ecc?
	
JSON_fileDirectory = "./Pedestals/Run1710429303/Pedestals_Run_1710429303_80fC_6Modules.json"
NumModules = 6
FlaggedModules = [0]  #By eye the first module has a non-workin section
# inizializzala con argparse potresti fare un file con gli indici e poi convertirle in una lista

def main():
	 
	dfPandas_list = JSONtoPandasDataframe(JSON_fileDirectory)
	ref_mean_ped, ref_rms_ped  = RefMeanRMSPed(dfPandas_list,FlaggedModules)
	
	#print(ref_mean_ped)
	#print(ref_rms_ped)
	
	#Verifico i moduli
	flagMod_mean, flagMod_rms = ValidationModule_ped(dfPandas_list, ref_mean_ped, ref_rms_ped)
	#print(flagMod_mean)
	#print(flagMod_rms)
	
	union_set = set(flagMod_mean) | set(flagMod_rms)
	Modlist_flag = list(union_set)
	
	ValidationChannels_ped(dfPandas_list, ref_mean_ped, ref_rms_ped,Modlist_flag)
	
	
	
    
if __name__ == "__main__":
	main()
