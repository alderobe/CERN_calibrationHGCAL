import ROOT
import pandas as pd
import json
import numpy as np
import csv
from scipy.stats import chi2
from math import sqrt

'''
The idea of this code is the following:
	-input = JSON file containing the data coming from a large set of silicon module (e.g. a layer of the CE-E compartment)
	-output = 1) Set of names of flagged modules
		  2) Hexplots of flag variables (Delta_Noise, Delta_ped) for flagged modules 
		  3) dictionary of flagged ch {Flagged_Module_name:[list of indices of ch], ... }
	N.B. This code needs two variables to be initialized:
			- NumModules_good in ValidationModule_ped which defines the number of "good" modules in the current validation step (= NumModules - len(FlaggedModules))
			- FlaggedModules is a list of "bad" modules (string type name) coming from the previous validation step
			
The script must be run in the /LocalCalibration directory
		  
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
	ROOT.TColor.CreateGradientColorTable(len(stops), array('d', stops), array('d', blue), array('d', green), array('d', red), ncolors)
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
	hex_plot.SetTitle(flag_name)
	hex_plot.SetStats(0)
	hex_plot.Draw("colz")
	c1.Draw()
	c1.SaveAs(f"scripts/Hexplots/flag_{flag_name}.png")
  


def chi2_confidence_interval_std(n, sample_std, confidence_level=0.7):
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
	into a dict key = Module (ML-FAA-BBB) item = Pandas DataFrame 
	'''
	# Load the JSON file
	with open(f'{JSON_fileDirectory}') as file:
		data = json.load(file)
	# Initialize an empty dict to store DataFrames
	df_dict = {}

	# Iterate over each module
	for module, record in data.items():
		# Create a DataFrame from the record
		df = pd.DataFrame(record)
		
		# Creat a dict {Module: PandasDataFrame,}
		df_dict[module] = df
	
	
	return df_dict

def RefMeanRMSPedNoise(df_dict, FlaggedModules):
	'''
	This module returns the reference values of the Ped and the Noise  at the beginning of the validation step
	FlaggedModules is a list of strings related to each module flagged in the previous validation. At the beginning, 
	it should be initialised.
	'''
	ref_mean_ped = 0
	ref_rms_ped = 0
	ref_mean_noise = 0
	ref_rms_noise = 0
	cont = 0
	i = 0
	for module, df in df_dict.items():
	
	# I want to compute the reference values as the mean among "good" modules. This is true for ADC_ped and Noise, but for the two RMS values, the sample standard deviation is used as the statistical estimator of RMS. 
	
		if module not in FlaggedModules: 
			cont += 1
			Reasonable_pedestals = []
			for ped in df["ADC_ped"]:
				if ped < 400:  #This cut could be wrong. It was introduced just for data of July test beam. Each of these 6 modules is characterized by few channels with very high pedestal. This common behaviour cannot be seen with this code unless it is used this technique.
					Reasonable_pedestals.append(ped)
			ref_mean_ped += np.mean(Reasonable_pedestals)
			ref_rms_ped += (np.std(Reasonable_pedestals))**2
			
			ref_mean_noise += np.mean(df["Noise"])
			ref_rms_noise += (np.std(df["Noise"]))**2
			
		else: continue
			
	# Each channel has an average pedestal, I am taking the mean of all channels within the same module, so that each module is characterized by a single pedestal value. Then I am taking the mean of "good" modules, which represents the reference pedestal for the entire set of modules. Same idea for the other variables with the only difference that I am taking the mean of variances for the RMS.
	
	ref_mean_ped = ref_mean_ped/cont 
	ref_rms_ped = np.sqrt(ref_rms_ped/cont)
	
	ref_mean_noise = ref_mean_noise/cont 
	ref_rms_noise = np.sqrt(ref_rms_noise/cont)
	
	return ref_mean_ped, ref_rms_ped, ref_mean_noise, ref_rms_noise
	


def Mean_RMS_selection(mean_ped,ref_mean_ped, rms_ped, ref_rms_ped,mean_noise,ref_mean_noise, rms_noise, ref_rms_noise, lower_bound_std_ped, upper_bound_std_ped,lower_bound_std_noise, upper_bound_std_noise ,alpha = 1):
	'''
	This module returns cont_mean_ped,cont_mean_noise,cont_rms_ped,cont_rms_noise = False if the module is good, and True if it is bad.
	mean_ped/mean_noise is the mean of all channels pedestal/noise within the same module. The same for rms.
	lower_bound_std, upper_bound_std and alpha define the "rejection" region. These parameters should be decreased in order to have a more strict selection or should be increased when, for instance we want to reset the system. In the latter case if alpha is sufficiently high we could empty the FlaggedModules in the subsequent validation
	
	'''
	cont_mean_ped = False
	cont_rms_ped = False
	cont_mean_noise = False
	cont_rms_noise = False
	
	if mean_ped < (ref_mean_ped - alpha*ref_rms_ped) or mean_ped > (ref_mean_ped + alpha*ref_rms_ped):
		cont_mean_ped = True
	if rms_ped < lower_bound_std_ped or rms_ped > upper_bound_std_ped:
		cont_rms_ped = True
	if mean_noise < (ref_mean_noise - alpha*ref_rms_noise) or mean_noise > (ref_mean_noise + alpha*ref_rms_noise):
		cont_mean_noise = True
	if rms_noise < lower_bound_std_noise or rms_noise > upper_bound_std_noise:
		cont_rms_noise = True
		
	
	return cont_mean_ped, cont_rms_ped, cont_mean_noise, cont_rms_noise
		
	


def ValidationModule_ped(df_dict,ref_mean_ped, ref_rms_ped, ref_mean_noise, ref_rms_noise):
	'''
	This module returns the list of strings associated to flagged modules. There are four type of flagging. 
        One module is flagged: - if it has a very different average pedestal (across channels' pedestals) compared to the reference value 
	                       - if it has a very different spread (RMS) of pedestal distribution compared to the reference value
			       - The other two conditions are the same but regarding the Noise distribution.
	'''
	NumModules_good = NumModules - len(FlaggedModules)
	# Lists which contains the indexes of "bad" modules
	flagged_modules_mean_ped = []
	flagged_modules_rms_ped = []
	
	flagged_modules_mean_noise = []
	flagged_modules_rms_noise = []
	
	#Setting the rejection area
	lower_bound_std_ped, upper_bound_std_ped = chi2_confidence_interval_std(NumModules_good, ref_rms_ped, confidence_level=0.7)
	lower_bound_std_noise, upper_bound_std_noise = chi2_confidence_interval_std(NumModules_good, ref_rms_noise, confidence_level=0.7)
	alpha = 1
	
	print(20*"-"+"Acceptance regions"+20*"-")
	print("\n")
	print("<ADC_ped>")
	print(f"{ref_mean_ped}+/-{alpha*ref_rms_ped}")
	print("\n")
	print("#sigma_{ADC_ped}")
	print(f"{ref_rms_ped}  [{lower_bound_std_ped},{upper_bound_std_ped}]")
	print("\n")
	print("<Noise>")
	print(f"{ref_mean_noise}+/-{alpha*ref_rms_noise}")
	print("\n")
	print("#sigma_Noise")
	print(f"{ref_rms_noise}  [{lower_bound_std_noise},{upper_bound_std_noise}]")
	print(48*"-")
	
	# iteration over modules
	for module, df in df_dict.items():
	
		# mean ped of the module
		mean_ped = np.mean(df["ADC_ped"])
		mean_noise = np.mean(df["Noise"])
		
		# rms of the module (statistically this quantity should be roughly equal to sqrt(NumChannels)*(mean of the channel noise of the module))
		rms_ped = np.std(df["ADC_ped"])
		rms_noise = np.std(df["Noise"])
		
		#Checking if the mean_ped or the rms_ped are good or not
		test_mean_ped, test_rms_ped, test_mean_noise, test_rms_noise = Mean_RMS_selection( mean_ped,ref_mean_ped, rms_ped, ref_rms_ped, mean_noise, ref_mean_noise, rms_noise, ref_rms_noise, lower_bound_std_ped, upper_bound_std_ped,lower_bound_std_noise, upper_bound_std_noise , alpha)
		if test_mean_ped:
			flagged_modules_mean_ped.append(module)
		if test_rms_ped:
			flagged_modules_rms_ped.append(module)
		if test_mean_noise:
			flagged_modules_mean_noise.append(module)
		if test_rms_noise:
			flagged_modules_rms_noise.append(module)
			
	return flagged_modules_mean_ped, flagged_modules_rms_ped, flagged_modules_mean_noise, flagged_modules_rms_noise
	
	
def ValidationChannels_ped(df_dict, ref_mean_ped, ref_mean_noise, Modlist_flag):
	'''
	For each flagged module we want to inspect further what has caused the issue. Channel by channel
	'''
	# dictionary which contain the indexes of "bad" channels (key = name of bad module, item = list of indexes of bad channels)
	flagged_channels_pull = {}
	
	
	NumChannels = 222
	
	
	#ref_rms_ped_channels = ref_rms_ped/sqrt(NumChannels) #This could be a trick to evaluate the mean of the noise per each channel
	
	#iteration over "bad" modules
	for module, df in df_dict.items():
		if module in Modlist_flag:
			
			# definition of two new coulumns. Delta_ped represents the difference between the ref_ped and the channel ped. Delta_noise is the difference between the ref rms (channel) and the channel noise
			df["Delta_ped"] =ref_mean_ped -  df["ADC_ped"] 
			df["Delta_noise"] = ref_mean_noise - df["Noise"]
			
			#N.B. the pull could be more intuitive as a flag variables. For instance define Pull_ped = (ref_mean_ped -  ADC_ped(ch))/ref_mean_noise
			df["Pull"] = df["Delta_ped"]/ref_mean_noise  # This definition should be checked
			
			flagged_channels_pull[module] = []
			for j, pull_value in enumerate(df["Pull"]):
				if abs(pull_value) > 1: #This condition is completely arbitrary and should be changed
					 flagged_channels_pull[module].append(j)
				
			
			
			
			
			# plotting to visualize which are the "strange" channels
			fillHexPlot(df["Delta_ped"].to_dict(),f"Delta_ped_MOD{module}",up = 120, low = -120)
			fillHexPlot(df["Delta_noise"].to_dict(),f"Delta_noise_MOD{module}",up = 2, low = -2)
	
	return flagged_channels_pull
	
	

JSON_fileDirectory = "./Pedestals/Run1710429303/Pedestals_Run_1710429303_80fC_6Modules.json"
NumModules = 6
FlaggedModules = ['ML-F3PT-TX-0003:0']  #By eye the first module has a non-working region (this comment is regarding the first set of 6 Modules)
# The previous list could be initialised with argparse 

def main():
	 
	dfPandas_dict = JSONtoPandasDataframe(JSON_fileDirectory)

	#computation of reference values
	ref_mean_ped, ref_rms_ped, ref_mean_noise, ref_rms_noise  = RefMeanRMSPedNoise(dfPandas_dict,FlaggedModules)
	
	#Module validation
	flagMod_mean_ped, flagMod_rms_ped, flagMod_mean_noise, flagMod_rms_noise = ValidationModule_ped(dfPandas_dict, ref_mean_ped, ref_rms_ped, ref_mean_noise, ref_rms_noise)
	
	print(40*"-")
	print("<ADC_ped> outside the acceptance region")
	print(flagMod_mean_ped)
	print("\n")
	print("#sigma_ADC_ped outside the acceptance region")
	print(flagMod_rms_ped)
	print("\n")
	print("<Noise> outside the acceptance region")
	print(flagMod_mean_noise)
	print("\n")
	print("#sigma_Noise outside the acceptance region")
	print(flagMod_rms_noise)
	print(40*"-")
	
	union_set = set(flagMod_mean_ped) | set(flagMod_rms_ped) |set(flagMod_mean_noise) | set(flagMod_rms_noise)
	
	#New list of flagged modules
	Modlist_flag = list(union_set)
	print("Complete set of flagged modules:")
	print(Modlist_flag)
	
	flagged_channels_pull = ValidationChannels_ped(dfPandas_dict, ref_mean_ped, ref_mean_noise,Modlist_flag)
	
	print("Flagged Channels")
	print(flagged_channels_pull)
	
    
if __name__ == "__main__":
	main()
