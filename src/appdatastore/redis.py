#!/usr/bin/env python3
'''
Datastore - Redis

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
from redis import Redis
# from appcore.helpers import timestamp
# from appcore.conversion import set_value, DataType, from_json, to_json

# Local app modules
from appdatastore.base import DataStoreBaseClass
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


#
# Global Variables
#


###########################################################################
#
# DataStoreRedis Class Definition
#
###########################################################################
class DataStoreRedis(DataStoreBaseClass):
    '''
    Class to describe the Redis datastore.

    A wrapper to crate a similar interface to Redis as other datastores

    Attributes:
        connected (bool) [ReadOnly]: If True the connection to Redis has been
            established
    '''
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
        # Extract the args for the redis connection (prefixed with 'redis_')
        _redis_args = {}
        _new_kwargs = {}

        for _key, _value in kwargs.items():
            if _key.find("redis_") == 0:
                _new_key = _key.replace("redis_", "")
                _redis_args[_new_key] = _value

            else:
                # Add this to the remaining kwargs
                _new_kwargs[_key] = _value

        # Run init in super class without the 'redis' keyword args
        super().__init__(*args, **_new_kwargs)

        # Set defaults for certain args
        if not "port" in _redis_args: _redis_args["port"] = 6379
        _redis_args["decode_responses"] = True

        # Private Attributes
        self._redis_args = _redis_args
        self._redis: Redis | None = None

        # Always store values serialised (just easier to process)
        self._store_serialised = True
        self._serialisation_method = SerialisationType.JSON
        self._encrypt_to_string = True

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # connected
    #
    @property
    def connected(self) -> bool:
        ''' Indicator if connected to Redis '''
        return True if isinstance(self._redis, Redis) else False


    ###########################################################################
    #
    # Redis Connectivity
    #
    ###########################################################################
    #
    # connect
    #
    def connect(self):
        '''
        Connect to a redis datastore

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self._redis = Redis(**self._redis_args)

        # Try an action on redis to see if connection works
        # Should raise an exception if connection doesn't work
        self._redis.exists("__connection_test__")


    #
    # disconnect
    #
    def disconnect(self):
        '''
        Disconnect from a redis datastore

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self._redis = None


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

        # Redis handles item expiry

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
            FileNotFoundError
                When not connected to Redis
        '''
        if not isinstance(self._redis, Redis):
            raise FileNotFoundError(
                "A connection has not been established to Redis"
            )

        self.maintenance()

        # 'exists' returns a number and our return is boolean, so be explicit
        if self._redis.exists(name):
            return True
        else:
            return False


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
            FileNotFoundError
                When not connected to Redis
            TypeError
                When value stored in Redis is not a string
        '''
        if not isinstance(self._redis, Redis):
            raise FileNotFoundError(
                "A connection has not been established to Redis"
            )

        if not self.has(name): return default

        # Check the type of the value (store everything as a string)
        _value_type = self._redis.type(name)
        if _value_type == "string":
            # String
            _value = str(self._redis.get(name))

        else:
            raise TypeError(
                f"Redis variable type not supported: {_value_type}"
            )

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
            FileNotFoundError
                When not connected to Redis
            AssertionError:
                When timeout is not zero or a positive integer
            KeyError:
                When the dot name is a low part of a hierarchy
        '''
        if not isinstance(self._redis, Redis):
            raise FileNotFoundError(
                "A connection has not been established to Redis"
            )

        assert isinstance(timeout, int), "Timeout value must be an integer"
        assert timeout >= 0, "Timeout value must be a postive integer"

        self.maintenance()

        # Check on dot names
        if self._dot_names:
            _keys = list(self._redis.scan_iter())
            if not self._check_dot_name(keys=_keys, name=name):
                raise KeyError(
                    "Value cannot be stored in a intermediate dot level name"
                )

        # Encode the value for storage (possibly encrypting)
        _value_to_store = self._encode(value=value, encrypt=encrypt)

        self._redis.set(name, _value_to_store)

        # Set the expiry value
        if timeout: 
            self._redis.expire(name, timeout)


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
            FileNotFoundError
                When not connected to Redis
        '''
        if not isinstance(self._redis, Redis):
            raise FileNotFoundError(
                "A connection has not been established to Redis"
            )

        if not self.has(name): return

        # 'delete' should raise an exception if there is a problem
        self._redis.delete(name)


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
            FileNotFoundError
                When not connected to Redis
        '''
        if not isinstance(self._redis, Redis):
            raise FileNotFoundError(
                "A connection has not been established to Redis"
            )

        self.maintenance()
        _item_list = []

        for _item in self._redis.scan_iter(match=f"{prefix}*"):
            _item_list.append(_item)
 
        return _item_list


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
            NotImplementedError
                When called as function is not supported
        '''
        raise NotImplementedError(
            "Export to JSON not support for Redis Datastore"
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
