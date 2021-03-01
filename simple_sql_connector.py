import mysql.connector
from mysql.connector import errorcode
import pandas as pd









#***********************************************************************
#***********************************************************************




config = {
  'user': 'temp',
  'password': 'pass',
  'host': '127.0.0.1',
  'database':'test',
  'raise_on_warnings': True
}

TABLES = {}

TABLES['feed_cut_seq'] = (
    "CREATE TABLE `feed_cut_seq` ("
    "  `index` int(11) NOT NULL AUTO_INCREMENT,"
    "  `tool_to_use` varchar(14) NOT NULL,"
    "  `primary_feed` int(16) NOT NULL,"
    "  `secondary_feed` int(14) NOT NULL,"
    "  `sheet_count` int(12) NOT NULL,"
    "  PRIMARY KEY (`index`)"
    ") ENGINE=InnoDB")


cnx = mysql.connector.connect(**config)

cursor = cnx.cursor()

cursor.execute('SHOW TABLES;')
print(cursor.fetchall())

def createInitialTables():
        
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
            
createInitialTables()

#***********************************************************************
#***********************************************************************

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
sl = 100000

#assuming the sheet starts at V
start = 0


#updating distances once the cuts are made
def resetDistances(i,d,patternLen):
    d[i] = patternLen

counter=0
while start < sl:

    closest_cut = min([i for i in dist.values()])     #find the closest cut
    feed_sequence.append(closest_cut)
    for i in dist.keys():
        if dist[i] == closest_cut:
            query = """INSERT INTO 
            feed_cut_seq (tool_to_use,primary_feed, secondary_feed, sheet_count) 
            VALUES(%s,%s,%s,%s)"""
            counter+=1
            cursor.execute(query,(cut_map[i],closest_cut,0,counter))
            cut_sequence.append(cut_map[i])
            resetDistances(i,dist,patternLen)
        else:
            dist[i] -= closest_cut

    start += closest_cut
    
    
cut_feed = list(zip(feed_sequence,cut_sequence))
df = pd.DataFrame(data = cut_feed, columns=['Feed', 'Cut'])
temp = pd.ExcelWriter('sample_cut_programs/CutFeed_0.xlsx')
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









#***********************************************************************
#***********************************************************************


query = ("SELECT * FROM feed_cut_seq ")

cursor.execute(query)

for (index, ttu, pf,sf,count) in cursor:
    print('{0} - {1} - {2} - {3} - {4}'.format(index, ttu, pf,sf,count))

proceed = input('Write to db ? (y or n) - ')
if proceed == 'y':
    cnx.commmit()
cursor.close()
cnx.close()



#***********************************************************************
#***********************************************************************
