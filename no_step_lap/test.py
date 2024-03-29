#import inputs
import pandas as pd

dav = 4335
dhv = 1250

#coil start positoin with respect to V notch
coil_start_pos = 0

cdav = dav + coil_start_pos
cdhv = dhv + coil_start_pos

tool_name_map = {'h':['Hole Punch', cdhv],
                 'v':['V Notch',coil_start_pos],
                 'fp45':['Full Cut +45',cdav],
                 'fm45':['Full Cut -45',cdav],
                 'f0':['Full Cut 0', cdav],
                 'pfr':['Partial Front Right',cdav],
                 'pfl':['Partial Front Left', cdav],
                 'prr':['Partial Rear Right',cdav],
                 'prl':['Partial Rear Left',cdav]
                 }


#for i in tool_name_map.keys():
#    print(i , ' - - ' , tool_name_map[i])
class Tool():
    
    def __init__(self,name,pos,pd=None,step_lap=0,step_lap_dist=0):
        self.name = name
        self.pos = pos
        self.pd = pd
        self.step_lap = step_lap
        self.step_lap_dist = step_lap_dist
        self.step_lap_counter = 0
        self.step_lap_dlist = []
        self.is_front = False
        self.is_open = False
        
    def isPartial(self):
        if self.name[0] == 'p':
            return True
        return False
    
    def longname(self):
        return tool_name_map[self.name][0]
    
    def generateStepLapDlist(self):
        # n = self.step_lap
        # for i in range(n // 2 +1):
        #     if i == 0:
        #         self.step_lap_dlist.append(0)
        #     else:
        #         self.step_lap_dlist.append(-self.step_lap_dist*i)
        #         self.step_lap_dlist.append(self.step_lap_dist*i)
        # self.step_lap_dlist = sorted(self.step_lap_dlist)
        self.step_lap_dlist = [i*self.step_lap_dist for i in range(self.step_lap)]

#temporary input        

tool_list = []
while True:
    pdist = None
    cmd = input('Enter option - ')
    if cmd == 'q':
        break
    else:
        name = input('Enter name - ')
        pos = input('Enter position - ')
        if name[0] == 'p':
            pdist = int(input('Enter height of the partial cut - '))
        if name not in tool_name_map.keys():
            print('Invalid tool name')
            continue
        #stplp_dist = inputs.getStepLapDistance()
        #stptlp = inputs.getStepLap()
        tool = Tool(name, int(pos), pdist)
        #tool.generateStepLapDlist()
        tool_list.append(tool)
        
        
pattern_len = int(input('Enter Pattern Length - '))

# for i in tool_list:
#     print(i.longname())

#********** initial distances ***************
dist = {}

for i in tool_list:
    if i.name == 'pr':
        continue
    dist[i] = i.pos + tool_name_map[i.name][1]
    #print(i.longname(),'  -  ',dist[i])
    
#********************************************

def feedPrimary(d, dist):
    for i in dist.keys():
        dist[i] += d


def resetDist(d, pl, tool):
    pass


#********************************************

start = 0
coil_length = 100000
prev_partial = 0
primary_feed = []
operation = []
secondary_feed = []

while start < coil_length:
    closest_cut = min([i for i in dist.values()])
    for i in dist.keys():
        if dist[i] == closest_cut:
            #resetDist(dist[i], pattern_len, i)
            dist[i] = pattern_len
            if i.isPartial():
                prev_partial = i.pd
            elif i.name[0] == 'f' and prev_partial > 0:
                primary_feed.append(closest_cut)
                secondary_feed.append(0)
                operation.append(i.longname())
                primary_feed.append(-1*prev_partial)
                secondary_feed.append(prev_partial)
                operation.append('Full Cut 0')
                feedPrimary(prev_partial,dist)
                prev_partial = 0
            else:
                primary_feed.append(closest_cut)
                operation.append(i.longname())
                secondary_feed.append(0)
        else:
                dist[i] -= closest_cut
    start += closest_cut

cut_feed = list(zip(primary_feed,secondary_feed,operation))
df = pd.DataFrame(data = cut_feed, columns=['Primary Feed', 'Secondary Feed','Operation'])
temp = pd.ExcelWriter('../cut_program_output/CutFeedTip.xlsx')
df.to_excel(temp)
temp.save()
del temp

