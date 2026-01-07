#!/usr/bin/env python3
'''
PyTest - Base class for test functions

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
# Base Class for tests
#
###########################################################################
#
# Base Class
#
class TestBase():
    '''
    Base Test Class

    Attributes:
        None
    '''
    #
    # check an item has NOT been set
    #
    def _assert_not_set(
            self,
            ds: DataStoreBaseClass | None,
            name: str = ""
    ):
        '''
        Assert that the item does not exist

        Args:
            ds (DataStoreBaseClass): The datastore to operate on
            name (str): Name of the item

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)
        assert isinstance(name, str)
        assert name

        # Ensure the item does not exist
        assert not ds.has(name=name)

        # Try to get the item (should return None)
        assert not ds.get(name=name)

        # Try to get the item (should return a default string)
        assert ds.get(
            name=name,
            default=DEFAULT_STR_VALUE
        ) == DEFAULT_STR_VALUE


    #
    # check an item has been set
    #
    def _assert_set(
            self,
            ds: DataStoreBaseClass | None,
            name: str = "",
            value: Any = None
    ):
        '''
        Assert that the item has been set

        Args:
            ds (DataStoreBaseClass): The datastore to operate on
            name (str): Name of the item
            value (Any): Value to set the item to

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)
        assert isinstance(name, str)
        assert name

        # Ensure the item exists
        assert ds.has(name=name)

        # Try to get the item (should return the value)
        assert ds.get(name=name) == value

        # Try to get the item (should return the value)
        assert ds.get(
            name=name,
            default=DEFAULT_STR_VALUE
        ) == value


    #
    # check an item has been set (value is encrypted)
    #
    def _assert_set_enc(
            self,
            ds: DataStoreBaseClass | None,
            name: str = "",
            value: Any = None
    ):
        '''
        Assert that the item has been set

        Args:
            ds (DataStoreBaseClass): The datastore to operate on
            name (str): Name of the item
            value (Any): Value to set the item to

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)
        assert isinstance(name, str)
        assert name

        # Ensure the item exists
        assert ds.has(name=name)

        # Try to get the item (should return the encrypted string)
        assert ds.get(name=name) != value

        # Try to get the item and decrypt it
        assert ds.get(name=name, decrypt=True) == value

        # Try to get the item with a default (should return the encrypted
        # string)
        assert ds.get(
            name=name,
            default=DEFAULT_STR_VALUE
        ) != value

        # Try to get the item with a default and decrypt it
        assert ds.get(
            name=name,
            default=DEFAULT_STR_VALUE,
            decrypt=True
        ) == value


    #
    # Perform the basic tests
    #
    def _basic_tests(self, ds: DataStoreBaseClass | None):
        '''
        Run a set of basic tests against the datastore

        Args:
            ds (DataStoreBaseClass): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)
        
        # The item should not exist
        self._assert_not_set(ds=ds, name=BASIC_NAME)

        # Create the item and check it exists (this checks the 'get' method)
        ds.set(name=BASIC_NAME, value=SIMPLE_STR_VALUE)
        self._assert_set(ds=ds, name=BASIC_NAME, value=SIMPLE_STR_VALUE)

        # Delete the item and make sure it is gone
        ds.delete(name=BASIC_NAME)
        self._assert_not_set(ds=ds, name=BASIC_NAME)


    #
    # Perform the tests for an encrypted item
    #
    def _encrypted_tests(self, ds: DataStoreBaseClass | None):
        '''
        Run a set of tests against an encryped item the datastore

        Args:
            ds (DataStoreBaseClass): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)
        
        # The item should not exist
        self._assert_not_set(ds=ds, name=BASIC_NAME)

        # Create the item and check it exists (this checks the 'get' method)
        ds.set(name=BASIC_NAME, value=SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(ds=ds, name=BASIC_NAME, value=SIMPLE_STR_VALUE)

        # Delete the item and make sure it is gone
        ds.delete(name=BASIC_NAME)
        self._assert_not_set(ds=ds, name=BASIC_NAME)


    #
    # Perform the tests for an item that expires
    #
    def _expiry_tests(self, ds: DataStoreBaseClass | None):
        '''
        Run a set of tests for an item that expires

        Args:
            ds (DataStoreBaseClass): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)

        # The item should not exist
        self._assert_not_set(ds=ds, name=BASIC_NAME)

        # Create the item and check it exists (this checks the 'get' method)
        ds.set(
            name=BASIC_NAME,
            value=SIMPLE_STR_VALUE,
            timeout=DEFAULT_TIMEOUT
        )
        self._assert_set(ds=ds, name=BASIC_NAME, value=SIMPLE_STR_VALUE)

        time.sleep(DEFAULT_TIMEOUT + DEFAULT_WAIT)

        # Make sure it is gone
        self._assert_not_set(ds=ds, name=BASIC_NAME)


    #
    # Perform the tests for dot names
    #
    def _dot_name_tests(self, ds: DataStoreBaseClass | None):
        '''
        Run a set of tests using dot names

        Args:
            ds (DataStoreBaseClass): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreBaseClass)

        # Make sure the data store is using dot names
        assert ds.dot_names

        # Create items using dotnames
        for _name in DOT_NAME_LIST:
            # Append "_value" to create a astring tgo use as the value
            _value = f"{_name}_value"

            # The item should not exist
            self._assert_not_set(ds=ds, name=_name)

            # Create the item and check it exists (this checks the 'get' method)
            ds.set(name=_name, value=_value)
            self._assert_set(ds=ds, name=_name, value=_value)


        # Test writing to an invalid dot name
        # - trying to add a value in the lower level of a tree
        # - Trying to add a branch when a value is set
        for _name in INVALID_DOT_NAME_LIST:
            with pytest.raises(KeyError):
                ds.set(name=_name, value=DEFAULT_STR_VALUE)

        for _name in DOT_NAME_LIST:
            ds.delete(name=_name)
            self._assert_not_set(ds=ds, name=_name)


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

