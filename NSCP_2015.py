
def zone(Z):
    if Z == "4":
        results = {
            "value": 0.4,
            "text" : "Zone 4, Z = 0.4"            
        }
    elif Z == "2":
        results = {
            "value" : 0.2 ,
            "text" : "Zone 2, Z = 0.2"          
        }        
    else:
        results = {
            "value" : Z ,
            "text" : "Inputted Z is not available in the Philippines"     
        }
    
    return results

##Source factor
 
near_source = {
        "Na" : {
            "2" : {
                "A" : 1.5,
                "B" : 1.3,
                "C" : 1.0
            }, 
            "5" : {
                "A" : 1.2,
                "B" : 1.0,
                "C" : 1.0
            }, 
            "10" : {
                "A" : 1.0,
                "B" : 1.0,
                "C" : 1.0
            }        
        },
        "Nv" : {
            "2" : {
                "A" : 2.0,
                "B" : 1.6,
                "C" : 1.0
            },
            "5" : {
                "A" : 1.6,
                "B" : 1.2,
                "C" : 1.0 
            },
            "10" : {
                "A" : 1.2,
                "B" : 1.0,
                "C" : 1.0 
            },
            "15" : {
                "A" : 1.0,
                "B" : 1.0,
                "C" : 1.0             
            } 
        }
    }

site_coefficent = {
        "Ca" : { 
            "s_a" : {
                "2" : 0.16,
                "4" : 0.32
            },
            "s_b" : {
                "2" : 0.20,
                "4" : 0.40
            },
            "s_c" : {
                "2" : 0.24,
                "4" : 0.40
            }, 
            "s_d" : {
                "2" : 0.28,
                "4" : 0.44
            }, 
            "s_e" : {
                "2" : 0.34,
                "4" : 0.44
            } 
        }, 
        "Cv" : {
            "s_a" : {
                "2" : 0.16,
                "4" : 0.32
            },
            "s_b" : {
                "2" : 0.20,
                "4" : 0.40
            },
            "s_c" : {
                "2" : 0.32,
                "4" : 0.56
            }, 
            "s_d" : {
                "2" : 0.40,
                "4" : 0.64
            }, 
            "s_e" : {
                "2" : 0.64,
                "4" : 0.96
            } 
        }
    }

def interpolate(X,Y,Y1):
    value = (Y1/Y)*X
    return value

class siteCoef:
    def __init__(param,distance,source_type,soil_type,zone):
            param.distance = distance
            param.source_type = source_type
            param.soil_type = soil_type
            param.zone = zone
            
    def na(param):
            distance = param.distance
            source_type = param.source_type
            
            if distance <= 2:

                Na = near_source["Na"]["2"][source_type]

            elif distance > 2 and distance < 5:

                Na_init1 = near_source["Na"]["2"][source_type] #1.5
                Na_init2 = near_source["Na"]["5"][source_type] #1.2

                Y = 3 # total distance
                X = Na_init1 - Na_init2 #0.3
                Y1 = distance - 2
                
                Na_init = interpolate(X,Y,Y1) #0.07
                Na = Na_init1 - Na_init #1.43 or #1.333

            elif distance == 5:

                Na = near_source["Na"]["10"][source_type]

            elif distance > 5 and distance < 10: 

                Na_init1 = near_source["Na"]["5"][source_type]
                Na_init2 = near_source["Na"]["10"][source_type]
        
                Y = 5 # total distance
                X = Na_init1 - Na_init2
                Y1 = distance - 5
                
                Na_init = interpolate(X,Y,Y1)
                Na = Na_init1 - Na_init
            
            elif distance >= 10:

                Na = near_source["Na"]["10"][source_type]
            
            return Na
    def nv(param):
            
            #Variables.
            distance = param.distance
            source_type = param.source_type

            if distance <= 2:

                Nv = near_source["Nv"]["2"][source_type]

            elif distance > 2 and distance < 5: 

                init1 = near_source["Nv"]["2"][source_type] #2.0
                init2 = near_source["Nv"]["5"][source_type] #1.6

                Y = 3 # total distance
                X = init1 - init2
                Y1 = distance - 2
                
                Nv_init = interpolate(X,Y,Y1)
                Nv = init1 - Nv_init

            elif distance == 5: 

                Nv = near_source["Nv"]["5"][source_type]

            elif distance > 5 and distance < 10:
                
                init1 = near_source["Nv"]["5"][source_type]
                init2 = near_source["Nv"]["10"][source_type]
    
                Y = 5 # total distance
                X = init1 - init2
                Y1 = distance - 5
                
                Nv_init = interpolate(X,Y,Y1)
                Nv = init1 - Nv_init
    
            elif distance == 10: 

                Nv = near_source["Nv"]["10"][source_type]

            elif distance > 10 and distance < 15:

                init1 = near_source["Nv"]["10"][source_type]
                init2 = near_source["Nv"]["15"][source_type]
                  
                # difference_distance = 5
                dist_diff =  (distance-10)/5
                difference_factor_init = init1 - init2
                if difference_factor_init == 1:
                    difference_factor =  1
                else: 
                    difference_factor = difference_factor_init
                
                a = difference_factor*dist_diff
                b = init1 - a

                Nv = b
                
            elif distance >= 15:

                Nv = near_source["Nv"]["15"][source_type]

            return Nv
    def ca(param):
            
            Na = param.na()
            soil_type = param.soil_type
            zone = param.zone
            Ca_init = site_coefficent["Ca"][soil_type][zone]

            def final(value): 
                if value == '2': 
                    output = Ca_init
                    return output
                elif value == '4':
                    output = Ca_init*Na
                    return output

            results = final(zone)
            
            return results
        
    def cv(param):
            
            Nv = param.nv()
            soil_type = param.soil_type
            zone = param.zone
            Cv_init = site_coefficent["Cv"][soil_type][zone]
         
            def final(value): 
                if value == '2': 
                    output = Cv_init
                    return output
                elif value == '4':
                    output = Cv_init*Nv
                    return output              
            
            results = final(zone)
            
            return results
        

def GMCURVE(data,R,report):
    R = 8.5
    #imported parameters
    Ca = data["Ca"]
    Cv = data["Cv"]
    
    twoptfiveCa = 2.5*Ca
    
    Ts = Cv/twoptfiveCa
    To = 0.2*Ts

    ###USED IN PLOTTING CURVE
    elastic_x = []
    elastic_y = []
    inelastic_x = []
    inelastic_y = []    
    for i in range(500):
            seconds = float(i)/100
            control_period = seconds/Ts
            if control_period == 0: 
                sa_index = Ca
                in_sa_index = Ca/R
            elif control_period > 0 and control_period <= 0.2:
                continue
            elif control_period > 0.2 and control_period <= 1:
                sa_index = twoptfiveCa
                in_sa_index = twoptfiveCa/R                
            elif control_period > 1 and control_period < 5:
                sa_index = Cv/seconds
                in_sa_index = (Cv/seconds)/R  
            elif control_period >= 5:
                continue
            elastic_x.append(control_period)
            elastic_y.append(sa_index)
            inelastic_x.append(control_period)
            inelastic_y.append(in_sa_index)    
            
    table_x = []
    table_y = []
    
    for i in range(25):
            seconds = float(i)*0.2
        
            if seconds == 0: 
                sa_index = Ca
            elif seconds > 0 and seconds <= To: 
                continue
            elif seconds > To and seconds <= Ts:
                sa_index = twoptfiveCa
            elif seconds > Ts:
                sa_index = Cv/seconds

            table_x.append(round(seconds,3))
            table_y.append(round(sa_index,3))
            
            curve = {
                "elastic" : {
                    "x" : elastic_x,
                    "y" : elastic_y
                },
                "inelastic" : {
                    "x" : inelastic_x,
                    "y" : inelastic_y
                },
                "TABLE" : {
                    "x" : table_x,
                    "y" : table_y
                },
                "max_sa" : twoptfiveCa,
                "Ca" : Ca,
                "Cv" : Cv,
                # "Na" : ,
                # "Nv" : 
            }  
        
    
    return curve

test = siteCoef(2,"A","s_d","4")
na = test.na()
nv = test.nv()
ca = test.ca()
cv = test.cv()
print(na)
print(nv)
print(ca)
print(cv)






