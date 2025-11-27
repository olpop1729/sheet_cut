#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base tool classes for sheet_cut application.
These classes represent the various cutting tools used in the machine.
"""

from .labels import Labels
from .config import Config


class BaseTool:
    """
    Base class for all cutting tools. Provides common functionality
    for step-lap handling and position tracking.
    """
    
    def __init__(self, var_dict=None):
        self.name = ''
        self.pos = 0
        self.step_lap_count = 1
        self.step_lap_counter = 0
        self.step_lap_distance = 0
        self.step_lap_vector = []
        self.is_front = False
        self.is_rear = False
        self.is_open = False
        
        if var_dict:
            self.loadFromDict(var_dict)
    
    def loadFromDict(self, var):
        """Load tool attributes from a dictionary."""
        if 'name' in var:
            self.name = var['name']
        if 'pos' in var:
            self.pos = var['pos']
        if 'step_lap_count' in var:
            self.step_lap_count = var['step_lap_count']
        if 'step_lap_counter' in var:
            self.step_lap_counter = var['step_lap_counter']
        if 'step_lap_distance' in var:
            self.step_lap_distance = var['step_lap_distance']
        if 'step_lap_vector' in var:
            self.step_lap_vector = var['step_lap_vector']
        if 'is_front' in var:
            self.is_front = var['is_front']
        if 'is_rear' in var:
            self.is_rear = var['is_rear']
        if 'is_open' in var:
            self.is_open = var['is_open']
    
    def hasStepLap(self) -> bool:
        """Check if this tool has step-lap enabled (count > 1)."""
        return self.step_lap_count > 1
    
    def lengthyfy(self):
        """
        Return length modification value. Override in subclasses.
        
        Returns:
            For base tools: 0 (no modification)
            For Spear: tuple of ([type, pos], [type, pos]) for v-notch and full cut operations
        """
        return 0
    
    def getIsFront(self):
        """Prompt user for front position setting."""
        is_front = input(Labels.get_is_front)
        if is_front.lower() in Config.LIST_NO:
            self.is_front = False
        else:
            self.is_front = True
    
    def getIsRear(self):
        """Prompt user for rear position setting."""
        is_rear = input(Labels.get_is_rear)
        if is_rear.lower() in Config.LIST_NO:
            self.is_rear = False
        else:
            self.is_rear = True
    
    def getIsOpen(self):
        """Prompt user for open/closed setting."""
        is_open = input(Labels.get_is_open)
        if is_open.lower() in Config.LIST_NO:
            self.is_open = False
        elif is_open.lower() in Config.LIST_YES:
            self.is_open = True
    
    def getStepLapCount(self):
        """Prompt user for step-lap count and validate input."""
        while True:
            try:
                val = int(input(Labels.get_step_lap_count))
                if val < 0:
                    Labels.warnNegativeCount()
                    continue
                if val % 2 == 0 and val > 0:
                    Labels.warnOddCount()
                    continue
                elif val % 2 == 1 and val > 1:
                    if val > 9:
                        Labels.warnHighStepLapCount()
                    self.step_lap_count = val
                    return val
                elif val == 1:
                    return 0
            except Exception as err:
                Labels.printError(err)
    
    def getStepLapDistance(self):
        """Prompt user for step-lap distance and validate input."""
        while True:
            try:
                step_lap_distance = float(input(Labels.get_step_lap_distance))
                if step_lap_distance <= 0:
                    Labels.warnNegativeDistance()
                    continue
                else:
                    if step_lap_distance > 20:
                        Labels.warnHighDistanceValue()
                    self.step_lap_distance = step_lap_distance
                    return step_lap_distance
            except Exception as err:
                Labels.printError(err)
    
    def generateStepLapVector(self):
        """Generate the step-lap vector based on count and distance."""
        self.step_lap_vector = [
            i * self.step_lap_distance 
            for i in range(self.step_lap_count // 2, -self.step_lap_count // 2, -1)
        ]
    
    def setStepLapCounter(self):
        """Set the initial step-lap counter based on open/closed state."""
        if self.is_open:
            self.step_lap_counter = 0
        else:
            self.step_lap_counter = self.step_lap_count - 1
    
    def incrementStepLapCounter(self):
        """Increment or decrement the step-lap counter based on open state."""
        if self.is_open:
            self.step_lap_counter += 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        else:
            self.step_lap_counter -= 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
    
    def show(self):
        """Print all tool attributes for debugging."""
        print(vars(self))


class Hole(BaseTool):
    """
    Hole punch tool class.
    """
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 'h'
        if var_dict:
            self.loadFromDict(var_dict)
    
    def hasStepLap(self) -> bool:
        """Holes typically don't have step-lap."""
        return False


class Vnotch(BaseTool):
    """
    V-notch cutting tool class with lateral shift capability.
    """
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 'v'
        self.lateral_shift_count = 1
        self.lateral_shift_counter = 0
        self.lateral_shift_vector = []
        self.lateral_shift_distance = 0
        self.rear_step_lap_counter = 0
        
        if var_dict:
            self.loadFromDict(var_dict)
    
    def loadFromDict(self, var):
        """Load Vnotch-specific attributes from dictionary."""
        super().loadFromDict(var)
        if 'lateral_shift_count' in var:
            self.lateral_shift_count = var['lateral_shift_count']
        if 'lateral_shift_counter' in var:
            self.lateral_shift_counter = var['lateral_shift_counter']
        if 'lateral_shift_vector' in var:
            self.lateral_shift_vector = var['lateral_shift_vector']
        if 'lateral_shift_distance' in var:
            self.lateral_shift_distance = var['lateral_shift_distance']
        if 'rear_step_lap_counter' in var:
            self.rear_step_lap_counter = var['rear_step_lap_counter']
    
    def incrementLateralShiftCounter(self):
        """Increment or decrement the lateral shift counter."""
        if self.is_open:
            self.lateral_shift_counter += 1
            self.lateral_shift_counter = self.lateral_shift_counter % self.lateral_shift_count
        else:
            self.lateral_shift_counter -= 1
            self.lateral_shift_counter = self.lateral_shift_counter % self.lateral_shift_count
    
    def incrementStepLapCounter(self):
        """Override to handle both front and rear step-lap counters."""
        if self.is_open and self.is_front and not self.is_rear:
            self.step_lap_counter += 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        elif self.is_open and not self.is_front and self.is_rear:
            self.rear_step_lap_counter += 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
        elif not self.is_open and self.is_front and not self.is_rear:
            self.step_lap_counter -= 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        elif not self.is_open and not self.is_front and self.is_rear:
            self.rear_step_lap_counter -= 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
    
    def setStepLapCounter(self):
        """Set initial step-lap counters for front and rear."""
        if self.is_front and self.is_rear and self.is_open:
            self.step_lap_counter = 0
            self.rear_step_lap_counter = self.step_lap_count - 1
        elif not self.is_open and self.is_front and self.is_rear:
            self.step_lap_counter = self.step_lap_count - 1
            self.rear_step_lap_counter = 0
    
    def getLateralShiftDistance(self):
        """Prompt user for lateral shift distance."""
        while True:
            try:
                self.lateral_shift_distance = float(input(Labels.get_lateral_shift_distance))
                return
            except ValueError as err:
                Labels.printError(err)
    
    def getLateralShiftCount(self):
        """Prompt user for lateral shift count."""
        while True:
            try:
                count = int(input(Labels.get_lateral_shift_count))
                if count <= 0:
                    Labels.warnNegativeCount()
                elif count == 1:
                    return 0
                else:
                    if count > 9:
                        Labels.warnHighLateralShiftCount()
                    self.lateral_shift_count = count
                    return count
            except Exception as err:
                Labels.printError(err)
    
    def setLateralShiftCounter(self):
        """Set the initial lateral shift counter."""
        if self.is_open:
            self.lateral_shift_counter = 0
        else:
            self.lateral_shift_counter = self.lateral_shift_count - 1
    
    def generateLateralShiftVector(self):
        """Generate the lateral shift vector."""
        self.lateral_shift_vector = [
            i * self.lateral_shift_distance
            for i in range(-self.lateral_shift_count // 2 + 1,
                          self.lateral_shift_count // 2 + 1)
        ]


class FullCut(BaseTool):
    """
    Base class for full-cut tools (fm45, fp45, f0).
    Extends BaseTool with front/rear open settings.
    """
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.front_open = False
        self.rear_open = False
        self.rear_step_lap_counter = 0
        
        if var_dict:
            self.loadFromDict(var_dict)
    
    def loadFromDict(self, var):
        """Load FullCut-specific attributes from dictionary."""
        super().loadFromDict(var)
        if 'front_open' in var:
            self.front_open = var['front_open']
        if 'rear_open' in var:
            self.rear_open = var['rear_open']
        if 'rear_step_lap_counter' in var:
            self.rear_step_lap_counter = var['rear_step_lap_counter']
    
    def setStepLapCounter(self):
        """Set initial step-lap counters based on front/rear open state."""
        if self.front_open and self.rear_open:
            self.step_lap_counter = 0
            self.rear_step_lap_counter = 0
        elif self.front_open and not self.rear_open:
            self.rear_step_lap_counter = self.step_lap_count - 1
            self.step_lap_counter = 0
        elif not self.front_open and self.rear_open:
            self.step_lap_counter = self.step_lap_count - 1
            self.rear_step_lap_counter = 0
        else:
            self.rear_step_lap_counter = self.step_lap_count - 1
            self.step_lap_counter = self.step_lap_count - 1
    
    def incrementStepLapCounter(self):
        """Increment both front and rear step-lap counters."""
        if self.front_open:
            self.step_lap_counter += 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        elif not self.front_open and self.is_front:
            self.step_lap_counter -= 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        if self.rear_open:
            self.rear_step_lap_counter += 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
        elif not self.rear_open and self.is_rear:
            self.rear_step_lap_counter -= 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
    
    def getFrontOpen(self):
        """Prompt user for front open setting."""
        front_open = input(Labels.get_front_open)
        if front_open.lower() in Config.LIST_NO:
            self.front_open = False
        else:
            self.front_open = True
    
    def getRearOpen(self):
        """Prompt user for rear open setting."""
        rear_open = input(Labels.get_rear_open)
        if rear_open.lower() in Config.LIST_NO:
            self.rear_open = False
        else:
            self.rear_open = True


class Fm45(FullCut):
    """Full cut at -45 degrees."""
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 'fm45'
        if var_dict:
            self.loadFromDict(var_dict)


class Fp45(FullCut):
    """Full cut at +45 degrees."""
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 'fp45'
        if var_dict:
            self.loadFromDict(var_dict)


class F0(FullCut):
    """Full cut at 0 degrees (straight cut)."""
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 'f0'
        if var_dict:
            self.loadFromDict(var_dict)


class Spear(BaseTool):
    """
    Spear tool class - creates spear-shaped cuts.
    Used in central limb cutting operations.
    """
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 's'
        self.front_open = False
        self.rear_open = False
        self.rear_step_lap_counter = 0
        
        if var_dict:
            self.loadFromDict(var_dict)
    
    def loadFromDict(self, var):
        """Load Spear-specific attributes from dictionary."""
        super().loadFromDict(var)
        if 'front_open' in var:
            self.front_open = var['front_open']
        if 'rear_open' in var:
            self.rear_open = var['rear_open']
        if 'rear_step_lap_counter' in var:
            self.rear_step_lap_counter = var['rear_step_lap_counter']
    
    def lengthyfy(self):
        """Return the operation tuple for execution."""
        return ['v', self.pos], ['f', self.pos]


class YokeSplitter(BaseTool):
    """
    Yoke splitter tool class - splits the yoke section.
    Used in split-yoke cutting operations.
    """
    
    def __init__(self, var_dict=None):
        super().__init__(var_dict)
        self.name = 'ys'
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.front_open = False
        
        if var_dict:
            self.loadFromDict(var_dict)
    
    def loadFromDict(self, var):
        """Load YokeSplitter-specific attributes from dictionary."""
        super().loadFromDict(var)
        if 'slp_count' in var:
            self.slp_count = var['slp_count']
        if 'slp_distance' in var:
            self.slp_distance = var['slp_distance']
        if 'slp_vector' in var:
            self.slp_vector = var['slp_vector']
        if 'slp_counter' in var:
            self.slp_counter = var['slp_counter']
        if 'front_open' in var:
            self.front_open = var['front_open']
    
    def hasStepLap(self) -> bool:
        """Check if step-lap is enabled."""
        return self.slp_count > 1
    
    def getSlpCount(self):
        """Prompt user for step-lap count."""
        self.slp_count = int(input('Enter step-lap count :'))
    
    def getSlpDistance(self):
        """Prompt user for step-lap distance."""
        self.slp_distance = float(input('Enter step-lap distance : '))
    
    def generateSlpVector(self):
        """Generate the step-lap vector."""
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i * d for i in range(n // 2, -n // 2, -1)]
        if self.front_open:
            self.slp_counter = 0
        else:
            self.slp_counter = n - 1
    
    def incrementSlpCounter(self):
        """Increment or decrement the step-lap counter."""
        if self.front_open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count
    
    def getFrontOpen(self):
        """Prompt user for front open setting."""
        if input('Front open : ').lower() in ['y', 'yes']:
            self.front_open = True
        else:
            self.front_open = False
