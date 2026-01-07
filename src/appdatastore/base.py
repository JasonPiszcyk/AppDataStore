#!/usr/bin/env python3
'''
Datastore - Base Class

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
from multiprocessing import Lock

# System Modules
import crypto_tools
from crypto_tools.constants import ENCODE_METHOD
from applogging.logging import get_logger, init_console_logger

# Local app modules
from appcore.helpers import timestamp
from appcore.conversion import set_value, DataType, from_json, to_json

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
DEFAULT_LOGGER_NAME = "AppDataStore"


#
# Global Variables
#


###########################################################################
#
# DataStoreBaseClass Class Definition
#
###########################################################################
class DataStoreBaseClass():
    '''
    The base class to be use for all datastore classeses

    Attributes:
        dot_names (bool) [ReadOnly]: If true, dots in item names indicate a
            hierachy.
    '''

    #
    # __init__
    #
    def __init__(
            self,
            password: str = "",
            salt: bytes = b"",
            security: str = "high",
            dot_names: bool = False,
            logger_name: str = "",
            logger_level: str = "CRITICAL"
    ):
        '''
        Initialises the instance.

        Args:
            password: (str): Password used to derive the encryption key - A
                random password will be used if none provided
            salt: (bytes): Binary string containing the salt - A default
                salt will be used in none provided
            security (str): Determines the computation time of the key.  Must
                be one of "low", "medium", or "high"
            dot_names (bool): If True, use dot names to create a hierarchy of
                values for this data store.  If False, dots in names are
                treated as normal characters
            logger_name (str): The name of the logger to use.  If empty (or
                not a string) then a logger will be created to log to the
                console
            logger_level (str): If no logger name is provided, the created
                logger will be set to log event at or above this level (default
                = "CRITICAL")

        Returns:
            None

        Raises:
            None
        '''
        # Private Attributes
        self.__data: dict = {}
        self.__data_expiry: list = []
        self.__manual_expiry = True

        self.__lock = Lock()

        if not salt:
            salt = b"a%Z\xe9\xc3N\x96\x82\xc5|#e\xfd1b&"

        if isinstance(logger_name, str) and logger_name:
            self.__logger = get_logger(name=logger_name)

        else:
            self.__logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self.__logger.setLevel(level=logger_level)

        self.__logger.debug("Creating Encryption Key")
        self._salt, self._key = crypto_tools.fernet.derive_key(
            salt=salt, password=password, security=security
        )
        self.__logger.debug("Encryption Key has been created")

        self._dot_names = dot_names

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # dot_names
    #
    @property
    def dot_names(self) -> bool:
        ''' If True, dots in names are used to create hierarchy '''
        return self._dot_names


    ###########################################################################
    #
    # Maintenance Functions
    #
    ###########################################################################
    #
    # __item_maintenance
    #
    def __item_maintenance(self):
        '''
        Perform maintenance on items (such as expiry)

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.__logger.debug("Start item maintenance")

        if self.__manual_expiry:
            self.__logger.debug("Begin manual expiry processing")

            # Process the expiry list
            _now = timestamp()
            _sorted_expiry_list = sorted(self.__data_expiry)

            # Use the copy of __data_expiry list as it can change it during
            # processing
            for _entry in _sorted_expiry_list:
                # Extract the timestamp from the key
                _timestamp_str, _, _name = str(_entry).partition("__")
                _timestamp = set_value(_timestamp_str, DataType.INT, default=0)            

                # Stop processing if the timestamp is in the future
                if _now < _timestamp: break

                # Remove the entry (and the expiry record)
                self.__logger.info(f"Expiring entry: {self.__data[_name]}")
                self.__lock.acquire()
                if _name in self.__data: del self.__data[_name]
                self.__data_expiry.remove(_entry)
                self.__lock.release()

            self.__logger.debug("End manual expiry processing")

        self.__logger.debug("End item maintenance")


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
        self.__item_maintenance()
        return name in self.__data


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

        _value = self.__data[name]

        if decrypt:
            # Decrypt, convert from JSON
            _decrypted_value = self._decrypt(_value)
            _value = from_json(_decrypted_value)

        return _value


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

        self.__item_maintenance()

        # Check on dot names
        if self._dot_names:
            _keys = list(self.__data.keys())
            if not self._check_dot_name(keys=_keys, name=name):
                raise KeyError(
                    "Value cannot be stored in a intermediate dot level name"
                )

        # Encrypt the value if required
        if encrypt:
            # Convert to JSON, Encrypt
            _json_value = to_json(value)
            value = self._encrypt(_json_value)

        # Set the value
        self.__lock.acquire()
        self.__data[name] = value

        # Set the expiry info for the item if required
        if timeout > 0:
            _timestamp = timestamp(offset=timeout)

            # Append the item name to prevent duplicate keys/timestamps
            self.__data_expiry.append(f"{_timestamp}__{name}")

        self.__lock.release()


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
            self.__lock.acquire()
            del self.__data[name]
            self.__lock.release()


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
        self.__item_maintenance()
        _key_list = list(self.__data.keys())
 
        if not prefix:
            return _key_list
        
        _filtered_list = []
        for _entry in _key_list:
            if str(_entry).find(prefix, 0) == 0:
                _filtered_list.append(_entry)

        return _filtered_list


    ###########################################################################
    #
    # Storage Methods
    #
    ###########################################################################
    #
    # _encrypt
    #
    def _encrypt(
            self,
            value: str = ""
    ) -> str:
        '''
        Encrypt the value
            
        Args:
            value (str): A value to be encrypted. Should generally be a JSON
                string.
        
        Returns:
            string: The encrypted string

        Raises:
            TypeError
                When value is not of type str
        '''
        # Check the type of the value provided
        if not isinstance(value, str):
            raise TypeError(
                f"Cannot encrypt data type: {type(value)}"
            )

        _byte_data = value.encode(ENCODE_METHOD)
        _encrypted_string = crypto_tools.fernet.encrypt(
            data=_byte_data,
            key=self._key
        ).decode(ENCODE_METHOD)

        if not _encrypted_string:
            return ""
        else:
            return _encrypted_string


    #
    # _decrypt
    #
    def _decrypt(
            self,
            value: str = ""
    ) -> str:
        '''
        Decrypt the value
            
        Args:
            value (str): A value to be decrypted
        
        Returns:
            string: The decrypted string

        Raises:
            TypeError
                When value is not of type str
        '''
         # Check the type of the value provided
        if not isinstance(value, str):
            raise TypeError(
                f"Cannot decrypt data type: {type(value)}"
            )

        _byte_data = str(value).encode(ENCODE_METHOD)
        _decrypted_bytes = crypto_tools.fernet.decrypt(
            data=_byte_data,
            key=self._key
        )

        if _decrypted_bytes:
            try:
                return _decrypted_bytes.decode(ENCODE_METHOD)
            except:
                pass

        return ""


    ###########################################################################
    #
    # Dot Name Handling
    #
    ###########################################################################
    def _check_dot_name(
            self,
            keys: list = [],
            name: str = ""
    ) -> bool:
        '''
        Check the name to ensure a value isn't going to be stored in a
        sub-level name
            
        Args:
            keys (list): A list of keys in the datastore
            name (str): The name to check
        
        Returns:
            bool: True if the name is OK, False otherwise

        Raises:
            None
        '''
        assert isinstance(keys, list), "Keys must be a list of key names"
        assert name, "A name is required to check"

        # Go through the whole list looking for the name
        for _key in sorted(keys):
            if name == _key: continue

            # Look for a name trying to add a branch where a value is stored
            if str(name).find(f"{_key}.") == 0:
                return False

            # Look for a name trying to add a value where a branch is
            if str(_key).find(f"{name}.") == 0:
                return False

        return True


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
        self.__logger.debug("Exporting Datastore to JSON")
        _export_data = {}

        # Transform the data to a straight dict
        _key_list = sorted(list(self.__data.keys()))

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
