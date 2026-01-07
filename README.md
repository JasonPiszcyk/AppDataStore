# AppDataStore
Copyright (c) 2025 Jason Piszcyk

Applications Components - Data Stores

<!-- 
Not yet Published to PyPi
[![PyPI version](https://badge.fury.io/py/appdatastore.svg)](https://pypi.org/project/appdatastore/)
[![Build Status](https://github.com/JasonPiszcyk/AppnetComms/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppDataStore/actions)
 -->

## Overview

**AppDataStore** provides different data store implementations

## Features

**AppDataStore** consists of a number of sub-modules, being:
- Global
  - A global class for storing variable information
- Shared
  - Implementation of list add dict in shared memory to allow sharing between threads/processes
- INI
  - Datastore implemented as an INI file
- REDIS
  - Interface to REDIS.  Implemented in separate module AppDataStore-REDIS


## Installation

Module has not been published to PyPi yet.  Install via:
```bash
pip install "appdatastore @ git+https://github.com/JasonPiszcyk/AppDataStore"
```

## Requirements

- Python >= 3.8

**NOTE:** The module has tested against Python 3.14 and 3.8

## Dependencies

- pytest
- "crypto_tools @ git+https://github.com/JasonPiszcyk/CryptoTools"

## Usage

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
