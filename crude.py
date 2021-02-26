import pandas as pd


#Inputs to the program

#distance from start of pattern to the cut type
l = {'h1':100,'h2':300,'a1':0,'a2':400,'v1':200,'v2':500}
#1#l = {'a1':0,'h1':200,'v1':450,'h2':750,'a2':1100,'h3':1500,'h4':1950}
#2#l = {'a1':0,'a2':0,'v1':0,'h1':400,'h2':850}
#3#l = {'a1':20,'a2':,'h1':220,'h2':770,'h3':,'h4':,'v1':470,'v2':,'a3':0,'a4':,'a5':,'a6':}

#distance between cutters
da_dv = 4355        #distance between 45 and V
dh_dv = 1255        #distance between H and V
da_dh = 3100        #distance between 45 and H

patternLen = 600
#1#patternLen = 2450
#2#patternLen = 1350
#3#patternLen = 

cut_sequence = []
feed_sequence = []
cut_map = {}

#intial distances between cutters and cuts
dist = {}
for i in l.keys():
    if i[0] == 'h':
        dist[i] = dh_dv + l[i]
        cut_map[i] = 'Hole Punch'
    elif i[0] == 'a':
        dist[i] = da_dv + l[i]
        if int(i[1]) % 2 == 0:
            cut_map[i] = 'Full Cut -45'
        else:
            cut_map[i] = 'Full Cut +45'
    else:
        cut_map[i] = 'V notch'
        dist[i] = l[i]


#taking some random sheet length
sl = 1000000

#assuming the sheet starts at V
start = 0


#updating distances once the cuts are made
def resetDistances(i,d,patternLen):
    d[i] = patternLen


while start < sl:
    closest_cut = min([i for i in dist.values()])     #find the closest cut
    feed_sequence.append(closest_cut)
    for i in dist.keys():
        if dist[i] == closest_cut:
            cut_sequence.append(cut_map[i])
            resetDistances(i,dist,patternLen)
        else:
            dist[i] -= closest_cut

    start += closest_cut
    
    
cut_feed = list(zip(feed_sequence,cut_sequence))
df = pd.DataFrame(data = cut_feed, columns=['Feed', 'Cut'])
temp = pd.ExcelWriter('CutFeed_0.xlsx')
df.to_excel(temp)
temp.save()
    
    
    
    
    
# import pandas as pd 
# import numpy as np 


# # Reading the csv file 
# df_new = pd.read_csv('Names.csv') 

# # saving xlsx file 
# GFG = pd.ExcelWriter('Names.xlsx') 
# df_new.to_excel(GFG, index = False) 

# GFG.save() 

