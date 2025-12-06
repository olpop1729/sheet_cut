#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 23:09:40 2021

@author: omkar

Fishy fish cutting module. Uses the shared modules for configuration and pandas utilities.
"""

import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Offset
from shared.pandas_utils import PandasModule, PandasWriterReader


class JobProfile():
    def __init__(self):
        self.pattern_length = 0
        self.step_lap_count = 1
        self.k = 0
        self.step_lap_distance = 0
        self.length_list = []
        self.fish_len = 0
        self.hole = []
        self.layers = 1

    def getLayers(self):
        while True:
            try:
                self.layers = int(input('Enter layers : '))
                return
            except ValueError as err:
                print(err)

    def getStepLapInfo(self):
        self.step_lap_count = int(input('Enter step-lap count : '))
        if input('Skewed ? : ').lower() in ['y', 'yes']:
            self.k = self.step_lap_count - 1
        else:
            self.k = self.step_lap_count // 2
        self.step_lap_distance = float(input('Enter step-lap distance : '))

    def getLengthList(self):
        self.length_list = [float(i) for i in input('Enter lengths : ').split()]
        self.fish_len = sum(self.length_list)
        self.createHoleList()

    def createHoleList(self):
        pos = 0
        ret = []
        if len(self.length_list) > 1:
            for i in range(len(self.length_list)-1):
                pos = round(pos + self.length_list[i], 5)
                ret.append(pos)
        self.hole = ret

    def createDict(self):
        exe = []
        d = self.step_lap_distance
        k = self.k
        l = self.fish_len
        m = self.layers
        n = self.step_lap_count
        mult = 1
        if n % 2 == 0:
            print('even count')
            for i in range(n*m):
                if len(self.hole) > 0:
                    for j in self.hole:
                        exe.append(['h', i*(l+mult*(n - 1)*d) + j + (2*(k - 0.5) - i//m)*d])
                exe.append(['fm45', (3*(k-0.5)-2*(i//m))*d + (l+mult*(n-1)*d)*i])
                exe.append(['fp45', ((k-0.5)-2*(i//m))*d + ((l+mult*(n-1)*d)*(i+1))])
                exe.append(['v', i*(l+mult*(n - 1) * d)])
            self.exe = exe
            self.pattern_length = n * ( l + mult * ( n - 1 ) * d ) * m
        else:
            for i in range(self.step_lap_count*m):
                if len(self.hole) > 0:
                    for j in self.hole:
                        #exe.append(['h', j + (2*self.k - i + 2*self.k*i)*self.step_lap_distance + i*self.fish_len])
                        #exe.append(['h',j + i*self.fish_len + self.step_lap_distance*(2*self.k*i + 2*self.k - i)])
                        exe.append(['h', i*(l+mult*(n - 1)*d) + j + (2*k - i//m)*d])
                #exe.append(['fm45', i*self.fish_len + (3+(i//m))*self.k*self.step_lap_distance])
                #exe.append(['fp45',((i//m) + 1)*self.fish_len + (3+(i//m))*self.k*self.step_lap_distance])
                exe.append(['fm45', (3*k-2*(i//m))*d + (l+mult*(n-1)*d)*i])
                exe.append(['fp45', (k-2*(i//m))*d + ((l+mult*(n-1)*d)*(i+1))])
                exe.append(['v', i*(self.fish_len + mult * (self.step_lap_count - 1) * self.step_lap_distance)])
            self.exe = exe
            self.pattern_length = n * ( l + mult * ( n - 1 ) * d ) * m

    def execute(self):
        # Use shared Offset values
        offset_fp45 = Offset.FP45
        offset_fm45 = Offset.FM45
        distance_shear = Offset.DISTANCE_SHEAR_VNOTCH - 0.5  # 4334.5
        distance_hole = Offset.DISTANCE_HOLE_VNOTCH + 0.125  # 1250.125
        
        for i in self.exe:
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
            close = min([i[1] for i in self.exe])
            repeat = False

            for i in self.exe:
                if i[1] == close:
                    if i[0] == 'v':
                        if self.step_lap_count % 2 == 0:
                            vaxis.append((self.k-0.5) * self.step_lap_distance)
                        else:
                            vaxis.append(self.k * self.step_lap_distance)
                    else:
                        vaxis.append(0)
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(close)
                    operation.append(i[0])
                    i[1] = self.pattern_length
                    repeat = True
                else:
                    i[1] -= close
                    i[1] = round(i[1], 5)

        PandasWriterReader.writeExcelSimple('FishyFish_0', feed, vaxis, operation)


def main():
    jp = JobProfile()
    jp.getStepLapInfo()
    jp.getLengthList()
    jp.getLayers()
    jp.createDict()
    for i in sorted(jp.exe, key = lambda x: x[1]):

        print(i[0], '--', i[1])

    jp.execute()




if __name__ == "__main__":
    main()
