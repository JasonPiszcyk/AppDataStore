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
from appcore.conversion import to_json, from_json, to_pickle, from_pickle
from appdatastore.typing import SerialisationType

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
                logger will be set to log events at or above this level (default
                = "CRITICAL")

        Returns:
            None

        Raises:
            None
        '''
        # Private Attributes
        self._data: dict = {}
        self._data_expiry: list = []
        self._manual_expiry = True
        self._store_serialised = False
        self._serialisation_method = SerialisationType.JSON

        self._lock = Lock()

        if not salt:
            salt = b"a%Z\xe9\xc3N\x96\x82\xc5|#e\xfd1b&"

        if isinstance(logger_name, str) and logger_name:
            self._logger = get_logger(name=logger_name)

        else:
            self._logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self._logger.setLevel(level=logger_level)

        self._logger.debug("Creating Encryption Key")
        self._salt, self._key = crypto_tools.fernet.derive_key(
            salt=salt,
            password=password,
            security=security
        )
        self._logger.debug("Encryption Key has been created")

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
    # Processing Methods
    #
    ###########################################################################
    def _filter_keys(
            self,
            keys: list = [],
            prefix: str = ""
    ) -> list:
        '''
        Filter the list of keys via the prefix

        Args:
            keys (list): A list of keys to be filtered
            prefix (str): Match any keys beginning with this str
        
        Returns:
            list: The list filtered by the prefix

        Raises:
            AssertionError
                when keys is not a list
                when prefix is not a string
        '''
        assert isinstance(keys, list), "keys must be a list"
        assert isinstance(prefix, str), "prefix must be a string"

        if not prefix:
            return keys.copy()
        
        _filtered_list = []
        for _entry in keys:
            if str(_entry).find(prefix, 0) == 0:
                _filtered_list.append(_entry)

        return _filtered_list


    ###########################################################################
    #
    # Storage Methods
    #
    ###########################################################################
    #
    # _encode
    #
    def _encode(
            self,
            value: Any = None,
            encrypt: bool = False
    ) -> Any:
        '''
        Encode the value for storage, possibly encrypting it
            
        Args:
            value (str): A value to be encoded
            encrypt (bool): whether or not to encrypt the value
        
        Returns:
            Any: The value in the format to be stored

        Raises:
            None
        '''
        if encrypt or self._store_serialised:
            if self._serialisation_method == SerialisationType.JSON:
                _value_to_store = to_json(data=value)
                _byte_data = _value_to_store.encode(ENCODE_METHOD)

            elif self._serialisation_method == SerialisationType.PICKLE:
                _value_to_store = to_pickle(data=value)
                _byte_data = _value_to_store

            else:
                raise AssertionError("Invalid serialisation type")

            if encrypt:
                _value_to_store = crypto_tools.fernet.encrypt(
                    data=_byte_data,
                    key=self._key
                ).decode(ENCODE_METHOD)

        else:
            _value_to_store = value

        return _value_to_store


    #
    # _decode
    #
    def _decode(
            self,
            value: Any = None,
            decrypt: bool = False
    ) -> Any:
        '''
        Decrypt the value
            
        Args:
            value (Any): A value to be decoded
            decrypt (bool): whether or not the value needs to be decrypted
        
        Returns:
            Any: The decoded value

        Raises:
            AssertionError
                When serilisation is not of type SerialisationType
            TypeError
                When value is not of type str if decrypting or JSON
        '''
        _decoded_val = None

        # Check the type of the value provided

        if decrypt or self._store_serialised:
            if decrypt:
                if not isinstance(value, str):
                    raise TypeError(
                        f"Cannot decrypt data type: {type(value)}"
                    )

                _serialised_bytes = crypto_tools.fernet.decrypt(
                    data=str(value).encode(ENCODE_METHOD),
                    key=self._key
                )

            else:
                _serialised_bytes = value

            # Deserialise the data
            if self._serialisation_method == SerialisationType.JSON:
                _decoded_val = from_json(
                    data=_serialised_bytes.decode(ENCODE_METHOD)
                )

            elif self._serialisation_method == SerialisationType.PICKLE:
                _decoded_val = from_pickle(data=value)

            else:
                raise AssertionError("Invalid serialisation type")

        else:
            _decoded_val = value

        return _decoded_val


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
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass
