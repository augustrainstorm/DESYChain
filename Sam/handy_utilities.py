import ROOT #PyROOT
from matplotlib.patches import Rectangle
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import os
from array import array

comments = '''Unfortunately, ROOT doesn't support renaming branches within a TTree
One alternative is setting aliases. This can be helpful, but faces limitations. 
For example, to directly use a branch we can't say TTree.GetBranch("alias"); instead we do TTree.GetBranch(TTree.GetAlias("alias")). Also, it doesn't show in TTree.Print()
However, in most cases it is helpful, e.g. print(getattr(event, "alias")) or TTree.Draw("alias>>TH1D") works

If you really want to get a fully reformated TTree, call renameBranches_new(tree).
'''

dictVersion = '1'

branchDict = {"QDC0_ch0": "scint", "QDC0_ch1": "calo_1", "QDC0_ch2": "calo_2", "QDC0_ch3": "calo_3", "QDC0_ch4": "calo_4",
                  "QDC0_ch5": "calo_0", "TDC0_ch0": "DWC_0-L", "TDC0_ch1": "DWC_0-R", "TDC0_ch2": "DWC_0-U", 
                  "TDC0_ch3": "DWC_0-D", "TDC0_ch4": "DWC_1-L", "TDC0_ch5": "DWC_1-R", "TDC0_ch6": "DWC_1-U",
                  "TDC0_ch7": "DWC_1-D", "NTDC0_ch0": "[N]DWC_0-L", "NTDC0_ch1": "[N]DWC_0-R", "NTDC0_ch2": "[N]DWC_0-U", 
                  "NTDC0_ch3": "[N]DWC_0-D", "NTDC0_ch4": "[N]DWC_1-L", "NTDC0_ch5": "[N]DWC_1-R", "NTDC0_ch6": "[N]DWC_1-U",
                  "NTDC0_ch7": "[N]DWC_1-D", "NMMFE8_02_hitChannel": "[N]MM_1L_hitChannel", 
                  "MMFE8_02_hitChannel": "MM_1L_hitChannel", "NMMFE8_02_hitTDO": "[N]MM_1L_hitTDO", 
                  "MMFE8_02_hitTDO": "MM_1L_hitTDO", "NMMFE8_02_hitPDO": "[N]MM_1L_hitPDO", "MMFE8_02_hitPDO": "MM_1L_hitPDO",
                  "NMMFE8_03_hitChannel": "[N]MM_1R_hitChannel", "MMFE8_03_hitChannel": "MM_1R_hitChannel", 
                  "NMMFE8_03_hitTDO": "[N]MM_1R_hitTDO", "MMFE8_03_hitTDO": "MM_1R_hitTDO", 
                  "NMMFE8_03_hitPDO": "[N]MM_1R_hitPDO", "MMFE8_03_hitPDO": "MM_1R_hitPDO",
                  "NMMFE8_05_hitChannel": "[N]MM_2T_hitChannel", "MMFE8_05_hitChannel": "MM_2T_hitChannel", 
                  "NMMFE8_05_hitTDO": "[N]MM_2T_hitTDO", "MMFE8_05_hitTDO": "MM_2T_hitTDO", 
                  "NMMFE8_05_hitPDO": "[N]MM_2T_hitPDO", "MMFE8_05_hitPDO": "MM_2T_hitPDO"}


def renameBranches_alias(tree):
    for oldName in branchDict:
        tree.SetAlias(branchDict[oldName], oldName)
    return tree

'''
For branches with variable length arrays (the TDC) branches, I was having trouble copying them
Inspired by https://root.cern.ch/root/html/tutorials/tree/tree3.C.html I tried for these type branches
n = array('i', [0]*10)
tree.Branch( 'mycode', n, 'MyCode/I' )

for event in TTree:
    data = getattr(event, "TDC0_ch0")
    for index in range(len(data)):
        n[index] = data[index]
    if counter < 10:
        print(data, n)
    tree.Fill()

But this gave slightly different results (e.g. on a histogram) than the actual data indicating inappropriate copying
Suggest fixes if you want

https://root-forum.cern.ch/t/copy-tree-entry-by-entry-in-pyroot/24324/3
'''
def create_tFile(runNum = ""):
    #os.chdir(os.path.expanduser("~")) #not sure if this affects the file the module is imported in? & don't want to do that
    outDir = os.path.join(os.path.expanduser("~"), "alteredRoot")
    if not os.path.isdir(outDir):
        os.mkdir(outDir)
     
    #If we already have the file, don't go to all the work of remaking it
    haveIt = False
    if runNum:
        tfilePath = os.path.join(outDir, runNum + '_' + dictVersion + 'root')
        if os.path.isfile(tfilePath):
            tfileOut = ROOT.TFile(tfilePath, "READ")
            haveIt = True
        else:
            tfileOut = ROOT.TFile(tfilePath , 'RECREATE')
    else:
        tfilePath = os.path.join(outDir, "tempTree.root")
        try: os.remove(tfilePath)
        except FileNotFoundError: pass
        tfileOut = ROOT.TFile(tfilePath, 'RECREATE')
    return tfileOut, haveIt


def renameBranches(inTree, runNum = ""):
    tfileOut, haveIt = create_tFile(runNum = runNum) 
    if haveIt:
        return tfileOut.Get("RAWdata") 
    
    #See above: I'm having troubles copying the TDC events which are these variable length arrays/buffers
    #Instead, we just copy the whole branches
    #One worry – branches are linked from original to new TTree, so weirdness could occur?
    inTree.SetBranchStatus('*', 0)
    inTree.SetBranchStatus('TDC*', 1) #TDC and NTDC seem to be linked #doing just this would activate all
    '''for branchName in branchDict:
           if 'TDC' in branchName: #or 'MMFE8' in branchName: #Too, the MMF8 counts need the NMFE8 counts to be read properly, and I don't know how to link them if I reconstruct each branch
           inTree.SetBranchStatus(branchName, 1)'''
    retTree = inTree.CloneTree()
    
    print("success")
    
    #ISSUE: this doesn't 'link' events so the copied (above) events and singly added ones are seperated.
    #this means the MMFE8/TDC branches are doubled
    retTree = renameBranches_limited(inTree, retTree = retTree)
    
    tfileOut.write()
    return renameBranches_alias(retTree)
                       
    
def renameBranches_limited(inTree, runNum = "", retTree = None):
    standAlone = False #this way we can use this method just on its own
    if not retTree: #then we need to make a file and a tree
        standAlone = True
        tfileOut, haveIt = create_tFile(runNum = "")
        retTree = ROOT.TTree( 'RAWdata', 'RawData' )
    #outDir = os.path.join(os.path.expanduser("~"), "alteredRoot")
    #tfileOut = ROOT.TFile(os.path.join(outDir, "testtree.root"), "RECREATE")
    
    #When we make a branch, we supply title, description, and the variable the branch WILL be filled from
    #Because C++, we need this object to have a pointer :(
    #Per https://web.archive.org/web/20150126183040/http://wlav.web.cern.ch/wlav/pyroot/tpytree.html
    #we use an array object to give an appropriate pointer
    
    #Create branches with variables to fill
    inTree.SetBranchStatus('*', 1)
    branchList = [q for q in branchDict.items() if not 'TDC' in q[0] and not 'MMFE8' in q[0]] #order shouldn't change, but hey
    arrList = []
    for unused_branch, name in branchList:
        arrList.append(array('i', [0]))
        retTree.Branch(name, arrList[-1], '%s/i'%name)
    print("branches made")
    
    #go around filling them
    for event in inTree:
        for arr, branch_names in zip(arrList, branchList):
            arr = getattr(event, branch_names[0])
        retTree.Fill()
    print("branches filled")
    retTree.Print()
    if standAlone: tfileOut.Write()
    return retTree


#def detPedestal(?):


def calPlot(runNumbers): #runNumbers accepts various formats: a list or a string, single or full path names
    if not isinstance(runNumbers, list):
        runNumbers = [runNumbers]
    for run in runNumbers:
        if isinstance(run, ROOT.TTree):
            RAWdata = run
            tProf = ROOT.TProfile(str(RAWdata).split(':')[1].split(' ')[1].strip(), "title", 5, 0.5, 5.5) #naming was done so very badly
        else:
            run = str(run) #but just provide strings, please
            if not os.path.exists(run): #if it ain't here, you better provide your own path!
                run = os.path.join("/nfs/dust/fhlabs/group/BL4S/data/DESYChain/ConvertedData", os.path.basename(run) + '.root')
            importRun = ROOT.TFile(run, "READ")
            RAWdata = importRun.Get("RAWdata")
            tProf = ROOT.TProfile(os.path.basename(run), "title", 5, 0.5, 5.5)

        #Define the locations of the calorimeters and make a TProfile
        caloPlace={5:1, 1:2, 2:3, 3:4, 4:5}
        #print(RAWdata)
        for event in RAWdata:
            for i in [5, 1, 2, 3, 4]:
                value = getattr(event, "QDC0_ch"+str(i))
                if value>200: #Think about the pedestal
                    tProf.Fill(caloPlace[i], value)

        #Normalize the data to a 0-1 range
        data=[]
        for i in range(1, 6):
            data+=[math.log(tProf.GetBinContent(i))]
            print((tProf.GetBinContent(i), math.log(tProf.GetBinContent(i))))
        data=np.interp(data, (np.amin(data), np.max(data)), (0, +1))

        #Create the figure
        plt.figure()
        currentAxis = plt.gca()
        currentAxis.set(xlim=(0, 5), ylim=(0, 5))

        #Make rectangles for each calorimeter
        currentAxis.add_patch(Rectangle((0, 0), 1, 5,alpha=1, facecolor=cm.viridis(data[0]))) #facecolor=col_pal[0]))
        currentAxis.add_patch(Rectangle((1, 0), 1, 5,alpha=1, facecolor=cm.viridis(data[1]))) #facecolor=col_pal[0]))
        currentAxis.add_patch(Rectangle((2, 0), 1, 5,alpha=1, facecolor=cm.viridis(data[2]))) #facecolor=col_pal[0]))
        currentAxis.add_patch(Rectangle((3, 0), 1, 5,alpha=1, facecolor=cm.viridis(data[3]))) #facecolor=col_pal[0]))
        currentAxis.add_patch(Rectangle((4, 0), 1, 5,alpha=1, facecolor=cm.viridis(data[4]))) #facecolor=col_pal[0]))

        print()
        
        
def dfTree(inTree):
    branchOut = {branchDict[key]: [] for key in branchDict.keys()}
    for event in inTree:
        for branchName in branchDict.keys():
            branchOut[branchDict[branchName]].append(getattr(event, branchName))
    out_df = pd.DataFrame(branchOut)
    print(out_df)
    return out_df
        
        
def main():
    print("Good job!")

if __name__ == '__main__':
    main()