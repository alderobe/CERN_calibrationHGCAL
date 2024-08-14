import ROOT
import os



#This module scan the six modules ROOT file in oder to get the mean and rms values of the Pedestal histograms then return 2 lists each corrisponding to the mean and rms values.

def Mean_rms_ped(filename, TObjectName):

	input_file = ROOT.TFile(f"{filename}", "READ")
	
	mean_list = []
	rms_list = []
	for key in input_file.GetListOfKeys():
		obj = key.ReadObj()
		tree = obj
		tree.Draw(f"{TObjectName} >> htemp")
		htemp = ROOT.gDirectory.Get("htemp")
		mean_list.append(htemp.GetMean())
		rms_list.append(htemp.GetRMS())
		htemp.Delete()
		
		#verifica che sia un histo altrimenti raiseAnError
		
	input_file.Close()
	return mean_list, rms_list
	
# This module returns a list (cont_flag) of indexes of flagged module and the mean pedestal among remaining "good" modules	

def flag_modules(mean_list,rms_list):
	rms_min_index = rms_list.index(min(rms_list)) # maybe a check over this variable should be implemented. if the rms is too low the module is flagged however the selection in the if still uses this minimum.
	#alpha and beta are calibration constants
	alpha = 1.3 # This comes from the observation of the plots, a module that returns this constant should be implemented
	beta = 10 #same for beta
	cont_flag = [] #vector in which are stored the indexes of flagged modules
	
	for rms in rms_list:
		if rms < beta:
			cont_flag.append(rms_list.index(rms))
	mean_ped = 0 #voglio calcolare la media delle medie dei piedistalli per i moduli "buoni"
	for i in range(len(rms_list)):
		if (rms_list[i] > rms_list[rms_min_index]*alpha):
			cont_flag.append(i)
		else:
			mean_ped += mean_list[i]
	if len(cont_flag) != 6:
		return cont_flag, mean_ped/(6-len(cont_flag))
	else:
		print("All the modules are flagged")
		return 1 ,1
		
#This module flag the modules that give high values of rms in the ADC_ped distribution

	
def main():
	input_filename = "ModulesData.root"
	Branch_name = "ADC_ped"
	mean_list, rms_list = Mean_rms_ped(input_filename, Branch_name)
	flag_array, mean_ped = flag_modules(mean_list,rms_list)
	print(flag_array, mean_ped)
	
	
	
if __name__ == "__main__":
	main()
