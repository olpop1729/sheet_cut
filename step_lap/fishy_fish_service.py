
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Offset
from shared.pandas_utils import PandasWriterReader

class FishyFishService:
    def __init__(self, length_list, step_lap_count, step_lap_distance, layers, scrap_length, is_skewed=False):
        self.length_list = length_list
        self.fish_len = sum(length_list)
        self.step_lap_count = step_lap_count
        self.step_lap_distance = step_lap_distance
        self.layers = layers
        self.scrap = scrap_length
        self.is_skewed = is_skewed
        
        if self.is_skewed:
            self.k = self.step_lap_count - 1
        else:
            self.k = self.step_lap_count // 2
            
        self.hole = self._create_hole_list()
        self.exe = []
        self.pattern_length = 0

    def _create_hole_list(self):
        pos = 0
        ret = []
        if len(self.length_list) > 1:
            for i in range(len(self.length_list)-1):
                pos = round(pos + self.length_list[i], 5)
                ret.append(pos)
        return ret

    def calculate_cut_sequence(self):
        exe = []
        d = self.step_lap_distance
        k = self.k
        l = self.fish_len
        m = self.layers
        x = self.scrap
        n = self.step_lap_count
        mult = 1
        if n % 2 == 0:
            for i in range(n*m):
                if len(self.hole) > 0:
                    for j in self.hole:
                        exe.append(['h', i*(l+mult*(n - 1)*d) + j + (2*(k - 0.5) - i//m)*d])
                exe.append(['fm45', (3*(k-0.5)-2*(i//m))*d + (l+mult*(n-1)*d)*i])
                exe.append(['fp45', ((k-0.5)-2*(i//m))*d + ((l+mult*(n-1)*d)*(i+1))])
                exe.append(['v', i*(2*x+l+mult*(n - 1) * d)])
            self.pattern_length = n * ( 2*x + l + mult * ( n - 1 ) * d ) * m
        else:
            for i in range(self.step_lap_count*m):
                if len(self.hole) > 0:
                    for j in self.hole:
                        exe.append(['h', i*(2*x + l + mult*(n - 1)*d) + j + (2*k - i//m)*d + x])
                exe.append(['fm45', (3*k-2*(i//m))*d + x + (2*x+l+mult*(n-1)*d)*i])
                exe.append(['fp45', (k-2*(i//m))*d - x + ((2*x+l+mult*(n-1)*d)*(i+1))])
                exe.append(['v', i*(2*x + self.fish_len + mult * (self.step_lap_count - 1) * self.step_lap_distance)])
            self.pattern_length = n * ( 2*x + l + mult * ( n - 1 ) * d ) * m
            
        self.exe = exe
        return self.exe

    def generate_feed_commands(self):
        # Use shared Offset values
        offset_fp45 = Offset.FP45
        offset_fm45 = Offset.FM45
        distance_shear = Offset.DISTANCE_SHEAR_VNOTCH - 0.5  # 4334.5
        distance_hole = Offset.DISTANCE_HOLE_VNOTCH + 0.125  # 1250.125
        
        if not self.exe:
            self.calculate_cut_sequence()
        
        # Deep copy to avoid modifying original exe state permanently across calls
        # The original code modifies 'exe' in place. 
        # We should iterate on a copy for simulation 
        # BUT original code modifies self.exe and continues using it?
        # Actually, look at the loop: 
        # for i in self.exe: ... i[1] += ...
        # Yes, it modifies self.exe permanently before the loop.
        
        sim_exe = [x[:] for x in self.exe]
        
        # Apply offsets once
        for i in sim_exe:
            if i[0] == 'fp45':
                i[1] += distance_shear + offset_fp45
            elif i[0] == 'fm45':
                i[1] += distance_shear + offset_fm45
            elif i[0] == 'h':
                i[1] += distance_hole
            i[1] = round(i[1], 5)

        terminate = 200
        feed = []
        vaxis = []
        operation = []
        
        while terminate > 0:
            terminate -= 1
            close = min([i[1] for i in sim_exe])
            repeat = False

            # We need to iterate and possibly modify multiple items
            # The original code iterates over self.exe and modifies i[1]
            # Since we are iterating over the list we are modifying, we need to be careful
            # Python handles this iteration fine as long as we don't add/remove items
            
            # Key difference: original code `if repeat: ... else: ...` 
            # effectively groups operations at the same 'close' distance.
            
            # Let's replicate exact behavior
            for i in sim_exe:
                if i[1] == close:
                    if i[0] == 'v':
                        if self.step_lap_count % 2 == 0:
                            # Original: vaxis.append((self.k-0.5) * self.step_lap_distance + self.scrap)
                            vaxis_val = (self.k-0.5) * self.step_lap_distance + self.scrap
                        else:
                            # Original: vaxis.append(self.k * self.step_lap_distance + self.scrap)
                            vaxis_val = self.k * self.step_lap_distance + self.scrap
                        vaxis.append(vaxis_val)
                    else:
                        vaxis.append(0)
                        
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(close)
                        # repeat is set to True below
                    
                    operation.append(i[0])
                    i[1] = self.pattern_length
                    repeat = True
                else:
                    i[1] -= close
                    i[1] = round(i[1], 5)

        return feed, vaxis, operation
        
    def export_data(self, filename):
        feed, vaxis, operation = self.generate_feed_commands()
        PandasWriterReader.writeExcelSimple(filename, feed, vaxis, operation)
        
if __name__ == "__main__":
    pass
