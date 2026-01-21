#!/usr/bin/env python3
'''
PyTest - Test of Redis datastore functions

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

# Local app modules
from test_base import TestBase
from appdatastore.redis import DataStoreRedis

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

#
# Global Variables
#


###########################################################################
#
# The tests...
#
###########################################################################
#
# Redis DataStore
#
class Test_Redis_Datastore(TestBase):
    '''
    Test Class - Redis Datastore

    Attributes:
        None
    '''
    #
    # Basic Tests - Has/Set/Get/Delete
    #
    def test_basic(self):
        '''
        Basic tests

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _ds = DataStoreRedis(security="low")
        _ds.connect()

        self._basic_tests(ds=_ds)


    #
    # Encryption Tests - Use different encryption options
    #
    @pytest.mark.parametrize("options", ENCRYPTION_OPTION_SETS)
    def test_encryption(self, options):
        '''
        Encryption tests

        Args:
            options (str): Fixture containing the key to process from the
                OPTION_SETS dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert options in ENCRYPTION_OPTION_SETS

        _kwargs = ENCRYPTION_OPTION_SETS[options]
        assert isinstance(_kwargs, dict)

        _ds = DataStoreRedis(security="low", **_kwargs)
        _ds.connect()

        self._encrypted_tests(ds=_ds)


    #
    # Expiry Tests
    #
    def test_expiry(self):
        '''
        Expiry tests

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _ds = DataStoreRedis(security="low")
        _ds.connect()

        self._expiry_tests(ds=_ds)


    #
    # Dot name Tests
    #
    def test_dot_names(self):
        '''
        Dotname tests

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _ds = DataStoreRedis(security="low",  dot_names=True)
        _ds.connect()

        self._dot_name_tests(ds=_ds)


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

