import ROOT
import os

def Mean_rms_ped():

	directory_path = "./Comparison_histo"
	
	mean_list = []
	rms_list = []
	
	for filename in os.listdir(directory_path):
		file = ROOT.TFile.Open(f"{directory_path}/{filename}")
		keys = file.GetListOfKeys()
		obj = keys[0].ReadObj()
		mean_list.append(obj.GetMean())
		rms_list.append(obj.GetRMS())
		file.Close()
	
	return mean_list, rms_list
	



def flag_comparison(mean_list, rms_list):

	rms_min_index = rms_list.index(min(rms_list))
	#alpha and beta are calibration constants
	alpha = 1.5 # This comes from the observation of the plots, a module that returns this constant should be implemented
	beta = 10 #same for beta
	cont_flag = [] #vector in which are stored the indexes of flagged comparison
	
	for rms in rms_list:
		if rms < beta:
			cont_flag.append(rms_list.index(rms))
	mean_ped = 0 #voglio calcolare la media delle medie dei delta piedistalli per i confronti "buoni" (sto scartando tutti quei confronti in cui ci potrebbe essere un un modulo da flaggare)
	
	for i in range(len(rms_list)):
		if (rms_list[i] > rms_list[rms_min_index]*alpha):
			cont_flag.append(i)
		else:
			mean_ped += mean_list[i]
	if len(cont_flag) != 15:
		return cont_flag, mean_ped/(15-len(cont_flag))
	else:
		print("All the Comparisons are flagged")
		return 1 ,1
		
def main():
	mean_list, rms_list = Mean_rms_ped()
	flag_array, mean_ped = flag_comparison(mean_list,rms_list)
	print(flag_array, mean_ped)
	
	
if __name__ == "__main__":
	main()
