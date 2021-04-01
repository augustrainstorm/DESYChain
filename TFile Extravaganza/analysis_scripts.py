from ROOT import TFile, TProfile, TCanvas, TH1D, TH2D
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import typing
import os
import sys
import math

def is_bad_event() -> bool :
    

def graph_calo_values(---something---):
    #graph calo
    #fit normal dist
    #get rid of outliers
    #graph again
    #return mean
    
    
    
def grap_scint_values() -> float:
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
    
    
def analyze_file(tfile_name: str, scint_type: str):