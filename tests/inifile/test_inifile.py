#!/usr/bin/env python3
'''
PyTest - Test of Ini File datastore functions

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
from tests.constants import *

# System Modules
import pytest
import time

# Local app modules
from appdatastore.inifile import DataStoreINIFile

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
# The tests...
#
###########################################################################
#
# Mem DataStore
#
class Test_INIFile_Datastore():
    '''
    Test Class - INIFile Datastore

    Can't inheret the base class as we need to overwrite everything

    Attributes:
        None
    '''
    #
    # check an item has NOT been set
    #
    def _assert_not_set(
            self,
            ds: DataStoreINIFile | None,
            section: str = "",
            name: str = ""
    ):
        '''
        Assert that the item does not exist

        Args:
            ds (DataStoreINIFile): The datastore to operate on
            section (str): The section in which the item appears 
            name (str): Name of the item

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreINIFile)
        assert isinstance(section, str)
        assert section
        assert isinstance(name, str)
        assert name

        # Ensure the item does not exist
        assert not ds.has(name=name, section=section)

        # Try to get the item (should return None)
        assert not ds.get(name=name, section=section)

        # Try to get the item (should return a default string)
        assert ds.get(
            name=name,
            section=section,
            default=DEFAULT_STR_VALUE
        ) == DEFAULT_STR_VALUE


    #
    # check an item has been set
    #
    def _assert_set(
            self,
            ds: DataStoreINIFile | None,
            section: str = "",
            name: str = "",
            value: Any = None
    ):
        '''
        Assert that the item has been set

        Args:
            ds (DataStoreINIFile): The datastore to operate on
            name (str): Name of the item
            section (str): The section in which the item appears 
            value (Any): Value to set the item to

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreINIFile)
        assert isinstance(section, str)
        assert section
        assert isinstance(name, str)

        # Ensure the item exists
        assert ds.has(name=name, section=section)

        # Try to get the item (should return the value)
        assert ds.get(name=name, section=section) == value

        # Try to get the item (should return the value)
        assert ds.get(
            name=name,
            section=section,
            default=DEFAULT_STR_VALUE
        ) == value


    #
    # check an item has been set (value is encrypted)
    #
    def _assert_set_enc(
            self,
            ds: DataStoreINIFile | None,
            section: str = "",
            name: str = "",
            value: Any = None
    ):
        '''
        Assert that the item has been set

        Args:
            ds (DataStoreINIFile): The datastore to operate on
            name (str): Name of the item
            section (str): The section in which the item appears 
            value (Any): Value to set the item to

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreINIFile)
        assert isinstance(section, str)
        assert section
        assert isinstance(name, str)

        # Ensure the item exists
        assert ds.has(name=name, section=section)

        # Try to get the item (should return the encrypted string)
        assert ds.get(name=name, section=section) != value

        # Try to get the item and decrypt it
        assert ds.get(name=name, section=section, decrypt=True) == value

        # Try to get the item with a default (should return the encrypted
        # string)
        assert ds.get(
            name=name,
            section=section,
            default=DEFAULT_STR_VALUE
        ) != value

        # Try to get the item with a default and decrypt it
        assert ds.get(
            name=name,
            section=section,
            default=DEFAULT_STR_VALUE,
            decrypt=True
        ) == value


    #
    # Perform the basic tests
    #
    def _basic_tests(self, ds: DataStoreINIFile | None):
        '''
        Run a set of basic tests against the datastore

        Args:
            ds (DataStoreINIFile): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreINIFile)
        
        # The item should not exist
        self._assert_not_set(ds=ds, name=BASIC_NAME, section=BASIC_SECTION)

        # Create the item and check it exists (this checks the 'get' method)
        ds.set(name=BASIC_NAME, section=BASIC_SECTION, value=SIMPLE_STR_VALUE)
        self._assert_set(
            ds=ds,
            name=BASIC_NAME,
            section=BASIC_SECTION,
            value=SIMPLE_STR_VALUE
        )

        # Delete the item and make sure it is gone
        ds.delete(name=BASIC_NAME, section=BASIC_SECTION)
        self._assert_not_set(ds=ds, name=BASIC_NAME, section=BASIC_SECTION)


    #
    # Perform the tests for an encrypted item
    #
    def _encrypted_tests(self, ds: DataStoreINIFile | None):
        '''
        Run a set of tests against an encryped item the datastore

        Args:
            ds (DataStoreINIFile): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreINIFile)
        
        # The item should not exist
        self._assert_not_set(ds=ds, name=BASIC_NAME, section=BASIC_SECTION)

        # Create the item and check it exists (this checks the 'get' method)
        ds.set(
            name=BASIC_NAME,
            section=BASIC_SECTION,
            value=SIMPLE_STR_VALUE,
            encrypt=True
        )
        self._assert_set_enc(
            ds=ds,
            name=BASIC_NAME,
            section=BASIC_SECTION,
            value=SIMPLE_STR_VALUE
        )
        

        # Delete the item and make sure it is gone
        ds.delete(name=BASIC_NAME, section=BASIC_SECTION)
        self._assert_not_set(ds=ds, name=BASIC_NAME, section=BASIC_SECTION)


    #
    # Perform the tests for an item that expires
    #
    def _expiry_tests(self, ds: DataStoreINIFile | None):
        '''
        Run a set of tests for an item that expires

        Args:
            ds (DataStoreINIFile): The datastore to operate on

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert isinstance(ds, DataStoreINIFile)

        # The item should not exist
        self._assert_not_set(ds=ds, name=BASIC_NAME, section=BASIC_SECTION)

        # Create the item and check it exists (this checks the 'get' method)
        ds.set(
            name=BASIC_NAME,
            value=SIMPLE_STR_VALUE,
            section=BASIC_SECTION,
            timeout=DEFAULT_TIMEOUT
        )
        self._assert_set(
            ds=ds,
            name=BASIC_NAME,
            section=BASIC_SECTION,
            value=SIMPLE_STR_VALUE
        )

        time.sleep(DEFAULT_TIMEOUT + DEFAULT_WAIT)

        # Make sure it is gone
        self._assert_not_set(ds=ds, name=BASIC_NAME, section=BASIC_SECTION)


    #
    # Basic Tests - Has/Set/Get/Delete
    #
    def test_basic(self, inifile):
        '''
        Basic tests

        Args:
            inifile (str): Fixture managing the ini file used during testing

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _ds = DataStoreINIFile(security="low", filename=inifile)

        self._basic_tests(ds=_ds)


    #
    # Encryption Tests - Use different encryption options
    #
    @pytest.mark.parametrize("options", ENCRYPTION_OPTION_SETS)
    def test_encryption(self, options, inifile):
        '''
        Encryption tests

        Args:
            options (str): Fixture containing the key to process from the
                OPTION_SETS dict
            inifile (str): Fixture managing the ini file used during testing

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert options in ENCRYPTION_OPTION_SETS

        _kwargs = ENCRYPTION_OPTION_SETS[options]
        assert isinstance(_kwargs, dict)

        _ds = DataStoreINIFile(security="low", filename=inifile, **_kwargs)

        self._encrypted_tests(ds=_ds)


    #
    # Expiry Tests
    #
    def test_expiry(self, inifile):
        '''
        Expiry tests

        Args:
            inifile (str): Fixture managing the ini file used during testing

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _ds = DataStoreINIFile(security="low", filename=inifile)

        self._expiry_tests(ds=_ds)


    #
    # Dot name Tests
    #
    def test_dot_names(self, inifile):
        '''
        Dotname tests

        Args:
            inifile (str): Fixture managing the ini file used during testing

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        with pytest.raises(NotImplementedError):
            _ = DataStoreINIFile(
                security="low",
                filename=inifile,
                dot_names=True
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

