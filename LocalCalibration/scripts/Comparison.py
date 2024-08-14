import ROOT
import numpy as np
import os

def TreesComparison(m1,m2):
		input_file = ROOT.TFile("ModulesData.root", "READ")
		tree1 = input_file.Get(f"Module_{m1}_TTree")
		tree2 = input_file.Get(f"Module_{m2}_TTree")
		if not os.path.exists("Comparison_root"):
			os.makedirs("Comparison_root")
		file = ROOT.TFile(f"Comparison_root/Comp_{m1}vs{m2}.root", "RECREATE")
		
		branch1 = tree1.GetBranch("Channel")
		branch2 = tree1.GetBranch("ADC_ped")
		branch3 = tree1.GetBranch("CM_ped")
		branch4 = tree1.GetBranch("CM_slope")
		branch5 = tree1.GetBranch("Noise")
		branch6 = tree2.GetBranch("Channel")
		branch7 = tree2.GetBranch("ADC_ped")
		branch8 = tree2.GetBranch("CM_ped")
		branch9 = tree2.GetBranch("CM_slope")
		branch10 = tree2.GetBranch("Noise")
		
		leaf1 = branch1.GetLeaf(branch1.GetName())
		leaf2 = branch2.GetLeaf(branch2.GetName())
		leaf3 = branch3.GetLeaf(branch3.GetName())
		leaf4 = branch4.GetLeaf(branch4.GetName())
		leaf5 = branch5.GetLeaf(branch5.GetName())
		leaf6 = branch6.GetLeaf(branch6.GetName())
		leaf7 = branch7.GetLeaf(branch7.GetName())
		leaf8 = branch8.GetLeaf(branch8.GetName())
		leaf9 = branch9.GetLeaf(branch9.GetName())
		leaf10 = branch10.GetLeaf(branch10.GetName())
		
		v1 = np.zeros(1, dtype=np.int64)
		v2 = np.zeros(1, dtype=np.float64)
		v3 = np.zeros(1, dtype=np.float64)
		v4 = np.zeros(1, dtype=np.float64)
		v5 = np.zeros(1, dtype=np.float64)
		
		u1 = np.zeros(1, dtype=np.int64)
		u2 = np.zeros(1, dtype=np.float64)
		u3 = np.zeros(1, dtype=np.float64)
		u4 = np.zeros(1, dtype=np.float64)
		u5 = np.zeros(1, dtype=np.float64)
		
		tree = ROOT.TTree(f"Comp_{m1}vs{m2}", f"Comp_{m1}vs{m2}_TTree")
		tree.Branch("Channel_1", v1, "Channel_1/I")
		tree.Branch("ADC_ped_1", v2, "ADC_ped_1/D")
		tree.Branch("CM_ped_1", v3, "CM_ped_1/D")
		tree.Branch("CM_slope_1", v4, "CM_slope_1/D")
		tree.Branch("Noise_1", v5, "Noise_1/D")
		tree.Branch("Channel_2", u1, "Channel_2/I")
		tree.Branch("ADC_ped_2", u2, "ADC_ped_2/D")
		tree.Branch("CM_ped_2", u3, "CM_ped_2/D")
		tree.Branch("CM_slope_2", u4, "CM_slope_2/D")
		tree.Branch("Noise_2", u5, "Noise_2/D")
		
		for i in range(tree1.GetEntries()):
			tree1.GetEntry(i)
			tree2.GetEntry(i)
			v1[0] = leaf1.GetValue()
			v2[0] = leaf2.GetValue()
			v3[0] = leaf3.GetValue()
			v4[0] = leaf4.GetValue()
			v5[0] = leaf5.GetValue()
			u1[0] = leaf6.GetValue()
			u2[0] = leaf7.GetValue()
			u3[0] = leaf8.GetValue()
			u4[0] = leaf9.GetValue()
			u5[0] = leaf10.GetValue()
			tree.Fill()
		tree.Write()
		file.Close()
		
def main():
		moduli = [0, 1, 2, 3, 4, 5]
		for i in range(len(moduli)):
			for j in range(i+1, len(moduli)):
				TreesComparison(i,j)
		
if __name__ == "__main__":
		main()

