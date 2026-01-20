#!/usr/bin/env python3
'''
Datastore - Shared Mem - Single Item

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
import sys
import time
from multiprocessing.shared_memory import SharedMemory

# Local app modules
from appdatastore.base import DEFAULT_LOGGER_NAME
from applogging.logging import get_logger, init_console_logger

# Imports for python variable type hints
from typing import Callable


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
LOCK_RETRY = 0.2
LOCK_WAIT_TIMEOUT = 30.0

# _SHM_SAFE_NAME_LENGTH in multiprocessing.shared_memory = 14
LOCK_NAME_SUFFIX = "L"
SHARED_ITEM_NAME_MAX = 14 - len(LOCK_NAME_SUFFIX)

#
# Global Variables
#
if sys.version_info < (3, 13):
    TrackArgs = {}
else:
    TrackArgs = { "track": False }

###########################################################################
#
# Utility Functions
#
###########################################################################
#
# shared_memory_exists
#
def shared_memory_exists(name: str = "") -> bool:
    '''
    Check if the named shared memory segment exists

    Args:
        name (str): Name of the shared memory segment to check

    Returns:
        bool: True is segment exists, False otherwise

    Raises:
        None
    '''
    try:
        _shm = SharedMemory(name=name, create=False, **TrackArgs)
        _shm.close()
        return True

    except FileNotFoundError:
        pass

    return False


###########################################################################
#
# DataStoreSharedMemItem Class Definition
#
###########################################################################
class DataStoreSharedMemItem():
    '''
    Class to to store a single item in shared memory

    Attributes:
        name (str) [ReadOnly]: Name of the item
        size (int) [ReadOnly]: The size of the shared memory segment
    '''
    #
    # __init__
    #
    def __init__(
            self,
            name: str = "",
            size: int = 1,
            logger_name: str = "",
            logger_level: str = "CRITICAL"
    ):
        '''
        Initialises the instance.

        Args:
            name (str): Name of the item being stored
            size (int): Size of the shared memeory segment to request
            logger_name (str): The name of the logger to use.  If empty (or
                not a string) then a logger will be created to log to the
                console
            logger_level (str): If no logger name is provided, the created
                logger will be set to log events at or above this level (default
                = "CRITICAL")

        Returns:
            None

        Raises:
            AssertionError
                When name is not a string, is empty, or is greater than
                    SHARED_ITEM_NAME_MAX characters
            TypeError
                When share memory creation fails
        '''
        assert isinstance(name, str), "name must be a string"
        assert name, "name cannot be empty"
        assert len(name) <= SHARED_ITEM_NAME_MAX, (
            f"name can be at most {SHARED_ITEM_NAME_MAX} characters"
        )

        # Private Attributes
        self._name = name
        self._shm = None
        self._lock_name = f"{name}{LOCK_NAME_SUFFIX}"
        self._lock = None

        if isinstance(logger_name, str) and logger_name:
            self._logger = get_logger(name=logger_name)

        else:
            self._logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self._logger.setLevel(level=logger_level)

        # Attributes

        # Open the shared mem segment
        self.open(size=size)


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
        # Cleanup the item (just close it, don't unlink it)
        if isinstance(self._shm, SharedMemory):
            try:
                self._shm.close()
            except:
                pass

        # Cleanup the lock if it is set (should be unlinked)
        if isinstance(self._lock, SharedMemory):
            try:
                self._lock.unlink()
                self._lock.close()
            except:
                pass


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
        ''' The name of the item '''
        return self._name


    #
    # size
    #
    @property
    def size(self) -> int:
        ''' The size of the shared memory segment '''
        assert isinstance(self._shm, SharedMemory), (
            "shared memory segment for item cannot be found"
        )

        return self._shm.size


    ###########################################################################
    #
    # Locking Functions
    #
    ###########################################################################
    #
    # _acquire_lock
    #
    def _acquire_lock(self):
        '''
        Acquire the lock for shared memory actions

        This done by creating a shared memory segment with the lock name.  Only
        one process can create shared memory, so this will fail for other
        processes attempting to acquire the lock

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError
                When lock has already been acquired
            SystemError
                When lock is invalid
            TimeOutError
                When lock cannot be acquired within timeout
        '''
        _lock_acquired = False
        _time_waited = 0.0

        if isinstance(self._lock, SharedMemory):
            if self._lock.name == self._lock_name:
                raise RuntimeError("lock has already been acquired")
            else:
                raise SystemError("invalid lock")

        while not _lock_acquired:
            # If segment already exists then another process has the lock
            try:
                self._lock = SharedMemory(
                    name=self._lock_name,
                    create=True,
                    size=1,
                    **TrackArgs
                )
                _lock_acquired = True

            except FileExistsError:
                pass

            if not _lock_acquired:
                time.sleep(LOCK_RETRY)
                _time_waited += LOCK_RETRY

                if _time_waited >= LOCK_WAIT_TIMEOUT:
                    raise TimeoutError(
                        "timeout waiting for shared memory lock"
                    )


    #
    # _release_lock
    #
    def _release_lock(self):
        '''
        Release the lock

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError
                When lock has not been acquired
            SystemError
                When lock is invalid
        '''
        if not isinstance(self._lock, SharedMemory):
            raise RuntimeError("lock has not been acquired")

        if self._lock.name != self._lock_name:
            raise SystemError("invalid lock")

        # Release the lock
        self._lock.unlink()
        self._lock.close()
        self._lock = None


    ###########################################################################
    #
    # Shared Mem Connection Functions
    #
    ###########################################################################
    #
    # open
    #
    def open(self, size: int = 1):
        '''
        Connect to a shared memory segment (if is has been closed or unlinked)

        Args:
            size (int): Size of the shared memeory segment to request

        Returns:
            None

        Raises:
            AssertionError
                When size is not a integer > 0
                When named shared memory has already been opened
        '''
        assert isinstance(size, int), "size must be an integer"
        assert size > 0, "size must be greater than 0"

        assert not self._shm, (
            "shared memory segment already opened"
        )

        _create_shm = False
        try:
            self._shm = SharedMemory(
                name=self._name,
                create=False,
                **TrackArgs
            )

        except FileNotFoundError:
            _create_shm = True

        if _create_shm:
            self._shm = SharedMemory(
                name=self._name,
                create=True,
                size=size,
                **TrackArgs
            )


    #
    # close
    #
    def close(self):
        '''
        Disconnect from the shared memory segment

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError
                When shm is not a valid shared memory segment
        '''
        assert isinstance(self._shm, SharedMemory), (
            "shared memory segment for item cannot be found"
        )

        try:
            self._shm.close()
        except FileNotFoundError:
            pass

        self._shm = None


    #
    # delete
    #
    def delete(self):
        '''
        Disconnect from the shared memory segment, and delete it

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError
                When shm is not a valid shared memory segment
        '''
        assert isinstance(self._shm, SharedMemory), (
            "shared memory segment for item cannot be found"
        )

        try:
            self._shm.unlink()
            self._shm.close()
        except FileNotFoundError:
            pass

        self._shm = None


    ###########################################################################
    #
    # Data Access
    #
    ###########################################################################
    #
    # get
    #
    def get(self) -> bytes:
        '''
        Get the item value

        Args:
            None

        Returns:
            bytes: The value stored in the shared memory segment

        Raises:
            AssertionError
                When shm is not a valid shared memory segment
                When the shared memory buffer is invalid
        '''
        assert isinstance(self._shm, SharedMemory), "shm must be SharedMemory"
        assert isinstance(self._shm.buf, memoryview), (
            "unable to process shared memory configuration"
        )

        return self._shm.buf.tobytes()


    #
    # set
    #
    def set(self, value: bytes = b"") -> None:
        '''
        Set the item value

        Args:
            value (bytes): Value to set the item to

        Returns:
            None

        Raises:
            AssertionError
                When shm is not a valid shared memory segment
                When the shared memory buffer is invalid
                When value is not in bytes format
            ValueError
                When the size of the value is too large for the segment
        '''
        assert isinstance(self._shm, SharedMemory), "shm must be SharedMemory"
        assert isinstance(self._shm.buf, memoryview), (
            "unable to process shared memory configuration"
        )

        assert isinstance(value, bytes), "value must be in byte format"

        _val_size = len(value)
        if _val_size > self._shm.size:
            raise ValueError("value is too big for shared memory segment")

        # Write to the segment and zero out the rest of it
        self._acquire_lock()

        self._shm.buf[:_val_size] = value
        if _val_size < self._shm.size:
            self._shm.buf[_val_size:] = b'\x00' * (self._shm.size - _val_size)

        self._release_lock()


    #
    # update
    #
    def update(self, func: Callable | None = None) -> None:
        '''
        Update an item value by reading value, applying some change, then
        setting the value

        Args:
            func (Callable): Func to transform the stored value to the new
                value to be stored. Must accept the current value as bytes
                and return the new value as bytes

        Returns:
            None

        Raises:
            AssertionError
                When shm is not a valid shared memory segment
                When the shared memory buffer is invalid
                When func is not callable
                When the function does not return a value in bytes format
        '''
        assert isinstance(self._shm, SharedMemory), "shm must be SharedMemory"
        assert isinstance(self._shm.buf, memoryview), (
            "unable to process shared memory configuration"
        )

        assert callable(func), "func must be callable"

        # Get the lock so no-one can change things while this happens
        self._acquire_lock()

        _stored_value = self._shm.buf.tobytes()

        # Call the function to modify the value
        _new_value = func(_stored_value)
        assert isinstance(_new_value, bytes), "value must be in byte format"

        _val_size = len(_new_value)
        if _val_size > self._shm.size:
            raise ValueError("new value is too big for shared memory segment")

        # Write to the segment and zero out the rest of it
        self._shm.buf[:_val_size] = _new_value
        if _val_size < self._shm.size:
            self._shm.buf[_val_size:] = b'\x00' * (self._shm.size - _val_size)

        self._release_lock()


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
