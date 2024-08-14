import sys
import pandas as pd
import ROOT
import argparse

def fillHexPlot(num_module, ch_values, moduletype='LD_full'):

    """
    this method takes care of instatiating a hexplot for a given module type and fill it with the values for the required channels
    ch_values is a dict of (channel number, value)
    module_type is a string with the module type to be used in the hexplot
    """
    
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
        
    fgeo.Close()

    return hex_plot


def count_ttrees(root_file_path):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(root_file_path)
    if not root_file or root_file.IsZombie():
        print("Error opening file")
        return 0
    
    # Get list of keys in the file
    keys = root_file.GetListOfKeys()
    
    # Count the number of TTree objects
    ttree_count = 0
    for key in keys:
        obj = key.ReadObj()
        if isinstance(obj, ROOT.TTree):
            ttree_count += 1
    
    # Close the ROOT file
    root_file.Close()
    
    return ttree_count


root_file_path = '/afs/cern.ch/user/a/alderobe/HGCalCommissioning/LocalCalibration/scripts/ModulesData.root'  # Replace with your ROOT file path


def main():

    #parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--moduletype",
                        help='module type=%(default)s',
                        default="LD_full")
    parser.add_argument("-i", "--input",
                        help='input CSV file with channel and data columns=%(default)s',
                        default="csv_files/input_hexaplot")   #in questo modo non permetto di utilizzare -i 
    parser.add_argument("-o", "--output",
                        help='output file with hexplotsdefault=%(default)s',
                        default='./Hexplots/hexplots')
    args = parser.parse_args()
    
    
    Num_modules = count_ttrees(root_file_path)
    
    for i in range(Num_modules):
	    #fill a dataframe from a csv file
	    fOut=ROOT.TFile.Open(f"{args.output}_{i}.root",'RECREATE')
	    df=pd.read_csv(f"{args.input}_{i}.csv",sep='\s+',header='infer')
	    df=df.set_index('channel')

	    #fill plots for every column in the dataframe and save to ROOT file
	    for c in df.columns:
	        if c.lower()=='channel' : continue
	        ch_values=df[c].to_dict()
	        h=fillHexPlot(i, ch_values=ch_values, moduletype=args.moduletype)
	        fOut.cd()
	        h.SetName(c)
	        h.SetDirectory(fOut)
	        h.Write()
	        h.GetZaxis().SetRangeUser(0, 300)
	        c1 = ROOT.TCanvas()
	        h.SetStats(0)
	        #h.GetXaxis.SetTitle("[cm]")
	        #h.GetYaxis.SetTitle("[cm]")
	        h.Draw("colz")
	        c1.Draw()
	        c1.SaveAs(f"Hexplots/hexplot_{i}.png")
	    fOut.Close()
    

if __name__ == '__main__':    
    sys.exit(main())
