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
  - Has 2 different modes for accessing shred memory segments:
    - Datastore: Opens and closes the shared memory on each access and maintains control over access.  When writing, will always create a new segment to ensure the size is set correctly.  This is slower but safer.
    - Fast: Shared memory must be explicitly opened and closed.  Can lead to memory leaks.  Datastore mode wraps 'fast' mode functions for safety.
- [INI File](#ini-file-usage)
  - Datastore implemented as an INI file.
- REDIS
  - Interface to REDIS.  Implemented in separate module AppDataStore-REDIS.

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

**NOTE:** The module has been tested against Python 3.14 and 3.8.

## Dependencies

- pytest
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


### <a id="mem-usage"></a>Mem
*class* AppDataStore.**DataStoreMem**(***Common Arguments***)

Common arguments as per [Common Arguments](#common-arguments)

**maintenance()**
<div style="padding-left: 30px;">
  Perform maintenance on items (such as expiry).  It is generally not necesary to call this function as it call whenever the DS is accessed.
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
    <tr><td><b>list</b> (str)</td><td>Match any item names beginning with this</td></tr>
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
*class* AppDataStore.**DataStoreSharedMem**(***Common Arguments***)

Common arguments as per [Common Arguments](#common-arguments)

### <a id="ini-file-usage"></a>INI File
*class* AppDataStore.**DataStoreINIFile**(***Common Arguments***, *filename=""*)

Common arguments as per [Common Arguments](#common-arguments)

| Argument | Description |
| - | - |
| **filename** (str) | The path for the INI file |

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
