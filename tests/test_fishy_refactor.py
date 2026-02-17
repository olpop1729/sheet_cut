
import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
# We import inside test methods or use direct reference if modules available
# But we need to make sure the import paths work.
from step_lap import fishy_fish_with_scrap
from step_lap.fishy_fish_service import FishyFishService
from shared.pandas_utils import PandasWriterReader

class TestFishyRefactor(unittest.TestCase):
    
    @patch('builtins.input')
    @patch('shared.pandas_utils.PandasWriterReader.writeExcelSimple')
    def test_output_parity_case1(self, mock_write_excel, mock_input):
        """Test standard case: Odd step lap, not skewed"""
        print("\nRunning Test Case 1: Standard (Odd Step Lap)...")
        
        # Inputs
        scrap = "50"
        step_lap_count = "5" 
        is_skewed = "n"
        step_lap_distance = "10"
        lengths = "100 200"
        layers = "2"
        
        mock_input.side_effect = [
            scrap, 
            step_lap_count, 
            is_skewed, 
            step_lap_distance, 
            lengths, 
            layers
        ]
        
        # Run legacy
        # Refreshes internal state of JobProfile inside main() ideally
        fishy_fish_with_scrap.main()
        
        # Capture legacy output
        # writeExcelSimple(fname, feed, v_axis, operation)
        legacy_args = mock_write_excel.call_args[0]
        legacy_feed = legacy_args[1]
        legacy_vaxis = legacy_args[2]
        legacy_ops = legacy_args[3]
        
        # Run new service
        service = FishyFishService(
            length_list=[100.0, 200.0],
            step_lap_count=5,
            step_lap_distance=10.0,
            layers=2,
            scrap_length=50.0,
            is_skewed=False
        )
        
        new_feed, new_vaxis, new_ops = service.generate_feed_commands()
        
        # Compare
        self.assertEqual(legacy_feed, new_feed, "Feed lists do not match")
        self.assertEqual(legacy_vaxis, new_vaxis, "V-axis lists do not match")
        self.assertEqual(legacy_ops, new_ops, "Operations do not match")
        print("Test Case 1 passed!")

    @patch('builtins.input')
    @patch('shared.pandas_utils.PandasWriterReader.writeExcelSimple')
    def test_output_parity_case2(self, mock_write_excel, mock_input):
        """Test case: Even step lap, skewed"""
        print("\nRunning Test Case 2: Even Step Lap, Skewed...")
        
        # Inputs
        scrap = "30"
        step_lap_count = "4" 
        is_skewed = "y"
        step_lap_distance = "15"
        lengths = "150 250 100"
        layers = "1"
        
        mock_input.side_effect = [
            scrap, 
            step_lap_count, 
            is_skewed, 
            step_lap_distance, 
            lengths, 
            layers
        ]
        
        # Run legacy
        fishy_fish_with_scrap.main()
        
        # Capture legacy output
        legacy_args = mock_write_excel.call_args[0]
        legacy_feed = legacy_args[1]
        legacy_vaxis = legacy_args[2]
        legacy_ops = legacy_args[3]
        
        # Run new service
        service = FishyFishService(
            length_list=[150.0, 250.0, 100.0],
            step_lap_count=4,
            step_lap_distance=15.0,
            layers=1,
            scrap_length=30.0,
            is_skewed=True
        )
        
        new_feed, new_vaxis, new_ops = service.generate_feed_commands()
        
        # Compare
        self.assertEqual(legacy_feed, new_feed, "Feed lists do not match")
        self.assertEqual(legacy_vaxis, new_vaxis, "V-axis lists do not match")
        self.assertEqual(legacy_ops, new_ops, "Operations do not match")
        print("Test Case 2 passed!")

if __name__ == '__main__':
    unittest.main()
