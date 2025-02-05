import logging

import pytest

from srbusapi import BeogradClient
from srbusapi.caching.redis_cache import RedisCache


@pytest.fixture
def beograd_api():
    return BeogradClient(cache=RedisCache(host="localhost", port=6379))


@pytest.mark.asyncio
async def test_get_stations(beograd_api):
    stations = await beograd_api.get_stations()
    assert stations, "Stations should not be empty"
    assert isinstance(stations, dict), "Stations should be a dictionary"
    assert "cities" in stations, "Stations should contain 'cities' key"
    assert "stations" in stations, "Stations should contain 'stations' key"
    assert isinstance(stations["cities"], list), "'cities' should be a list"
    assert isinstance(stations["stations"], list), "'stations' should be a list"
    assert len(stations["stations"]) > 0, "There should be at least one station"


@pytest.mark.asyncio
async def test_get_arrivals(beograd_api):
    station_id = "20089"
    arrivals = await beograd_api.get_arrivals(station_id)

    assert arrivals, "Arrivals should not be empty"
    assert isinstance(arrivals, dict), "Arrivals should be a dictionary"
    # Check for success key and its value
    assert "success" in arrivals, "Arrivals should contain 'success' key"
    assert arrivals["success"] is True, "'success' should be True"
    # Check structure of arrivals
    assert "data" in arrivals, "Arrivals should contain 'data'"
    assert isinstance(arrivals["data"], list), "'data' should be a list"
    assert all(isinstance(arr, dict) for arr in arrivals["data"]), (
        "All elements in arrivals should be dictionaries"
    )


@pytest.mark.asyncio
async def test_get_route(beograd_api):
    actual_line_number = "1007"
    route = await beograd_api.get_route(actual_line_number)
    assert route, "Route should not be empty"
    assert isinstance(route, dict), "Route should be a dictionary"

    # Check structure of route
    assert "line_route" in route, "Route should contain 'line_route'"
    assert isinstance(route["line_route"], list), "'line_route' should be a list"


@pytest.mark.asyncio
async def test_get_route_version(beograd_api):
    actual_line_number = "1007"
    route_version = await beograd_api.get_route_version(actual_line_number)
    assert route_version, "Route version should not be empty"
    assert isinstance(route_version, dict), "Route version should be a dictionary"
    # Check for success key and its value
    assert "success" in route_version, "Route version should contain 'success' key"
    assert route_version["success"] is True, "'success' should be True"

    # Check structure of route version
    assert "data" in route_version, "Route version should contain 'data'"
    assert isinstance(route_version["data"], dict), "'data' should be a dictionary"
    assert "line_route_version" in route_version["data"], (
        "Route version data should contain 'line_route_version'"
    )
    assert isinstance(route_version["data"]["line_route_version"], int), (
        "'line_route_version' should be an integer"
    )


@pytest.mark.asyncio
async def test_get_line_numbers(beograd_api):
    station_ids = ["20495", "20494"]

    line_numbers = await beograd_api.get_line_numbers(station_ids)
    assert line_numbers, "Line numbers should not be empty"
    assert isinstance(line_numbers, dict), "Line numbers should be a dictionary"

    # Check for success key and its value
    assert "success" in line_numbers, "Line numbers should contain 'success' key"
    assert line_numbers["success"] is True, "'success' should be True"

    # Check structure of line numbers
    assert "data" in line_numbers, "Line numbers should contain 'data'"
    assert isinstance(line_numbers["data"], list), "'data' should be a list"
    for item in line_numbers["data"]:
        assert isinstance(item, dict), "Each item in 'data' should be a dictionary"
        assert "line_numbers" in item, "Each item should contain 'line_numbers'"
        assert isinstance(item["line_numbers"], list), "'line_numbers' should be a list"
