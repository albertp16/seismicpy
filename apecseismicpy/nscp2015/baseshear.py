# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 08:27:02 2023

@author: albert pamonag 
"""
import math

class calculate_base_shear:
    def __init__(self,zone,nv,ca,cv,importance_factor,response_modification,period,weight):
        self.zone = zone
        self.nv = nv
        self.ca = ca
        self.cv = cv
        self.importance_factor = importance_factor
        self.response_modification = response_modification
        self.period = period
        self.weight = weight
    def totalBaseShear(self):
        # Equation 208-08
        return ((self.cv*self.importance_factor)/(self.response_modification*self.period))*self.weight
    def maxBaseShear(self):
        # Equation 208-09
        CONSTANT = 2.5
        return ((CONSTANT*self.ca*self.importance_factor)/(self.response_modification))*self.weight
    def minBaseShear(self):
        # Equation 208-10
        CONSTANT = 0.11
        return CONSTANT*self.ca*self.importance_factor*self.weight
    def maxBaseShearZ4(self):
        # Equation 208-11
        CONSTANT = 0.8
        return ((CONSTANT*self.nv*self.importance_factor*0.4)/(self.response_modification))*self.weight
    def governingShear(self):
        
        if(self.zone == 4):
            # TODO to complete this conditions 
            govern_shear_max = min(self.totalBaseShear(),self.maxBaseShear())
            govern_shear_min = max(self.totalBaseShear(),self.minBaseShear())
            govern_shear = min(govern_shear_max,self.maxBaseShearZ4())
        
        return govern_shear
    
    
data_one = calculate_base_shear(4,1.29,0.42,0.72,1,8.0,0.62,21000)
print(data_one.totalBaseShear())
print(data_one.maxBaseShear())
print(data_one.minBaseShear())
print(data_one.maxBaseShearZ4())
print(data_one.governingShear())