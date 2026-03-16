from ipaddress import (
    IPv4Address,
    IPv6Address
)
from ipaddress import ip_address
from fastapi import JSONResponse
import geoip2.database.Reader as geo_db_reader
import json

async def ip_block_middleware(request, call_next: callable) -> JSONResponse:
    try:
        ip: IPv4Address | IPv6Address = ip_address(request.client.host)
    except ValueError:
        return JSONResponse(status_code=403, content={"error": "Invalid Ip"})
    with open("Backend/App/middleware/ip_block/ip_block_list.json", "r") as ip_block_list:
        ip_block_list = json.loads()
    
    reader = geo_db_reader("GeoLite2-City.mmdb")
    response = reader.city(ip)

    iso_code = response.country.iso_code
    subdivision = response.subdivisions.most_specific.name

    # ----- Validating Location -----
    if iso_code in ip_block_list["BLOCKED_COUNTRYS"]:
        return JSONResponse(status_code=403, content={"error": "Blocked Country"})
    
    if ip in ip_block_list["BLOCKED_IPS"]:
        return JSONResponse(status_code=403, content={"error": "Blocked IP"})

    if subdivision in ip_block_list["BLOCKED_REGIONS"]:
        return JSONResponse(status_code=403, content={"error": "Blocked Region"})
    