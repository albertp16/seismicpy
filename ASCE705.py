
def sitecoefficients(soil_type_input,Ss_input,S1_input): 

        Ss = Ss_input;
        S_one = S1_input;

        SEIS_soil_type_value = soil_type_input;
        
        def interpolate(value,left, right):
            a = (value - left)/0.25
            b = left - right
            c = left - (a*b)
            return c
        
        def interpolateFv(value,left, right):
            a = (value - left)/0.10
            b = left - right
            c = left - (a*b)
            return c        
            
        
        if (SEIS_soil_type_value == "s_a"):
            site_class = "A"
        elif (SEIS_soil_type_value == "s_b"):
            site_class = "B"
        elif (SEIS_soil_type_value == "s_c"):
            site_class = "C"
        elif (SEIS_soil_type_value == "s_d"):
            site_class = "D"
        elif (SEIS_soil_type_value == "s_e"):
            site_class = "E"

        if (Ss <= 0.25):
            if (site_class == "A"):
                Fa = 0.8
            elif (site_class == "B"):
                Fa = 1.0
            elif (site_class == "C"):
                Fa = 1.2
            elif (site_class == "D"):
                Fa = 1.6;
            elif (site_class == "E"):
                Fa = 2.5;
        elif Ss > 0.25 and Ss <= 0.5:
            if (site_class == "A"):
                Fa = 0.8
            elif (site_class == "B"):
                Fa = 1.0
            elif (site_class == "C"):
                Fa = 1.2
            elif (site_class == "D"):
                Fa = interpolate(Ss,1.6,1.4)                
#                 Fa = (1.6 - 1.4) * (Ss / 0.25)
            elif (site_class == "E"):
                Fa = interpolate(Ss,2.5,1.7)                
#                 Fa = (2.5 - 1.7) * (Ss / 0.25)
        elif Ss > 0.5 and Ss <= 0.75:
            
            if (site_class == "A"):
                Fa = 0.8
            elif (site_class == "B"):
                Fa = 1.0
            elif (site_class == "C"):
                Fa = interpolate(Ss,1.2,1.1)
#                 Fa = (1.2 - 1.1) * (Ss / 0.25)
            elif (site_class == "D"):
                Fa = interpolate(Ss,1.4,1.2)
#                 Fa = (1.4 - 1.2) * (Ss / 0.25)
            elif (site_class == "E"):
                Fa = interpolate(Ss,1.7,1.2)
#                 Fa = (1.7 - 1.2) * (Ss / 0.25)

        elif Ss > 0.75 and Ss <= 1.00:

            if (site_class == "A"):
                Fa = 0.8
            elif (site_class == "B"):
                Fa = 1.0
            elif (site_class == "C"):
                Fa = interpolate(Ss,1.1,1.0)                
#                 Fa = (1.1 - 1.0) * (Ss / 0.25)
            elif (site_class == "D"):
                Fa = interpolate(Ss,1.2,1.1)
#                 Fa = (1.2 - 1.1) * (Ss / 0.25)
            elif (site_class == "E"):
                Fa = interpolate(Ss,1.2,0.9)
#                 Fa = (1.2 - 0.9) * (Ss / 0.25)

        elif Ss > 1.00 and Ss <= 1.25:
            
            if (site_class == "A"):
                Fa = 0.8
            elif (site_class == "B"):
                Fa = 1.0
            elif (site_class == "C"):
                Fa = 1.0
            elif (site_class == "D"):
#                 Fa = * (Ss / 0.25) * (1.1 - 1.0)
                Fa = interpolate(Ss,1.1,1.0)
            elif (site_class == "E"):
                Fa = 0.9
                
        elif (Ss >= 1.25):

            if (site_class == "A"):
                Fa = 0.8
            elif (site_class == "B"):
                Fa = 1.0;
            elif (site_class == "C"):
                Fa = 1.0
            elif (site_class == "D"):
                Fa = 1.0
            elif (site_class == "E"):
                Fa = 0.9

        #MCEr spectral response acceleration parameter at a period of 1

        if (S_one <= 0.1):
            if (site_class == "A"):
                Fv = 0.8
            elif (site_class == "B"):
                Fv = 1.0
            elif (site_class == "C"):
                Fv = 1.7
            elif (site_class == "D"):
                Fv = 2.4
            elif (site_class == "E"):
                Fv = 3.5

        elif S_one > 0.1 and S_one <= 0.2:

            if (site_class == "A"):
                Fv = 0.8
            elif (site_class == "B"):
                Fv = 1.0;
            elif (site_class == "C"):
                Fv = interpolateFv(S_one,1.7,1.6)
#                 Fv = (1.7 - 1.6) * (S_one / 0.10)
            elif (site_class == "D"):
                Fv = interpolateFv(S_one,2.4,2)
#                 Fv = (2.4 - 2.0) * (S_one / 0.10)
            elif (site_class == "E"):
                Fv = interpolateFv(S_one,3.5,3.2)        
#                 Fv = (3.5 - 3.2) * (S_one / 0.10)

        elif S_one > 0.2 and S_one <= 0.3 :

            if (site_class == "A"):
                Fv = 0.8
            elif (site_class == "B"):
                Fv = 1.0
            elif (site_class == "C"):
                Fv = interpolateFv(S_one,1.6,1.5)
#                 Fv = (1.6 - 1.5) * (S_one / 0.10)
            elif (site_class == "D"):
                Fv = interpolateFv(S_one,2.0,1.8)                
#                 Fv = (2.0 - 1.8) * (S_one / 0.10)
            elif (site_class == "E"):
                Fv = interpolateFv(S_one,3.2,2.8)
#                 Fv = (3.2 - 2.8) * (S_one / 0.10)

        elif S_one > 0.3 and S_one <= 0.4:

            if (site_class == "A"):
                Fv = 0.8
            elif (site_class == "B"):
                Fv = 1.0
            elif (site_class == "C"):
                Fv = interpolateFv(S_one,1.5,1.4)
#                 Fv = (1.5 - 1.4) * (S_one / 0.10)
            elif (site_class == "D"):
                Fv = interpolateFv(S_one,1.8,1.6)
#                 Fv = (1.8 - 1.6) * (S_one / 0.10)
            elif (site_class == "E"):
                Fv = interpolateFv(S_one,2.8,2.4)
#                 Fv = (2.8 - 2.4) * (S_one / 0.10)

        elif S_one > 0.4 and S_one < 0.5:

            if (site_class == "A"):
                Fv = 0.8
            elif (site_class == "B"):
                Fv = 1.0;
            elif (site_class == "C"):
                Fv = interpolateFv(S_one,1.4,1.3)
#                 Fv = (1.4 - 1.3) * (S_one / 0.10)
            elif (site_class == "D"):
                Fv = interpolateFv(S_one,1.6,1.5)
#                 Fv = (1.6 - 1.5) * (S_one / 0.10)
            elif (site_class == "E"):
                Fv = 2.4;
                
        elif (S_one >= 0.5):
            if (site_class == "A"):
                Fv = 0.8
            elif (site_class == "B"):
                Fv = 1.0
            elif (site_class == "C"):
                Fv = 1.3
            elif (site_class == "D"):
                Fv = 1.5
            elif (site_class == "E"):
                Fv = 2.4
            
        results = {
            "fa" : Fa,
            "fv" : Fv
        }
     
        return results
    




def responseSpecturmCurve(Ss,S1,Fa,Fv,TL,reduce):
    
        Sms = Fa*Ss
        Sm1 = Fv*S1
        R = 8
        
        if reduce == True:
            factor = 2/3
        else : 
            factor = 1
        
        Sds = factor*Sms
        Sd1 = factor*Sm1
        
        TL_max = TL
        To = ((0.20*Sd1)/Sds)
        Ts = Sd1/Sds

        x_axis_value_curve = [] 
        y_axis_value_curve = []
        scaled_curve = []           
    
        ###USED IN PLOTTING CURVE
        # secs_x = []
        # sa_y = []
    
        for i in range(800):
            seconds = float(i)/100

            if seconds >= 0 and seconds < To: 
                
                sa_jsx_b = (0.6*seconds)/To
                sa_jsx = Sds*( 0.4 + sa_jsx_b)
                scaled = sa_jsx*(1/R)
                
            elif To <= seconds and seconds <= Ts: 
            
                sa_jsx = Sds
                scaled = sa_jsx*(1/R)           
            elif Ts < seconds and seconds <= TL_max:
                
                sa_jsx = Sd1/seconds
                scaled = sa_jsx*(1/R)            
            
            elif seconds > TL_max:
                
                sa_jsx = Sd1*(TL_max/seconds**2)
                scaled = sa_jsx*(1/R)
                
            x_axis_value_curve.append(seconds)
            y_axis_value_curve.append(sa_jsx)
            scaled_curve.append(scaled)    
            
        ####################
        ### USED IN TABLE ## 
        ####################
        
        table_x = []
        table_y = []
    
        for i in range(25):
            seconds = float(i)*0.2

            if seconds >= 0 and seconds < To: 

                sa_jsx_b = (0.6*seconds)/To
                sa_jsx = Sds*( 0.4 + sa_jsx_b)

            elif To <= seconds and seconds <= Ts: 

                sa_jsx = Sds

            elif Ts < seconds and seconds <= TL_max:

                sa_jsx = Sd1/seconds

            elif seconds > TL_max:

                sa_jsx = Sd1*(TL_max/seconds**2)

            table_x.append(round(seconds,3))
            table_y.append(round(sa_jsx,3))

            curve = {
                "elastic" : {
                    "x" : x_axis_value_curve,
                    "y" : y_axis_value_curve, 
                    "scaled" : scaled_curve
                    },
                "TABLE" : {
                    "x" : table_x,
                    "y" : table_y
                     },
                "value" : {
                    "Sds" : Sds,
                    "Sd1" : Sd1,
                    "To" : To, 
                    "Ts" : Ts
                }
                    
            }  


            return curve
            
            


         




