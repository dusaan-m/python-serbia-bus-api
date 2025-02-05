# Serbia Bus API

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdusaan-m%2Fpython-serbia-bus-api%2Fmain%2Fpyproject.toml)
![License](https://img.shields.io/badge/license-MIT-green)

Serbia Bus API (`srbusapi`) is a Python package that provides access to real-time bus arrival data for major cities in Serbia, including Belgrade, Novi Sad, and Niš. It is based on a reversed-engineered API extracted from mobile bus applications, allowing developers to retrieve bus station details, arrival times, and route information efficiently.

## Features

- Retrieve real-time bus arrivals for stations in Belgrade, Novi Sad, and Niš.
- Fetch route details and versions for specific bus lines.
- Caching support via Redis for optimized API calls.
- AES encryption for secure communication with APIs.
- Asynchronous support using `httpx`.

## Installation

Install `srbusapi` via pip:

```sh
pip install srbusapi
```

For Redis caching support, install with:

```sh
pip install srbusapi[redis]
```

## Usage

### Initialize a Client

To use the API, import the desired city client and fetch data:

```python
import asyncio
from srbusapi import BeogradClient

async def main():
    client = BeogradClient()

    # Fetch station details
    stations = await client.get_stations() # Returns a list of stations explore this to see ids for stations
    print(stations)

    # Fetch arrivals for a specific station
    arrivals = await client.get_arrivals(station_id="20493")
    print(arrivals)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Redis Cache

If you have Redis set up, provide the credentials via environment variables:

```sh
export REDIS_HOST=localhost # Put your redis host here
export REDIS_PORT=6379 # Put your redis port here
export REDIS_USERNAME=yourusername # Optional
export REDIS_PASSWORD=yourpassword # Optional
```


```python
import asyncio
from srbusapi import BeogradClient, RedisCache


async def main():
    cache = RedisCache(
        host="localhost", # Put your redis host here
        port=6379, # Put your redis port here
        username="yourusername",  # Optional
        password="yourpassword"  # Optional
    )
    client = BeogradClient(cache=cache)

    stations = await client.get_stations()
    print(stations)


if __name__ == "__main__":
    asyncio.run(main())
```

## API Methods

### General Methods (Available in all city clients)

- `get_stations() -> dict` - Retrieve station information.
- `get_arrivals(station_id: str) -> dict` - Fetch bus arrival times.
- `get_route(actual_line_number: str) -> dict` - Get route details for a bus line.
- `get_route_version(actual_line_number: str) -> dict` - Fetch the latest route version.

### City-Specific Clients

| City     | Client Class    |
|----------|-----------------|
| Belgrade | `BeogradClient` |
| Novi Sad | `NoviSadClient` |
| Niš      | `NisClient`     |

## Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

