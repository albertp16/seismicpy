# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 20:16:47 2021

@author: Albert Pamonag
ASEP sensitivity Analysis
"""

# import matplotlib
import matplotlib.pyplot as plt
# from fpdf import FPDF

import NSCP_2015 as NSCP
import ASCE705 as ASCE


note1 = 'NSCP Committee - Chapter 3'
note2 = 'Seismic Sensivity Analysis Report - DRAFT'

# class PDF(FPDF):
#     def header(self):
#         #logo
#         self.image('ASEP logo.png',165,10,25)
#         self.set_font('times','',12)
#         self.cell(0,5,note1 ,border=False,ln=True,align='L')
#         self.set_font('times','B',12)
#         self.cell(0,5,note2,border=False,ln=True,align='L')
#         self.ln(10)
#     def footer(self):
#         self.set_y(-20)
#         self.set_font('times','',8)
#         self.cell(0,10,note2 + f' Page {self.page_no()}/{{nb}}', align='C')
#         self.set_font('times','',8)

#     pass


# pdf = PDF('P','mm','A4')
# pdf.add_page() 
# pdf.set_font('times', '',  12)





def generate(location,ss,s1,soil_profile,distance):
    soil_arr = ['s_a','s_b','s_c','s_d','s_e']
    # pdf.set_font('times','B',20) 
    # pdf.cell(30,5,location, ln=True)
    # pdf.set_font('times','',12)
    # pdf.ln(2)
    # pdf.cell(30,5, 'ASCE 7-05 Parameters', ln=True)
    # pdf.ln(2)
    # pdf.cell(30,5, 'Ss : ' + str(ss), ln=True)
    # pdf.cell(30,5, 'S1 : ' + str(s1), ln=True)
    # pdf.ln(2)
    # pdf.cell(30,5, 'NSCP 2015 Parameters', ln=True)
    # pdf.ln(2)
    # pdf.cell(30,5, 'Fault distance : ' + str(distance) + ' KM', ln=True)
    # pdf.ln(2)
    # pdf.set_font('times','B',12)
    # pdf.cell(30,5, 'Elastic Curve', ln=True)   
    # pdf.set_font('times','',12)
    fig, ax = plt.subplots(2,3,figsize=(13,13))
    fig2, bx = plt.subplots(2,3,figsize=(13,13))
    NSCP_sa_max_list = ["NSCP"]
    ASCE_sa_max_list = ["ASCE"]
    Diff = ["Diff (%)"]
    
    for i in soil_arr:

        if(i == 's_a'):
            sp_report = "Sa"
        elif (i == 's_b'):
             sp_report = "Sb"   
        elif (i == 's_c'):
            sp_report = "Sc"
        elif (i == 's_d'):
            sp_report = "Sd"
        elif (i == 's_e'):
             sp_report = "Se" 
             
        nscp_index = NSCP.siteCoef(distance,"A",i,"4")         
        asce_index = ASCE.sitecoefficients(i,ss,s1)
        soil_param = {
            "Na" : nscp_index.Na(),
            "Nv" : nscp_index.Nv(),
            "Ca" : nscp_index.Ca(),
            "Cv" : nscp_index.Cv()    
        }
        print("Na" + str(soil_param["Na"]))
        print("Nv" + str(soil_param["Nv"]))
        fa_index = asce_index["fa"]
        fv_index = asce_index["fv"]
        
        NSCP_functions = NSCP.GMCURVE(soil_param,False)
        ASCE_functions = ASCE.responseSpecturmCurve(ss,s1,fa_index,fv_index,8,True)
        nscp_x = NSCP_functions["elastic"]["x"]
        nscp_y = NSCP_functions["elastic"]["y"]
        in_nscp_x = NSCP_functions["inelastic"]["x"]
        in_nscp_y = NSCP_functions["inelastic"]["y"]        
        
        asce_x = ASCE_functions["elastic"]["x"] 
        asce_y  = ASCE_functions["elastic"]["y"]        
        in_asce_y  = ASCE_functions["elastic"]["scaled"]
        
        sds_index = ASCE_functions["value"]["Sds"] 
        nscp_index = NSCP_functions["max_sa"]   
        
        if(i == 's_a'):
            plot_x = 0
            plot_y = 0
        elif(i == 's_b'):
            plot_x = 0
            plot_y = 1
        elif(i == 's_c'):        
            plot_x = 0
            plot_y = 2
        elif(i == 's_d'):   
            plot_x = 1
            plot_y = 0
        elif(i == 's_e'):        
            plot_x = 1
            plot_y = 1  
            
        ax[plot_x,plot_y].set(xlabel='Period (T)', ylabel='Spectral Acceleration',
                title='DESIGN RESPONSE SPECTRA (' + sp_report + ')')
        ax[plot_x,plot_y].grid('on')
        line1, = ax[plot_x,plot_y].plot(nscp_x, nscp_y, label='NSCP 2015', color='blue')
        line2, = ax[plot_x,plot_y].plot(asce_x, asce_y, label='ASCE 7-05', color='red')        
        ax[plot_x,plot_y].legend()
        
        #inelastic
        bx[plot_x,plot_y].set(xlabel='Period (T)', ylabel='Spectral Acceleration',
                title='DESIGN RESPONSE SPECTRA (' + sp_report + ')')
        bx[plot_x,plot_y].grid('on')
        line1, = bx[plot_x,plot_y].plot(in_nscp_x, in_nscp_y, label='NSCP 2015', color='blue')
        line2, = bx[plot_x,plot_y].plot(asce_x, in_asce_y, label='ASCE 7-05', color='red')        
        bx[plot_x,plot_y].legend()

        
        diff = ((max(sds_index,nscp_index) - min(sds_index,nscp_index))/max(sds_index,nscp_index))*100
        
        NSCP_sa_max_list.append(round(nscp_index,3))
        ASCE_sa_max_list.append(round(sds_index,3))   
        Diff.append(round(diff,3))  
        
    #--end of loop
    
    plt.show()      
    fig.savefig('maps/'+location+'.png',dpi=150) 
    pdf.image('maps/'+location+'.png',h=175)
    pdf.add_page() 
 
    # fig2.savefig('maps/inelastic '+location+'.png',dpi=150) 
    # pdf.image('maps/inelastic '+location+'.png',h=175)
    # pdf.add_page() 
 
    plt.show()
    fig = plt.figure(dpi=150)
    ax = fig.add_subplot(1,1,1)
    table_data=[
        ["Soil Profile", "Sa", "Sb", "Sc", "Sd", "Se"
        ],
        NSCP_sa_max_list,
        ASCE_sa_max_list,
        Diff
    ]
    pdf.set_font('times','B',12)
    pdf.cell(30,5, 'Comparision of max Sa NSCP vs. ASCE 7-05 : ', ln=True)
    pdf.set_font('times','',12)
    pdf.ln(2)
    table = ax.table(cellText=table_data, loc='center')
    table.set_fontsize(30)
    table.scale(1,4)
    ax.axis('off')
    plt.show()   
    fig.savefig('maps/table '+location+'.png') 
    pdf.image('maps/table '+location+'.png',h=100)
    pdf.add_page() 
    
