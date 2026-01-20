#!/usr/bin/env python3
'''
Datastore - Shared Mem

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
from appcore.conversion import to_json

# Local app modules
from appdatastore.base import DataStoreBaseClass
from appdatastore.shared_mem_item import (
    DataStoreSharedMemItem,
    SHARED_ITEM_NAME_MAX
)
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
DEFAULT_SHARED_MEM_NAME = "AppDS_SHM"
DEFAULT_INDEX_SIZE = 16384      # 16K

INDEX_SUFFIX = "I"
EXPIRY_DICT_SUFFIX = "E"

SHARED_MEM_NAME_MAX = SHARED_ITEM_NAME_MAX - len(INDEX_SUFFIX)

#
# Global Variables
#


###########################################################################
#
# DataStoreSharedMem Class Definition
#
###########################################################################
class DataStoreSharedMem(DataStoreBaseClass):
    '''
    Class to describe the shared memory datastore.

    The data is stored in a dictionary that is made available via shared memory

    Attributes:
        name (str) [ReadOnly]: Name of the shared memory segment
        index_size (int) [ReadOnly]: Size of the index shared memory segment
    '''
    #
    # __init__
    #
    def __init__(
            self,
            *args,
            name: str = "",
            encrypt_index: bool = False,
            index_size: int = DEFAULT_INDEX_SIZE,
            delete_on_cleanup: bool = False,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            name (str): Name of the data store
            encrypt_index (bool): If true, encrypt the index.  Password must
                be provided or a random password will be used and no other
                processes can access the shared memory datastore
            index_size (int): The size for the index segment in shared memory.
                The default should be reasonable, but if exceeded will raise
                a MemoryError.
            delete_on_cleanup (bool): When True, the 'cleanup' method (and
                the __del__ function) will close and unlink any managed
                shared memory segments.  When False (the default) the managed
                segment will be closed but not unlinked.
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            AssertionError
                When name is not a string or is greater than
                    SHARED_MEM_NAME_MAX characters
                When encrypt_index is not a bool
            TypeError
                When share memory creation fails
        '''
        assert isinstance(name, str), "name must be a string"
        assert len(name) <= SHARED_MEM_NAME_MAX, (
            f"name can be at most {SHARED_MEM_NAME_MAX} characters"
        )
        assert isinstance(encrypt_index, bool), "encrypt_index must be a bool"
        assert isinstance(index_size, int), "index_size must be an int"
        assert isinstance(delete_on_cleanup, bool), (
            "delete_on_cleanup must be a bool"
        )

        super().__init__(*args, **kwargs)

        # Extract the logging info from kwargs (if it is set)
        if "logger_name" in kwargs:
            self._logger_name = kwargs["logger_name"]
        else:
            self._logger_name = ""

        if "logger_level" in kwargs:
            self._logger_level = kwargs["logger_level"]
        else:
            self._logger_level = "CRITICAL"

        # Private Attributes
        self._name = name or DEFAULT_SHARED_MEM_NAME
        self._encrypt_index = encrypt_index
        self._index_name = f"{name}{INDEX_SUFFIX}"
        self._expiry_dict_name = f"{name}{EXPIRY_DICT_SUFFIX}"

        if index_size > DEFAULT_INDEX_SIZE:
            _index_size = index_size
        else:
            _index_size = DEFAULT_INDEX_SIZE

        self._delete_on_cleanup = delete_on_cleanup

        # Always store values serialised (Shared mem stores bytes)
        self._store_serialised = True
        self._serialisation_method = SerialisationType.PICKLE

        self._index_shm = DataStoreSharedMemItem(
            name=self._index_name,
            size=_index_size,
            logger_name=self._logger_name,
            logger_level=self._logger_level
        )
        self._index_shm.set(
            value=self._encode(value=[], encrypt=self._encrypt_index)
        )

        self._expiry_dict_shm = DataStoreSharedMemItem(
            name=self._expiry_dict_name,
            size=_index_size,
            logger_name=self._logger_name,
            logger_level=self._logger_level
        )
        self._expiry_dict_shm.set(
            value=self._encode(value={}, encrypt=self._encrypt_index)
        )

        # Attributes


    #
    # __del__
    #
    def __del__(self):
        '''
        Called when instance is destroyed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.cleanup()


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # name
    #
    @property
    def name(self) -> str:
        ''' The name of the shared memory segment '''
        return self._name


    #
    # index_size
    #
    @property
    def index_size(self) -> int:
        ''' The size of the index '''
        assert isinstance(self._index_shm, DataStoreSharedMemItem), (
            "shared memory segment for index cannot be found"
        )

        return self._index_shm.size


    ###########################################################################
    #
    # Indexing Functions
    #
    ###########################################################################
    #
    # _get_index
    #
    def _get_index(self) -> list:
        '''
        Get the shared index

        Args:
            None

        Returns:
            list: The list of shared memory segment names

        Raises:
            AssertionError
                When the index memory segment can't be found
            TypeError
                When the index is not a list
        '''
        assert isinstance(self._index_shm, DataStoreSharedMemItem), (
            "shared memory segment for index cannot be found"
        )

        _index_list = self._decode(
            value=self._index_shm.get(),
            decrypt=self._encrypt_index
        )

        if not isinstance(_index_list, list):
            raise TypeError("index is corrupt")

        return _index_list


    #
    # _add_to_index
    #
    def _add_to_index(self, name:str = ""):
        '''
        Add a name to the shared index.

        Args:
            name (str): Name of the item to add

        Returns:
            None

        Raises:
            AssertionError
                When the index memory segment can't be found
                When name is empty or not a string
            TypeError
                When the index is not a list
        '''
        assert isinstance(self._index_shm, DataStoreSharedMemItem), (
            "shared memory segment for index cannot be found"
        )

        assert isinstance(name, str), "name must be a string"
        assert name, "name must contain a value"

        # The function to perform the update
        def _add_item_to_index(val: bytes=b"") -> bytes:
            _index_list = self._decode(value=val, decrypt=self._encrypt_index)

            if not isinstance(_index_list, list):
                raise TypeError("index is corrupt")

            if not name in _index_list: _index_list.append(name)

            return self._encode(value=_index_list, encrypt=self._encrypt_index)

        # Perform the update
        self._index_shm.update(func=_add_item_to_index)


    #
    # _del_from_index
    #
    def _del_from_index(self, name:str = ""):
        '''
        Remove a name from the shared index

        Args:
            name (str): Name of the item to remove

        Returns:
            None

        Raises:
            AssertionError
                When the index memory segment can't be found
                When name is empty or not a string
            TypeError
                When the index is not a list
        '''
        assert isinstance(self._index_shm, DataStoreSharedMemItem), (
            "shared memory segment for index cannot be found"
        )

        assert isinstance(name, str), "name must be a string"
        assert name, "name must contain a value"

        # The function to perform the update
        def _remove_item_from_index(val: bytes=b"") -> bytes:
            _index_list = self._decode(value=val, decrypt=self._encrypt_index)

            if not isinstance(_index_list, list):
                raise TypeError("index is corrupt")

            if name in _index_list: _index_list.remove(name)

            return self._encode(value=_index_list, encrypt=self._encrypt_index)

        # Perform the update
        self._index_shm.update(func=_remove_item_from_index)


    ###########################################################################
    #
    # Expiry Dict Functions
    #
    ###########################################################################
    #
    # _get_expiry_dict
    #
    def _get_expiry_dict(self) -> dict:
        '''
        Get the expiry dict

        Args:
            None

        Returns:
            dict: The dict on entries with timeouts

        Raises:
            AssertionError
                When the expiry dict memory segment can't be found
            TypeError
                When the expiry dict is not a dict
        '''
        assert isinstance(self._expiry_dict_shm, DataStoreSharedMemItem), (
            "shared memory segment for expiry dict cannot be found"
        )

        _expiry_dict = self._decode(
            value=self._expiry_dict_shm.get(),
            decrypt=self._encrypt_index
        )

        if not isinstance(_expiry_dict, dict):
            raise TypeError("expiry dict is corrupt")

        return _expiry_dict


    #
    # _add_to_expiry_dict
    #
    def _add_to_expiry_dict(self, name:str = "", timestamp: int = 0):
        '''
        Add an entry to the expiry dict

        Args:
            name (str): Name of the item to add
            timestamp (int): Timestamp indicating when the item should be
                expired

        Returns:
            None

        Raises:
            AssertionError
                When the expiry dict memory segment can't be found
                When name is empty or not a string
                When timestamp is not zero or a positive integer
            TypeError
                When the index is not a list
        '''
        assert isinstance(self._expiry_dict_shm, DataStoreSharedMemItem), (
            "shared memory segment for expiry dict cannot be found"
        )

        assert isinstance(name, str), "name must be a string"
        assert name, "name must contain a value"

        assert isinstance(timestamp, int), "timestamp value must be an integer"
        assert timestamp >= 0, "timestamp value must be a postive integer"

        # The function to perform the update
        def _add_item_to_expiry_dict(val: bytes=b"") -> bytes:
            _expiry_dict = self._decode(value=val, decrypt=self._encrypt_index)

            if not isinstance(_expiry_dict, dict):
                raise TypeError("expiry dict is corrupt")

            _expiry_dict[name] = timestamp

            return self._encode(
                value=_expiry_dict,
                encrypt=self._encrypt_index
            )

        # Perform the update
        self._expiry_dict_shm.update(func=_add_item_to_expiry_dict)


    #
    # _del_from_expiry_dict
    #
    def _del_from_expiry_dict(self, name:str = ""):
        '''
        Remove an entry from the expiry dict

        Args:
            name (str): Name of the item to add

        Returns:
            None

        Raises:
            AssertionError
                When the expiry dict memory segment can't be found
                When name is empty or not a string
                When timestamp is not zero or a positive integer
            TypeError
                When the index is not a list
        '''
        assert isinstance(self._expiry_dict_shm, DataStoreSharedMemItem), (
            "shared memory segment for expiry dict cannot be found"
        )

        assert isinstance(name, str), "name must be a string"
        assert name, "name must contain a value"

        # The function to perform the update
        def _remove_item_from_expiry_dict(val: bytes=b"") -> bytes:
            _expiry_dict = self._decode(value=val, decrypt=self._encrypt_index)

            if not isinstance(_expiry_dict, dict):
                raise TypeError("expiry dict is corrupt")

            try:
                del _expiry_dict[name]
            except:
                pass

            return self._encode(
                value=_expiry_dict,
                encrypt=self._encrypt_index
            )

        # Perform the update
        self._expiry_dict_shm.update(func=_remove_item_from_expiry_dict)


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

            # Process the expiry dict
            _expiry_dict = self._get_expiry_dict()

            _now = timestamp()

            for _item, _expiry in _expiry_dict.items():
                # Stop processing if the timestamp is in the future
                if _now > _expiry:
                    # Remove the item (and the expiry record)
                    self._logger.info(f"Expiring entry: {_item}")

                    # Delete the named segment
                    _shm = DataStoreSharedMemItem(name=_item)
                    _shm.delete()

                    # Delete the expiry dict entry
                    self._del_from_expiry_dict(name=_item)

                    # Delete the index entry
                    self._del_from_index(name=_item)

            self._logger.debug("End manual expiry processing")

        self._logger.debug("End item maintenance")


    #
    # cleanup
    #
    def cleanup(self):
        '''
        Close and unlink all of the shared memory segments we know about

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self._logger.debug("Start shared memory cleanup")

        # Clean up the expiry dict
        try:
            if self._delete_on_cleanup:
                self._expiry_dict_shm.delete()
            else:
                self._expiry_dict_shm.close()

        except:
            # May already be closed/deleted
            pass

        # If deleting, clean up all entries in the index
        if self._delete_on_cleanup:
            try:
                _index = self._get_index()
            except:
                _index = []

            # Go through the index and close/unlink all segments
            for _name in _index:
                # Delete the named segment
                _shm = DataStoreSharedMemItem(name=_name)
                _shm.delete()

        # Clean up the index segment
        try:
            if self._delete_on_cleanup:
                self._index_shm.delete()
            else:
                self._index_shm.close()

        except:
            # May already be closed/deleted
            pass

        self._logger.debug("End shared memory cleanup")


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
            AssertionError
                When cannot access shared memory
                When the shared memory buffer is not accessible
        '''
        self.maintenance()

        # Get the index
        _index = self._get_index()

        # Get the id of the mem segment that holds the index
        return name in _index


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
        if not self.has(name=name): return default

        _item = DataStoreSharedMemItem(name=name)
        _value = _item.get()
        _item.close()

        return self._decode(value=_value, decrypt=decrypt)


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
        Set a value for an item (Datastore mode)

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
            _keys = self._get_index()
            if not self._check_dot_name(keys=_keys, name=name):
                raise KeyError(
                    "Value cannot be stored in a intermediate dot level name"
                )

        # Update the index
        self._add_to_index(name=name)

        # Encode the value for storage (possibly encrypting) and store it
        _value_to_store = self._encode(value=value, encrypt=encrypt)
        _item = DataStoreSharedMemItem(name=name)
        _item.set(value=_value_to_store)
        _item.close()

        # If timeout is provided, add to expiry dict
        if timeout > 0:
            self._add_to_expiry_dict(
                name=name,
                timestamp=timestamp(offset=timeout)
            )


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
            # Remove the item
            _item = DataStoreSharedMemItem(name=name)
            _item.delete()

            # Remove any expiry dict entry
            self._del_from_expiry_dict(name=name)

            # Remove the index entry
            self._del_from_index(name=name)


    #
    # list
    #
    def list(
            self,
            prefix: str = ""
    ) -> list:
        '''
        Return a list of items in the datastore

        Args:
            prefix (str): Will try to match any items beginning with this str.

        Returns:
            list: The list of items

        Raises:
            None
        '''
        self.maintenance()
        _item_list = self._get_index()
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
        _item_list = sorted(self._get_index())

        for _item_name in _item_list:
            # Get the share mem item
            _item = DataStoreSharedMemItem(name=_item_name)

            # If dot names, handle the hierarchy
            if self._dot_names:
                _rest = str(_item_name)
                _cur_level = _export_data

                while _rest:
                    # Split the name to get the first level (and the rest)
                    # If no dot in the name, then _rest will be empty
                    (_level, _, _rest) = _rest.partition(".")

                    if not _rest:
                        # This is the item name
                        _cur_level[_level] = _item.get()
                        continue

                    elif not _level in _cur_level:
                        _cur_level[_level] = {}

                    # Move on to the next level
                    _cur_level = _cur_level[_level]

            else:
                _export_data[_item] = _item.get()

            # Close the item
            _item.close()

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
