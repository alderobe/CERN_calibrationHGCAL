import ROOT
import os
import numpy as np
import matplotlib.pyplot as plt

# This module takes the tree containing ped,noise,... of a pair of modules and defines a dataframe with new variables useful to test the goodness of the calibration. Plots of these variables are stored in /plots and root files with histograms are generated as weel in /Comparison_histo

def DataFrame(treeName, input_file):

	df = ROOT.RDataFrame(treeName, input_file)
	def1 = df.Define("Delta_ped", "(ADC_ped_1-ADC_ped_2)")
	def2 = def1.Define("Delta_CM", "(CM_ped_1-CM_ped_2)")
	def3 = def2.Define("Delta_slope", "(CM_slope_1-CM_slope_2)")
	def4 = def3.Define("Delta_noise", "(Noise_1-Noise_2)")
	def5 = def4.Define("Pull", "(ADC_ped_1-ADC_ped_2)/Noise_1")

	display = def5.Display(["Delta_ped", "Delta_CM", "Delta_slope", "Delta_noise", "Pull"], 10)
	display.Print()
	#ovviamente si potrebbe creare una lista di histo e canvas così da generalizzare la lista delle variabili da indagare
	# nella cartella plot definisco ulteriori cartelle ognuna riferita ad una specifica variabile, dove verranno salvati i plot
	if not os.path.exists(f"plots/Delta_ped"):
		os.makedirs(f"plots/Delta_ped")
	if not os.path.exists(f"plots/Delta_CM"):
		os.makedirs(f"plots/Delta_CM")
	if not os.path.exists(f"plots/Delta_slope"):
		os.makedirs(f"plots/Delta_slope")
	if not os.path.exists(f"plots/Delta_noise"):
		os.makedirs(f"plots/Delta_noise")
	if not os.path.exists(f"plots/Pull"):
		os.makedirs(f"plots/Pull")
	c1 = ROOT.TCanvas()
	h1 = def5.Histo1D("Delta_ped")
	h1.Draw()
	c1.Draw()
	c1.SaveAs(f"plots/Delta_ped/{treeName}.png")
	
	c2 = ROOT.TCanvas()
	h2 = def5.Histo1D("Delta_CM")
	h2.Draw()
	c2.Draw()
	c2.SaveAs(f"plots//Delta_CM/{treeName}.png")

	c3 = ROOT.TCanvas()
	h3 = def5.Histo1D("Delta_slope")
	h3.Draw()
	c3.Draw()
	c3.SaveAs(f"plots/Delta_slope/{treeName}.png")

	c4 = ROOT.TCanvas()
	h4 = def5.Histo1D("Delta_noise")
	h4.Draw()
	c4.Draw()
	c4.SaveAs(f"plots/Delta_noise/{treeName}.png")

	c5 = ROOT.TCanvas()
	h5 = def5.Histo1D("Pull")
	h5.Draw()
	c5.Draw()
	c5.SaveAs(f"plots/Pull/{treeName}.png")
	
	if not os.path.exists("Comparison_histo"):
		os.makedirs("Comparison_histo")
	outFile = ROOT.TFile(f"Comparison_histo/{treeName}_histo.root", "RECREATE")
	h1.Write()
	h2.Write()
	h3.Write()
	h4.Write()
	h5.Write()
	outFile.Close()
	return def5

# 	
def create_histogram(data, title, xlabel, ylabel, filename):
    plt.figure()
    plt.hist(data, bins="auto", alpha=0.75)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(filename)
    plt.close()
       
        
#   
def Analysis(df):
	h1 = df.Histo1D("Delta_ped")
	h2 = df.Histo1D("Delta_CM")
	h3 = df.Histo1D("Delta_slope")
	h4 = df.Histo1D("Delta_noise")
	h5 = df.Histo1D("Pull")
	
	max_value = []
	mean_value = []
	rms_value = []
	
	max_value.append(h1.GetMaximum())
	mean_value.append(h1.GetMean())
	rms_value.append(h1.GetRMS())
	"""
	print(10*"-"+"Delta_ped"+"-"*10)
	print(f"The maximum bin content in the histogram is: {max_value[0]}")
	print(f"The mean value of the histogram is: {mean_value[0]}")
	print(25*"-") """
	
	max_value.append(h2.GetMaximum())
	mean_value.append(h2.GetMean())
	rms_value.append(h2.GetRMS())
	"""
	print(10*"-"+"Delta_CM"+"-"*10)
	print(f"The maximum bin content in the histogram is: {max_value[1]}")
	print(f"The mean value of the histogram is: {mean_value[1]}")
	print(25*"-") """
	
	max_value.append(h3.GetMaximum())
	mean_value.append(h3.GetMean())
	rms_value.append(h3.GetRMS())
	"""
	print(10*"-"+"Delta_slope"+"-"*10)
	print(f"The maximum bin content in the histogram is: {max_value[2]}")
	print(f"The mean value of the histogram is: {mean_value[2]}")
	print(25*"-") """
	
	max_value.append(h4.GetMaximum())
	mean_value.append(h4.GetMean())
	rms_value.append(h4.GetRMS())
	"""
	print(10*"-"+"Delta_Noise"+"-"*10)
	print(f"The maximum bin content in the histogram is: {max_value[3]}")
	print(f"The mean value of the histogram is: {mean_value[3]}")
	print(25*"-") """
	
	max_value.append(h5.GetMaximum())
	mean_value.append(h5.GetMean())
	rms_value.append(h5.GetRMS())
	"""
	print(10*"-"+"Pull"+"-"*10)
	print(f"The maximum bin content in the histogram is: {max_value[4]}")
	print(f"The mean value of the histogram is: {mean_value[4]}")
	print(25*"-") """
	
	return max_value, mean_value, rms_value
        
def main():
	directory_path = './Comparison_root'
	
	#dictionary cointained for each key variables, the list of values due to the 15 comparisons.
	histograms = {
        "max_Delta_ped": [],
        "max_Delta_CM": [],         #max of histos
        "max_Delta_slope": [],
        "max_Delta_noise": [],
        "max_pull": [],
        "mean_Delta_ped": [],
        "mean_Delta_CM": [],        #mean of histos
        "mean_Delta_slope": [],
        "mean_Delta_noise": [],
        "mean_pull": [],
        "err_Delta_ped": [],
        "err_Delta_CM": [],
        "err_Delta_slope": [],       #RMS of histos
        "err_Delta_noise": [],
        "err_pull": []}
		
	mean_modules_ped = 0 #media delle medie dei piedistalli
	rms_modules_ped = 0
	max_modules_ped = 0
		
	for filename in os.listdir(directory_path):
		file = ROOT.TFile.Open(f"{directory_path}/{filename}")
		keys = file.GetListOfKeys()
		obj = keys[0].ReadObj()
		treeName = obj.GetName()
		file.Close()
		df = DataFrame(treeName, f"{directory_path}/{filename}")
		max_list, mean_list, rms_list = Analysis(df)
		
		histograms["max_Delta_ped"].append(max_list[0])
		histograms["max_Delta_CM"].append(max_list[1])
		histograms["max_Delta_slope"].append(max_list[2])
		histograms["max_Delta_noise"].append(max_list[3])
		histograms["max_pull"].append(max_list[4])

		histograms["mean_Delta_ped"].append(mean_list[0])
		histograms["mean_Delta_CM"].append(mean_list[1])
		histograms["mean_Delta_slope"].append(mean_list[2])
		histograms["mean_Delta_noise"].append(mean_list[3])
		histograms["mean_pull"].append(mean_list[4])
		
		histograms["err_Delta_ped"].append(rms_list[0])
		histograms["err_Delta_CM"].append(rms_list[1])
		histograms["err_Delta_slope"].append(rms_list[2])
		histograms["err_Delta_noise"].append(rms_list[3])
		histograms["err_pull"].append(rms_list[4])
		
		mean_modules_ped += mean_list[0]
		rms_modules_ped += rms_list[0]
		max_modules_ped += max_list[0]
		
	print(f"Il valore medio di piedistallo tra i 6 moduli è : {mean_modules_ped/6}")
	print(f"L'RMS medio relativo ai piedistalli, tra i 6 moduli è: {rms_modules_ped/6} ")
	print(f"Il massimo  valore di piedistallo medio, tra i 6 moduli è: {max_modules_ped/6} ")
		
	if not os.path.exists("./flag_variables"):
		os.makedirs("./flag_variables")
		
	"""
	output_file = ROOT.TFile("flag_variables/flag_variables.root", "RECREATE")
	
	h_max_ped = ROOT.TH1F("max_Delta_ped", "max_Delta_ped", 10, np.array(histograms["max_Delta_ped"]))
	h_max_CM = ROOT.TH1F("max_Delta_CM", "max_Delta_CM", 10, np.array(histograms["max_Delta_CM"]))
	h_max_slope = ROOT.TH1F("max_Delta_slope", "max_Delta_slope", 10, np.array(histograms["max_Delta_slope"]))
	h_max_noise = ROOT.TH1F("max_Delta_noise", "max_Delta_noise", 10, np.array(histograms["max_Delta_noise"]))
	h_max_pull = ROOT.TH1F("max_pull", "max_pull", 10, np.array(histograms["max_pull"]))
	h_mean_ped = ROOT.TH1F("mean_Delta_ped", "mean_Delta_ped", 10, np.array(histograms["mean_Delta_ped"]))
	h_mean_CM = ROOT.TH1F("mean_Delta_CM", "mean_Delta_CM", 10, np.array(histograms["mean_Delta_CM"]))
	h_mean_slope = ROOT.TH1F("mean_Delta_slope", "mean_Delta_slope", 10, np.array(histograms["mean_Delta_slope"]))
	h_mean_noise = ROOT.TH1F("mean_Delta_noise", "mean_Delta_noise", 10, np.array(histograms["mean_Delta_noise"]))
	h_mean_pull = ROOT.TH1F("mean_pull", "mean_pull", 10, np.array(histograms["mean_pull"]))
	h_err_ped = ROOT.TH1F("err_Delta_ped", "err_Delta_ped", 10, np.array(histograms["err_Delta_ped"]))
	h_err_CM = ROOT.TH1F("err_Delta_CM", "err_Delta_CM", 10, np.array(histograms["err_Delta_CM"]))
	h_err_slope = ROOT.TH1F("err_Delta_slope", "err_Delta_slope", 10, np.array(histograms["err_Delta_slope"]))
	h_err_noise = ROOT.TH1F("err_Delta_noise", "err_Delta_noise", 10, np.array(histograms["err_Delta_noise"]))
	h_err_pull = ROOT.TH1F("err_pull", "err_pull", 10, np.array(histograms["err_pull"]))
	
	output_file.Close()
	
	"""
	for key, data in histograms.items():
		
		create_histogram(data, title=key, xlabel=key, ylabel='Counts', filename=f"./flag_variables/{key}.png")
	
if __name__=="__main__":
	main()
