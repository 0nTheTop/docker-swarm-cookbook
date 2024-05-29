import sys
sys.dont_write_bytecode = True

import yaml, os
from typing import Dict, Union

class ConfigReader:
    def __init__(self, file_path=None) -> None:
        self.file_path = file_path
        
    def read_config(self, file_path=None) -> Union[Dict,None]:
        if file_path is None:
            file_path = self.file_path 
        
        # If still file path is None - return None    
        if file_path is None:
            return None
        
        # Check if file_path exist/if not - then check if it is just file name and if it exist in config folder
        if not os.path.exists(file_path):
            file_path = os.path.join("config", file_path)

        # read local json file and return as dict
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            return data