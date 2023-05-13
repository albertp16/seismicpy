# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 10:34:57 2023

@author: alber
"""

import math
import pandas as pd
import numpy as np
import matplotlib as mpl

zone = .4
source = "B"
distance = 10 
soil_type = "sc"
occupancy = "IV"
column_area = 0.4*0.4 
shear_wall_area_1= 0.2*(3 + 2.1 +3) 
shear_wall_area_9= 0.2*4 
shear_wall_area_10= 0.2*6
Ec = 2.2e6 
fc = 28 #MPa
h = 3 #meters
poission = 0.10

##function 
def areaRectangle(x,y):
    return x*y 

def internia(b,h):
    return (b*math.pow(h,3))/12

def interniaBase(b,h):
    return (b*math.pow(h,3))/3

def computeRectanglesCentroid(rectangles):
    numRectangles = len(rectangles)
    total_area = 0
    totalX = 0
    totalY = 0
  
    ##Compute the sum of all the x and y coordinates of the rectangle centroids
    i = 0
    while i < numRectangles:
        rectangle = rectangles[i]
        area_index = rectangle['width'] * rectangle['height']
        total_area += area_index
        area_index_x = area_index*rectangle['x'];
        area_index_y = area_index*rectangle['y'];
        
        totalX += area_index_x;
        totalY += area_index_y;
        i += 1
    
    ##Divide by the number of rectangles to get the average centroid
    centroidX = totalX / total_area;
    centroidY = totalY / total_area;
    
    ##Ix and Iy 
    ix_total = 0
    iy_total = 0
    
    i = 0
    while i < numRectangles:
        rectangle = rectangles[i]
        area_index = rectangle['width'] * rectangle['height']
        inertia_x_index = internia(rectangle['width'],rectangle['height'])
        transfer_x_index = area_index*math.pow(rectangle['y'] - centroidY,2)

        inertia_y_index = internia(rectangle['height'],rectangle['width'])
        transfer_y_index = area_index*math.pow(rectangle['x'] - centroidX,2)
        
        ix_total += inertia_x_index + transfer_x_index
        iy_total += inertia_y_index + transfer_y_index;
        i += 1    
  
    return { 'x': centroidX, 'y': centroidY, 'area' : total_area, 'ix' : ix_total, 'iy' : iy_total};

def deformationF(P,h,E,I,TYPE):
    if TYPE == "BE": ##Both Ends
        output = (P*math.pow(h,3))/(12*E*I)
    elif TYPE == "OE":
        output = (P*math.pow(h,3))/(3*E*I)        
    return output

def deformationV(P,h,G,A):
    output = (1.2*P*h)/(G*A)
    return output

def shearModulus(E,v):
    G = E/(2*(1+v))
    return G

def modulusConcrete(fc):
    output = 4700*math.sqrt(fc)
    return output

Ec = modulusConcrete(fc)

shearwall1 = [
    { 'x': 0.1, 'y': 10.5, 'width': 0.2, 'height': 3 },
    { 'x': 1.25, 'y': 11.9, 'width': 2.1, 'height': 0.2 },
    { 'x': 2.4, 'y': 10.5, 'width': 0.2, 'height': 3 }
];

shearwall9 = [
    { 'x': 7, 'y': 0.1, 'width': 4, 'height': 0.2 },
];
shearwall10 = [
    { 'x': 13.9, 'y': 3, 'width': 0.2, 'height': 6 },
];
# computeRectanglesCentroid(shearwall1)

def createShearWall(id,data):
    importdatas = computeRectanglesCentroid(data)
    area = round(importdatas['area'],5)
    ix = round(importdatas['ix'],5)
    iy = round(importdatas['iy'],5)
    return [id,"Wall",importdatas['x'],importdatas['y'],area,ix,iy]

def createElementColumn(id,x,y,b,h):
    area = round(areaRectangle(b,h),5)
    ix = round(internia(b,h),5)
    iy = round(internia(b,h),5)
    return [id,"Column",x,y,area,ix,iy]

# print(internia(0.4,0.4))
element_one = createShearWall(1,shearwall1)
element_two = createElementColumn(2,5,12-0.2,0.4,0.4)
element_three = createElementColumn(3,9,12-0.2,0.4,0.4)
element_four = createElementColumn(4,14-0.2,12-0.2,0.4,0.4)
element_five = createElementColumn(5,0.2,6,0.4,0.4)
element_six = createElementColumn(6,5,6,0.4,0.4)
element_seven = createElementColumn(7,9,6,0.4,0.4)
element_eight = createElementColumn(8,0.2,0.4,0.4,0.4)
element_nine = createShearWall(9,shearwall9)
element_ten = createShearWall(10,shearwall10)

# f
building_elements = [
    element_one,
    element_two,
    element_three,
    element_four,
    element_five,
    element_six,
    element_seven,
    element_eight,
    element_nine,
    element_ten,
]
# building_elements
n_elements = len(building_elements)
bldg_df = pd.DataFrame(building_elements,columns=["Element ID","Type", "Xbrp (m)","Ybrp (m)","Area (sq.m)","Ix (m^4)","Iy (m^4)"])

shear_modulus = shearModulus(Ec,poission) ##MPa to KPa

data_two = []
total_kxy = 0
total_kx = 0
kx_arr = []
i = 0
while i < n_elements:
    element_type = building_elements[i][1]
    
    if element_type == "Wall":
        delta_f = deformationF(1000,3,Ec,building_elements[i][6],"OE")
    elif element_type == "Column": 
        delta_f = deformationF(1000,3,Ec,building_elements[i][6],"BE")
        
    delta_v = deformationV(1000,3,shear_modulus,building_elements[i][4])
    
    total_delta = delta_f + delta_v
    
    kx = (1/total_delta)*1000
    kx_arr.append(kx)
    kxy = kx*building_elements[i][3]
    total_kxy += kxy
    total_kx += kx    
    data_two.append([delta_f,delta_v,total_delta,kx,kxy])
    i += 1

yr =  total_kxy/total_kx
print('kxy = ' + str(total_kxy)) 
print('kx = ' + str(total_kx)) 
print('Center of rigity, YR = ' + str(yr) + " m")    

xr_df = pd.DataFrame(data_two
                 ,columns=["delta_F (mm)","delta_V (mm)", "total delta","kx","kxy"])
# df
