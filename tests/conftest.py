#!/usr/bin/env python3
'''
PyTest - Testing Config

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
import os

# Local app modules

# Imports for python variable type hints


###########################################################################
#
# Config
#
###########################################################################
def pytest_configure(config: pytest.Config):
    '''
    Global configuration for the PyTest session

    Args:
        config (pytest.Config): Configuration information

    Returns:
        None

    Raises:
        None
    '''
    pass


###########################################################################
#
# Fixtures
#
###########################################################################
#
# INI file
#
@pytest.fixture(scope="function")
def inifile(request: pytest.FixtureRequest) -> str:
    '''
    Make sure the ini file is empty at start of test and deleted at end of test

    Args:
        None

    Returns:
        str: The path for the log file

    Raises:
        None
    '''
    def _delete_file():
        if os.path.exists(INI_FILE_NAME):
            os.remove(INI_FILE_NAME)

    # Delete the file
    _delete_file()

    # Add a finaliser to delete the file regardless of the test status
    request.addfinalizer(_delete_file)

    return INI_FILE_NAME
