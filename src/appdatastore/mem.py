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
from appcore.helpers import timestamp
from appcore.conversion import set_value, DataType, from_json, to_json

# Local app modules
from appdatastore.base import DataStoreBaseClass

# Imports for python variable type hints
from typing import Any

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
    Class to describe the memory datastore.

    The data is stored in a dictionary that is made available in memory

    Attributes:
        None
    '''
    # We only want one instance of this class.  Store the instance to 
    # provide it if the constructor is called again
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
    # Maintenance Functions
    #
    ###########################################################################
    #
    # maintenance
    #
    def maintenance(self):
        '''
        Perform maintenance on items (such as expiry)

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self._logger.debug("Start item maintenance")

        if self._manual_expiry:
            self._logger.debug("Begin manual expiry processing")

            # Process the expiry list
            _now = timestamp()
            _sorted_expiry_list = sorted(self._data_expiry)

            # Use the copy of __data_expiry list as it can change it during
            # processing
            for _entry in _sorted_expiry_list:
                # Extract the timestamp from the key
                _timestamp_str, _, _name = str(_entry).partition("__")
                _timestamp = set_value(
                    data=_timestamp_str,
                    type=DataType.INT,
                    default=0
                )

                # Stop processing if the timestamp is in the future
                if _now < _timestamp: break

                # Remove the entry (and the expiry record)
                self._logger.info(f"Expiring entry: {self._data[_name]}")
                self._lock.acquire()
                if _name in self._data: del self._data[_name]
                self._data_expiry.remove(_entry)
                self._lock.release()

            self._logger.debug("End manual expiry processing")

        self._logger.debug("End item maintenance")


    ###########################################################################
    #
    # Data Access
    #
    ###########################################################################
    #
    # has
    #
    def has(
            self,
            name: str = ""
    ) -> bool:
        '''
        Check if the item exists in the datastore

        Args:
            name (str): The name of the item to check

        Returns:
            bool: True if the item exists, False otherwise

        Raises:
            None
        '''
        self.maintenance()
        return name in self._data


    #
    # get
    #
    def get(
            self,
            name: str = "",
            default: Any = None,
            decrypt: bool = False
    ) -> Any:
        '''
        Get a value

        Args:
            name (str): The name of the item to get
            default (Any): Value to return if the item cannot be found
            decrypt (bool): If True, attempt to decrypt the value

        Returns:
            Any: The value of the item

        Raises:
            None
        '''
        if not self.has(name): return default

        _value = self._data[name]

        _decoded_value = self._decode(value=_value, decrypt=decrypt)

        return _decoded_value


    #
    # set
    #
    def set(
            self,
            name: str = "",
            value: Any = None,
            encrypt: bool = False,
            timeout: int = 0
    ) -> None:
        '''
        Set a value for an item

        Args:
            name (str): The name of the item to set
            value (Any): Value to set the item to
            encrypt (bool): If True, attempt to encrypt the value
            timeout (int): The number of seconds before the item should be
                deleted (0 = never delete)

        Returns:
            None

        Raises:
            AssertionError:
                When timeout is not zero or a positive integer
            KeyError:
                When the dot name is a low part of a hierarchy
        '''
        assert isinstance(timeout, int), "Timeout value must be an integer"
        assert timeout >= 0, "Timeout value must be a postive integer"

        self.maintenance()

        # Check on dot names
        if self._dot_names:
            _keys = list(self._data.keys())
            if not self._check_dot_name(keys=_keys, name=name):
                raise KeyError(
                    "Value cannot be stored in a intermediate dot level name"
                )

        # Encode the value for storage (possibly encrypting)
        _value_to_store = self._encode(value=value, encrypt=encrypt)

        # Set the value
        self._lock.acquire()
        self._data[name] = _value_to_store

        # Set the expiry info for the item if required
        if timeout > 0:
            _timestamp = timestamp(offset=timeout)

            # Append the item name to prevent duplicate keys/timestamps
            self._data_expiry.append(f"{_timestamp}__{name}")

        self._lock.release()


    #
    # delete
    #
    def delete(
            self,
            name: str = ""
    ) -> None:
        '''
        Delete an item from the datastore

        Args:
            name (str): The name of the item to delete

        Returns:
            Any: The value of the item

        Raises:
            None
        '''
        if self.has(name):
            self._lock.acquire()
            del self._data[name]
            self._lock.release()


    #
    # list
    #
    def list(
            self,
            prefix: str = ""
    ) -> list:
        '''
        Return a list of keys in the datastore

        Args:
            prefix (str): Will try to match any keys beginning with this str.

        Returns:
            list: The list of items

        Raises:
            None
        '''
        self.maintenance()
        _item_list = list(self._data.keys())
 
        return self._filter_items(items=_item_list, prefix=prefix)


    ###########################################################################
    #
    # Export Functions
    #
    ###########################################################################
    #
    # export_to_json
    #
    def export_to_json(
            self,
            container: bool = True
    ) -> str:
        '''
        Export the data store to JSON

        Args:
            container (bool): If true, the export contains an outer layer:
                {
                    "value": { The export values },
                    "type": "dictionary"
                }

        Returns:
            str: The JSON string

        Raises:
            None
        '''
        # Convert to JSON
        self._logger.debug("Exporting Datastore to JSON")
        _export_data = {}

        # Transform the data to a straight dict
        _key_list = sorted(list(self._data.keys()))

        for _key in _key_list:
            # If dot names, handle the hierarchy
            if self._dot_names:
                _rest = _key
                _cur_level = _export_data

                while _rest:
                    # Split the name to get the first level (and the rest)
                    # If no dot in the name, then _rest will be empty
                    (_level, _, _rest) = _rest.partition(".")

                    if not _rest:
                        # This is the item name
                        _cur_level[_level] = self.get(_key)
                        continue

                    elif not _level in _cur_level:
                        _cur_level[_level] = {}

                    # Move on to the next level
                    _cur_level = _cur_level[_level]

            else:
                _export_data[_key] = self.get(_key)

        return to_json(
            data=_export_data,
            skip_invalid=True,
            container=container
        )


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
