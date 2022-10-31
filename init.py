# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 20:16:47 2021

@author: Albert Pamonag
ASEP sensitivity Analysis
"""

# import matplotlib
import matplotlib.pyplot as plt

import NSCP_2015 as NSCP
import ASCE705 as ASCE


def generate(ca,cv,R):
      
    data = NSCP.rsCurve(ca,cv,R)  
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot(data['elastic']['x'], data['elastic']['y'], label = "NSCP 2015")
    
    ax.set(xlabel="Period (sec)", ylabel="Spectral Acceleration (Sa)",
            title= "Design Response Spectra")
    ax.grid()
    plt.xscale('line')
    plt.legend()
    plt.show()
    
test = NSCP.siteCoef(2,"A","s_d","4")
ca = test.ca()
cv = test.cv()
R = 8.5
generate(ca,cv,R)