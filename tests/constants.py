#!/usr/bin/env python3
'''
The Constants used for Testing

Copyright (C) 2025 Jason Piszcyk
Email: Jason.Piszcyk@gmail.com

All rights reserved.

This software is private and may NOT be copied, distributed, reverse engineered,
decompiled, or modified without the express written permission of the copyright
holder.

The copyright holder makes no warranties, express or implied, about its 
suitability for any particular purpose.
'''
###########################################################################
#
# Imports
#
###########################################################################
# Shared variables, constants, etc

# System Modules
import crypto_tools

# Local app modules

# Imports for python variable type hints


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#

#
# Constants
#
DEFAULT_STR_VALUE = "default_string_value"
DEFAULT_TIMEOUT = 2
DEFAULT_WAIT = 1

BASIC_NAME = "VariableName"
DOT_NAME = "dot.name"
SIMPLE_STR_VALUE = "Value for simple variable"

ENCRYPTION_OPTION_SETS = {
    "No_Password": {},
    "Password": { "password": "simple_password" },
    "Password_and_Salt": {
        "password": "simple_password",
        "salt": crypto_tools.fernet.generate_salt() 
    }
}

DOT_NAME_LIST = [ "1", "2.1", "2.2" , "2.3.1" ]
INVALID_DOT_NAME_LIST = [
    "1.1",  # Trying to add a branch when a value is set
    "2"     # Trying to add a value in the lower level of a tree
]

#
# Global Variables
#
