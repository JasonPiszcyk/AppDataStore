#!/usr/bin/env python3
'''
Datastore - Mem

Copyright (C) 2025 Jason Piszcyk
Email: Jason.Piszcyk@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (See file: COPYING). If not, see
<https://www.gnu.org/licenses/>.
'''
###########################################################################
#
# Imports
#
###########################################################################
from __future__ import annotations

# Shared variables, constants, etc

# System Modules

# Local app modules
from appdatastore.base import DataStoreBaseClass
# import appcore.datastore.exception as exception
# from appcore.conversion import to_json, from_json, set_value, DataType
# from appcore.util.functions import timestamp

# Imports for python variable type hints
# from typing import Any
# from threading import Lock as LockType


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


#
# Global Variables
#


###########################################################################
#
# DataStoreMem Class Definition
#
###########################################################################
class DataStoreMem(DataStoreBaseClass):
    '''
    Class to describe the local datastore.

    The data is stored in a dictionary that is made available in memory

    Attributes:
        None
    '''
    # We only want one instance of this class.  Store the instance to 
    # provide it if the constructgor is called again
    _instance = None


    #
    # __init__
    #
    def __init__(
            self,
            *args,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes

        # Attributes


    #
    # __new__
    #
    def __new__(cls, *args, **kwargs) -> DataStoreMem:
        '''
        Create the instance.

        Args:
            None

        Returns:
            DataStoreGlobal: The instance

        Raises:
            None
        '''
        # If this is the first time, create the instance and store it
        if cls._instance is None:
            cls._instance = super(DataStoreMem, cls).__new__(cls)

        return cls._instance


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


###########################################################################
#
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass
