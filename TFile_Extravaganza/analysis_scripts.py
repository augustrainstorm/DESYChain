from ROOT import TFile, TProfile, TCanvas, TH1D, TH2D, TF1
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import typing
import os
import sys
import math


def is_bad_event() -> bool :
    pass

def graph_calo_values():
    #graph calo
    #fit normal dist
    #get rid of outliers
    #graph again
    #return mean
    pass
    
    

    
#stored k values for each scintialltor:
kDict = {"1cm1580": 4.16278486487498, 
         "1cm1580": 389.9474818847028, 
         "0.5cm1630":2.7975514800695227,
         "2cm1450": 6.407665156833858,
         "0.2cm1800": 2.0945646444857497,
         "0.2cm1530": 4.6891965871302705,
         "cr1800": 83.73620099139626}
#run on one run at a time
#Tfile open with the correct file path, Tfile = runName
def graph_scint_values(runNumber) -> float:
   # iterate
    """
    for event in TTree:
        if not(is_bad_event(event)):
            THist.Fill(event * k_value) (or whatever normalized values is)
    THist.fit(normal)
    Take ±5 sigma
    Graph again with cutoffs
    return THist.mean()
      
    """
    #if is_bad_event == False:
    fitti = TF1('fitti', 'landau')
    
    #get a TTree from the run that we are passing in
    runName = f"/nfs/dust/fhlabs/group/BL4S/data/DESYChain/ConvertedData/{runNumber}.root"
    importFile = TFile(runName, "READ")
    #RECOdata = importFile.Get("RECOdata")
    RAWdata = importFile.Get("RAWdata")
    #maybe this code: TTree = TFile.Get("RECOData")
    
    #draw the hist of the run with landau dist
    #do we want this to graph onto one canvas? make a new canvas?
    #for now I just did one canvas bc we're passing in one run at a time
    
    c = TCanvas('c', 'c', 800, 1200)
    c.Divide(1,2)
    c.cd(1) # what does this code do?
    hist1 = TH1D("hist1", "RAW Scintillator Data", 100, 200, 3800)
    
    #graph without cutoffs
    # RECOdata.Draw("QDC0_ch0>>name", "QDC0_ch0<3800 && QDC0_ch0>200")
    RAWdata.Draw("QDC0_ch0>>hist1", "QDC0_ch0<3800 && QDC0_ch0>200")
    hist1.Fit(fitti)
    c.Draw()
    
    #return the fitti mean (we can change this for the histogram mean)
    fittiMean = fitti.GetParameter("MPV")
    stdDev = hist1.GetStdDev()
    lowerBound = fittiMean - 3 * stdDev
    upperBound = fittiMean + 3 * stdDev
    #scaleMean = kDict[wowmagicindex]*fittiMean
    scaleMean = 4.16278486487498*fittiMean
    #todo: make each run correspond to some voltage and thickness
    
    
    #slice the sigma
    #graph again
    c.cd(2)
    histNorm = TH1D("histNorm", "Scintillator Without Outliers", 100, lowerBound, upperBound)
    # RECOdata.Draw("QDC0_ch0>>name", "QDC0_ch0<upperBound && QDC0_ch0>lowerBound")
    cutoffs = f"QDC0_ch0<{upperBound} && QDC0_ch0>{lowerBound}"
    print(cutoffs)
    RAWdata.Draw("QDC0_ch0>>histNorm", cutoffs)
    # RAWdata.Draw("QDC0_ch0>>name", "QDC0_ch0<3800 && QDC0_ch0>200")
    histNorm.Draw()
    c.Draw()


def analyze_file(tfile_name: str, scint_type: str):
    pass