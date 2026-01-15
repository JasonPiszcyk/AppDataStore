#!/usr/bin/env python3
'''
PyTest - Test of Shared Memory Items

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
# Shared variables, constants, etc
from tests.constants import *

# System Modules
import pytest
import time
from multiprocessing import Process

from appcore.conversion import to_pickle, from_pickle

# Local app modules
from test_base import TestBase
from appdatastore.shared_mem_item import (
    DataStoreSharedMemItem,
    shared_memory_exists,
    LOCK_WAIT_TIMEOUT
)

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
WAIT_TIMEOUT = 10

DATA_SET = {
    "String": { "type": str, "value": "A string to be stored in shared mem" },
    "Integer": { "type": int, "value": 100 },
    "Dict": { 
        "type": dict,
        "value": {
            "value_string": "a string stored in the dict",
            "value_int": 100
        }
    },
    "List": {
        "type": list,
        "value": [ "string in list", 8, "another string" ]
    }
}

#
# Global Variables
#


###########################################################################
#
# Tests to run in the child process
#
###########################################################################
#
# _run_child
def _run_child(target=None, kwargs={} ):
    _process = Process(target=target, kwargs=kwargs)
    _process.start()
    _process.join()


#
# _child_shared_mem_exists
#
def _child_shared_mem_exists(name=""):
    # The shared memory segment should exist
    assert shared_memory_exists(name=name)


#
# _child_shared_mem_missing
#
def _child_shared_mem_missing(name=""):
    # The shared memory segment should NOT exist
    assert not shared_memory_exists(name=name)


#
# _child_shared_mem_empty
#
def _child_shared_mem_empty(name=""):
    # Attach to the shared mem and ensure the value hasn't been set
    _child_shm = DataStoreSharedMemItem(name=name)
    _size = _child_shm.size
    _val = _child_shm.get()
    _child_shm.close()

    assert _val == b'\x00' * _size


#
# _child_shared_mem_get
#
def _child_shared_mem_get(name="", value=None, datatype=str):
    # Attach to the shared mem and get a value
    _child_shm = DataStoreSharedMemItem(name=name)
    _pickle = _child_shm.get()
    _child_shm.close()

    _val = from_pickle(data=_pickle)
    assert isinstance(_val, datatype)
    assert _val == value


#
# _child_shared_mem_fail_lock_timeout
#
def _child_shared_mem_fail_lock_timeout(name=""):
    # Attach to the shared mem and try to set a value
    _child_shm = DataStoreSharedMemItem(name=name)

    time.sleep(2)

    # Get the same data to write back to memory
    _pickle = _child_shm.get()

    with pytest.raises(TimeoutError):
        _child_shm.set(value=_pickle)


###########################################################################
#
# The tests...
#
###########################################################################
#
# Shared Mem Item
#
class Test_Shared_Mem_Items(TestBase):
    '''
    Test Class - Shared Mem Item

    Attributes:
        None
    '''
    #
    # Basic Test - Create/Set/Read/Delete Meme
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_basic(self, name):
        '''
        Basic test

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Pickle the value for storage
        _pickle = to_pickle(data=DATA_SET[name]["value"])
        _size = len(_pickle)

        # The shared memory segment should not exist
        assert not shared_memory_exists(name=name)
        _run_child(target=_child_shared_mem_missing, kwargs={ "name": name })

        # Create the Item in this process
        _shm = DataStoreSharedMemItem(name=name, size=_size)

        # Check the memory exists, and get the value which should be empty
        assert shared_memory_exists(name=name)
        assert _shm.get() == b'\x00' * _shm.size
        _run_child(target=_child_shared_mem_exists, kwargs={ "name": name })
        _run_child(target=_child_shared_mem_empty, kwargs={ "name": name })

        # Add a value
        _shm.set(value=_pickle)

        # Get value
        _get_val = from_pickle(data=_shm.get())
        assert isinstance(_get_val, DATA_SET[name]["type"])
        assert _get_val == DATA_SET[name]["value"]
        _run_child(target=_child_shared_mem_get, kwargs={
                "name": name,
                "value": DATA_SET[name]["value"],
                "datatype": DATA_SET[name]["type"]
            }
        )

        # Delete Mem
        _shm.delete()

        # The shared memory segment should not exist
        assert not shared_memory_exists(name=name)
        _run_child(target=_child_shared_mem_missing, kwargs={ "name": name })


    #
    # Test updating
    #
    def test_update(self):
        '''
        Test the item update functionality

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _name = "test_update"
        _value = "StringPrefix"
        _add_to_str = " extra stuff"
        _new_value = f"{_value}{_add_to_str}"

        # Pickle the value for storage
        _pickle = to_pickle(data=_value)
        _size = len(_pickle)

        # Create Shared mem and add value
        _shm = DataStoreSharedMemItem(name=_name, size=_size)
        _shm.set(value=_pickle)

        # Confirm value OK
        _get_val = from_pickle(data=_shm.get())
        assert _get_val == _value

        # Update the value
        def _update(old_bytes):
            _old_value = from_pickle(data=old_bytes)
            return to_pickle(f"{_old_value}{_add_to_str}")

        _shm.update(func=_update)

        # Confirm value has changed
        _get_val = from_pickle(data=_shm.get())
        assert _get_val == _new_value

        # Delete Mem
        _shm.delete()

        # The shared memory segment should not exist
        assert not shared_memory_exists(name=_name)


    #
    # Test item locks
    #
    def test_item_locks(self):
        '''
        Test the locking is working

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _name = "test_locks"
        _value = "StringPrefix"
        _add_to_str = " extra stuff"
        _new_value = f"{_value}{_add_to_str}"

        # Pickle the value for storage
        _pickle = to_pickle(data=_value)
        _size = len(_pickle)

        # Create Shared mem and add value
        _shm = DataStoreSharedMemItem(name=_name, size=_size)
        _shm.set(value=_pickle)

        # Confirm value OK
        _get_val = from_pickle(data=_shm.get())
        assert _get_val == _value

        # Update the value (delaying for longer than lock timeout)
        def _update(old_bytes):
            _old_value = from_pickle(data=old_bytes)
            time.sleep(LOCK_WAIT_TIMEOUT + 5)
            return to_pickle(f"{_old_value}{_add_to_str}")

        # Start a child process to try and write and expect to fail
        # dalys the write for 2 seconds to allow update process to begin
        _run_child(
            target=_child_shared_mem_fail_lock_timeout,
            kwargs={ "name": _name }
        )

        _shm.update(func=_update)

        # Confirm value has changed
        _get_val = from_pickle(data=_shm.get())
        assert _get_val == _new_value

        # Delete Mem
        _shm.delete()

        # The shared memory segment should not exist
        assert not shared_memory_exists(name=_name)


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

