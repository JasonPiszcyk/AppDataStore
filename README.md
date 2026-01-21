# AppDataStore
Copyright (c) 2025 Jason Piszcyk

Applications Components - Data Stores

<!-- 
Not yet Published to PyPi
[![PyPI version](https://badge.fury.io/py/appdatastore.svg)](https://pypi.org/project/appdatastore/)
[![Build Status](https://github.com/JasonPiszcyk/AppnetComms/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppDataStore/actions)
 -->


## Overview


**AppDataStore** provides different data store implementations.


## Features


**AppDataStore** consists of a number of sub-modules, being:
- [Mem](#mem-usage)
  - A memory based datastore for storing information within a process.
- [Shared Mem](#shared-mem-usage)
  - Implementation of data store in shared memory to allow sharing between threads/processes.
  - Also implements a single item shared memory interface DataStoreSharedMemItem
- [INI File](#ini-file-usage)
  - Datastore implemented as an INI file.
- [Redis](#redis-usage)
  - Interface to Redis consistent with datastores in this module.

All datastores share a set of basic characteristics:
- Encryption
  - If a password is not specified, a random password will be generated and used when the object is instantiated.
  - If a salt is not specific, an internal salt will be used.
  - A security level can be chosen from "low", "medium", "high" (default = "high").
    - This defines the computation cost for deriving a key from the password (higher = longer computation time = more difficult to brute force).
- Dot Names
  - If enabled, '.' (dots/periods) in item names are used to create a hierarchy, eg:
  - The variables Branch-1.SubBranch-1.item-1, Branch-1.SubBranch-1.item-2, and Branch-1.SubBranch-2.item-1 break into a hierarchy as follows:
    - Branch-1
      - SubBranch-1
        - item-1
        - item-2
      - SubBranch-2
        - item-1
  - Items can only be stored in the bottom branch nodes (eg trying to store a value in Branch-1.item-1 is invalid once a sub-branch has been created).
  - Sub Branches cannot be created in a 'bottom branch' node if an item exists (eg trying to create Branch-1.SubBranch-1.AnotherBranch.item-1 is invalid once an item has been created in Branch-1.SubBranch-1).
- Logging
  - The default module logger writes to the console, and the logging level can be customised.
  - A custom python logger can be used in place of the default module logger to allow for greater customisation.


## Installation

Module has not been published to PyPi yet.  Install via:
```bash
pip install "appdatastore @ git+https://github.com/JasonPiszcyk/AppDataStore"
```


## Requirements

- Python >= 3.8

> [!NOTE]
> The module has been tested against Python 3.8 and 3.14.


## Dependencies

- pytest
- redis
- "appcore @ git+https://github.com/JasonPiszcyk/AppCore"
- "crypto_tools @ git+https://github.com/JasonPiszcyk/CryptoTools"


## Usage


### <a id="common-arguments"></a>Common Arguments
*class* AppDataStore.**DataStoreBaseClass**(*password="", salt=b"", security="high", dot_names=False, logger_name="", logger_level="CRITICAL"*)

| Argument | Description |
| - | - |
| **password** (str) | The password used to derive the encryption key - A random password will be used if none provided |
| **salt** (bytes) | A binary string containing the salt - A default salt will be used in none provided |
| **security** (str) | Determines the computation time of the key.  Must be one of "low", "medium", or "high" |
| **dot_names** (bool) | If True, use dot names to create a hierarchy of values for this data store.  If False, dots in names are treated as normal characters |
| **logger_name** (str) | The name of the logger to use.  If empty (or not a string) then a logger will be created to log to the console |
| **logger_level** (str) | If no logger name is provided, the created logger will be set to log events at or above this level (default = "CRITICAL") |


### <a id="common-properties"></a>Common Properties
| Property | Description |
| - | - |
| **dot_names** (str) [ReadOnly] | If True, dot names are used to create a hierarchy of values for this data store |


### <a id="mem-usage"></a>Mem
*class* AppDataStore.**DataStoreMem**(***Common Arguments***)

Common arguments as per [Common Arguments](#common-arguments)

Common properties as per [Common Properties](#common-properties)


**maintenance()**

Perform maintenance on items (such as expiry).  It is generally not necessary to call this function as it is called whenever the datastore is accessed.


**has(** name="" **)**

> Check if the item represented by *name* exists in the datastore.

> | Argument | Description |
> | - | - |
> | **name** (str) | The name of the item to check |


**get(** name="", default=None, decrypt=False **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to get</td></tr>
    <tr><td><b>default</b> (Any)</td><td>Value to return if the item cannot be found</td></tr>
    <tr><td><b>decrypt</b> (bool)</td><td>If True, attempt to decrypt the value</td></tr>
  </table>

  Get the item represented by *name* in the datastore, optionally trying to decrypt the encrypted stored value.  If not found, return the value specified in *default*.
</div>


**set(** name="", value=Any, encrypt=False, timeout=0 **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to set</td></tr>
    <tr><td><b>value</b> (Any)</td><td>The value to set the item to</td></tr>
    <tr><td><b>encrypt</b> (bool)</td><td>If True, encrypt the value before storing it</td></tr>
    <tr><td><b>timeout</b> (int)</td><td>The number of seconds before the item should be deleted (0 = never delete)</td></tr>
  </table>

  Set the item represented by *name* in the datastore to *value*. If *encrypt* is True, encrypt the item before storing.  If *timeout* is non-zero, delete the item after *timeout* seconds.
</div>


**delete(** name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to delete</td></tr>
  </table>

  Delete the item represented by *name* from the datastore.
</div>


**list(** prefix="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>prefix</b> (str)</td><td>Match any item names beginning with this string</td></tr>
  </table>

  List the items in the data store.  If *prefix* is provided, the list will be restricted to those item names that start with *prefix*.
</div>


**export_to_json(** container=True **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>container</b> (bool)</td><td>If True, additional non-standard information is added to assist with data typing when importing the JSON data.  This additional information will not be processed correctly by a standard JSON interpreter and should appears as additional string values.</td></tr>
  </table>

  Export the items in the data store to a JSON format.  If *container* is True, additional non-standard information is added to assist with data typing.
</div>


### <a id="shared-mem-usage"></a>Shared Mem
*class* AppDataStore.**DataStoreSharedMemItem**(*name="", size=1, logger_name="", logger_level="CRITICAL"*)

| Argument | Description |
| - | - |
| **name** (str) | The name of the item/shared memory segment |
| **size** (str) | The requested size of the shared memory segment if it needs to be created, or ignored if connecting to existing segment  (default = 1) |
| **logger_name** (str) | The name of the logger to use.  If empty (or not a string) then a logger will be created to log to the console |
| **logger_level** (str) | If no logger name is provided, the created logger will be set to log events at or above this level (default = "CRITICAL") |

| Property | Description |
| - | - |
| **name** (str) [ReadOnly] | The name of the item/shared memory segment |
| **size** (str) [ReadOnly] | The size of the shared memory segment (which maybe larger than the requested size when it was created) |

**open()**
<div style="padding-left: 30px;">
  Connect to the shared memory segment (if is has been closed) or create a new segment (if it has never been created or has been unlinked). This is called automatically when the instance is created.
</div>
&nbsp

**close()**
<div style="padding-left: 30px;">
  Disconnect from shared memory segment.
</div>
&nbsp

**delete()**
<div style="padding-left: 30px;">
  Disconnect from shared memory segment and delete it. The segment will no longer be accessible for remote processes.
</div>
&nbsp

**get()**
<div style="padding-left: 30px;">
  Get the raw value (in bytes) from the shared memory segment. The segment is locked during the write of the value.
</div>
&nbsp

**set(** value=b"" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>value</b> (bytes)</td><td>The raw value, in bytes, to store in the shared memory segment</td></tr>
  </table>

  Store a value in the shared memory segment.
</div>

**update(** function=None **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>function</b> (Callable)</td><td>A function to transform the stored value to the new value. Must accept the current value as bytes and return the new value as bytes</td></tr>
  </table>

  Perform an atomic update using the mutation function provided.  The item is locked before the value is read until the function completes and the result is written.
</div>

```python
# Example usage of Shared Memory Item
from appdatastore.shared_mem_item import (
  DataStoreSharedMemItem,
  shared_memory_exists
)

# More useful to use a pickle, etc
byte_val = b"A simple value"

# Create the Item in Process 1
shm = DataStoreSharedMemItem(name="Test Value", size=len(byte_val))

# Connect to existing item Process 2
shm = DataStoreSharedMemItem(name="Test Value", size=len(byte_val))

# Get size
shm_size = shm.size     # Might be a page size like 16384 NOT size of value

# Add a value
shm.set(value=byte_val)

# Get the value
stored_val = shm.get()  # Will be = b"A simple value"

# Modify the value
def mutate_function(old_value):
  new_value = old_value + b" plus some extra words"
  return new_value

shm.update(func=mutate_function)

# Get the value
updated_val = shm.get()  # Will be = b"A simple value plus some extra words"

# Disconnect in Process 2
shm.close()

# Delete in Process 1
shm.delete()
```

*class* AppDataStore.**DataStoreSharedMem**(***Common Arguments***, *name="", encrypt_index=False, index_size=16384, delete_on_cleanup=False*)

Common arguments as per [Common Arguments](#common-arguments)

| Argument | Description |
| - | - |
| **name** (str) | Name of the data store |
| **encrypt_index** (bool) | Encrypt the index when storing it in shared memory (default = False) |
| **index_size** (int) | The size of the index (default = 16384).  Can be increased if a large number of items (> 100) are being stored |
| **delete_on_cleanup** (bool) | If True, unlink all shared memory segments when the cleanup function is called, or when the datastore is no longer used (default = False) |

Common properties as per [Common Properties](#common-properties)

| Property | Description |
| - | - |
| **name** (str) [ReadOnly] | The name of the datastore |
| **index_size** (str) [ReadOnly] | The size of the index shared memory segment (which maybe larger than the requested size when it was created) |


**maintenance()**
<div style="padding-left: 30px;">
  Perform maintenance on items (such as expiry).  It is generally not necesary to call this function as it call whenever the datastore is accessed.
</div>
&nbsp

**has(** name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to check</td></tr>
  </table>

  Check if the item represented by *name* exists in the datastore.
</div>


**get(** name="", default=None, decrypt=False **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to get</td></tr>
    <tr><td><b>default</b> (Any)</td><td>Value to return if the item cannot be found</td></tr>
    <tr><td><b>decrypt</b> (bool)</td><td>If True, attempt to decrypt the value</td></tr>
  </table>

  Get the item represented by *name* in the datastore, optionally trying to decrypt the encrypted stored value.  If not found, return the value specified in *default*.
</div>


**set(** name="", value=Any, encrypt=False, timeout=0 **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to set</td></tr>
    <tr><td><b>value</b> (Any)</td><td>The value to set the item to</td></tr>
    <tr><td><b>encrypt</b> (bool)</td><td>If True, encrypt the value before storing it</td></tr>
    <tr><td><b>timeout</b> (int)</td><td>The number of seconds before the item should be deleted (0 = never delete)</td></tr>
  </table>

  Set the item represented by *name* in the datastore to *value*. If *encrypt* is True, encrypt the item before storing.  If *timeout* is non-zero, delete the item after *timeout* seconds.
</div>


**delete(** name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to delete</td></tr>
  </table>

  Delete the item represented by *name* from the datastore.
</div>


**list(** prefix="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>prefix</b> (str)</td><td>Match any item names beginning with this string</td></tr>
  </table>

  List the items in the data store.  If *prefix* is provided, the list will be restricted to those item names that start with *prefix*.
</div>


**export_to_json(** container=True **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>container</b> (bool)</td><td>If True, additional non-standard information is added to assist with data typing when importing the JSON data.  This additional information will not be processed correctly by a standard JSON interpreter and should appears as additional string values.</td></tr>
  </table>

  Export the items in the data store to a JSON format.  If *container* is True, additional non-standard information is added to assist with data typing.
</div>


### <a id="ini-file-usage"></a>INI File
*class* AppDataStore.**DataStoreINIFile**(***Common Arguments***, *filename=""*)

Common arguments as per [Common Arguments](#common-arguments)

| Argument | Description |
| - | - |
| **filename** (str) | The path for the INI file |

Common properties as per [Common Properties](#common-properties)

| Property | Description |
| - | - |
| **filename** (str) [ReadOnly] | The path for the INI file |

**maintenance()**
<div style="padding-left: 30px;">
  Perform maintenance on items (such as expiry).  It is generally not necesary to call this function as it call whenever the DS is accessed.
</div>
&nbsp

**has_section(** section="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>section</b> (str)</td><td>The section to check</td></tr>
  </table>

  Check if the section represented by *section* exists in the datastore.
</div>


**has(** section="", name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>section</b> (str)</td><td>The section to check</td></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to check</td></tr>
  </table>

  Check if the item represented by *name* exists in the section represented by *section* in the datastore.
</div>


**get(** section="", name="", default=None, decrypt=False **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>section</b> (str)</td><td>The section containing the item to get</td></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to get</td></tr>
    <tr><td><b>default</b> (Any)</td><td>Value to return if the item cannot be found</td></tr>
    <tr><td><b>decrypt</b> (bool)</td><td>If True, attempt to decrypt the value</td></tr>
  </table>

  Get the item represented by *name*, in the section represented by *section*, in the datastore, optionally trying to decrypt the encrypted stored value.  If not found, return the value specified in *default*.
</div>


**set(** section="", name="", value=Any, encrypt=False, timeout=0 **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>section</b> (str)</td><td>The section containing the item to set</td></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to set</td></tr>
    <tr><td><b>value</b> (Any)</td><td>The value to set the item to</td></tr>
    <tr><td><b>encrypt</b> (bool)</td><td>If True, encrypt the value before storing it</td></tr>
    <tr><td><b>timeout</b> (int)</td><td>The number of seconds before the item should be deleted (0 = never delete)</td></tr>
  </table>

  Set the item represented by *name*, in the section represented by *section*, in the datastore to *value*. If *encrypt* is True, encrypt the item before storing.  If *timeout* is non-zero, delete the item after *timeout* seconds.
</div>


**delete(** section="", name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>section</b> (str)</td><td>The section containing the item to delete</td></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to delete</td></tr>
  </table>

  Delete the item represented by *name*, in the section represented by *section*, from the datastore.
</div>


**delete_file()**
<div style="padding-left: 30px;">
  Delete the file provided when the object was created.
</div>
&nbsp


**list(** section="", prefix="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>section</b> (str)</td><td>The section containing the items to list</td></tr>
    <tr><td><b>list</b> (str)</td><td>Match any item names beginning with this</td></tr>
  </table>

  List the items in the data store.  If *section* is not provided, list the sections in the datastore.  If *section* is provided, list the items with the section. If *prefix* is provided, the list will be restricted to those item or section names that start with *prefix*.
</div>


**export_to_json(** container=True **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>container</b> (bool)</td><td>If True, additional non-standard information is added to assist with data typing when importing the JSON data.  This additional information will not be processed correctly by a standard JSON interpreter and should appears as additional string values.</td></tr>
  </table>

  Export the items in the data store to a JSON format.  If *container* is True, additional non-standard information is added to assist with data typing.
</div>


### <a id="redis-usage"></a>Mem
*class* AppDataStore.**DataStoreRedis**(***Common Arguments***, ***Redis Arguments***)

Common arguments as per [Common Arguments](#common-arguments)

Redis Arguments are prefixed with 'redis_'.  Args have the prefix ('redis_') stripped and are passed to the Redis object constructur.

Common properties as per [Common Properties](#common-properties)

| Property | Description |
| - | - |
| **connected** (str) [ReadOnly] | If True, the connection to Redis has been established |


**connect()**
<div style="padding-left: 30px;">
  Connect to Redis datastore
</div>
&nbsp

**disconnect()**
<div style="padding-left: 30px;">
  Disconnect from the Redis datastore.
</div>
&nbsp

**maintenance()**
<div style="padding-left: 30px;">
  Perform maintenance on items.  It is generally not necesary to call this function as it call whenever the datastore is accessed.
</div>
&nbsp

**has(** name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to check</td></tr>
  </table>

  Check if the item represented by *name* exists in the datastore.
</div>

**get(** name="", default=None, decrypt=False **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to get</td></tr>
    <tr><td><b>default</b> (Any)</td><td>Value to return if the item cannot be found</td></tr>
    <tr><td><b>decrypt</b> (bool)</td><td>If True, attempt to decrypt the value</td></tr>
  </table>

  Get the item represented by *name* in the datastore, optionally trying to decrypt the encrypted stored value.  If not found, return the value specified in *default*.
</div>


**set(** name="", value=Any, encrypt=False, timeout=0 **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to set</td></tr>
    <tr><td><b>value</b> (Any)</td><td>The value to set the item to</td></tr>
    <tr><td><b>encrypt</b> (bool)</td><td>If True, encrypt the value before storing it</td></tr>
    <tr><td><b>timeout</b> (int)</td><td>The number of seconds before the item should be deleted (0 = never delete)</td></tr>
  </table>

  Set the item represented by *name* in the datastore to *value*. If *encrypt* is True, encrypt the item before storing.  If *timeout* is non-zero, delete the item after *timeout* seconds.
</div>


**delete(** name="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>name</b> (str)</td><td>The name of the item to delete</td></tr>
  </table>

  Delete the item represented by *name* from the datastore.
</div>


**list(** prefix="" **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>prefix</b> (str)</td><td>Match any item names beginning with this string</td></tr>
  </table>

  List the items in the data store.  If *prefix* is provided, the list will be restricted to those item names that start with *prefix*.
</div>


**export_to_json(** container=True **)**
<div style="padding-left: 30px;">
  <table>
    <tr><th>Argument</th><th>Description</th></tr>
    <tr><td><b>container</b> (bool)</td><td>If True, additional non-standard information is added to assist with data typing when importing the JSON data.  This additional information will not be processed correctly by a standard JSON interpreter and should appears as additional string values.</td></tr>
  </table>

  Not currently implemented.  Raises 'NotImplementedError'.
</div>


```python
import appdatastore
# Example usage of AppDataStore components
```

## Development

1. Clone the repository:
    ```bash
    git clone https://github.com/JasonPiszcyk/AppDataStore.git
    cd AppDataStore
    ```
2. Install dependencies:
    ```bash
    pip install -e .[dev]
    ```

## Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please submit issues or pull requests via [GitHub Issues](https://github.com/JasonPiszcyk/AppDataStore/issues).

## License

GNU General Public License

## Author

Jason Piszcyk  
[Jason.Piszcyk@gmail.com](mailto:Jason.Piszcyk@gmail.com)

## Links

- [Homepage](https://github.com/JasonPiszcyk/AppDataStore)
- [Bug Tracker](https://github.com/JasonPiszcyk/AppDataStore/issues)
