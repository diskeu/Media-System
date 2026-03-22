# https://fastapi.tiangolo.com/advanced/behind-a-proxy/#redirects-with-https -> Fast-Api-Proxys-Doc
from Backend.App.Exceptions.Base_Exceptions import InvalidIpError

# IP-processing-Lib
from ipaddress import (
    IPv4Address,
    IPv6Address)
from ipaddress import ip_address, ip_network 
from geoip2.database import Reader as GeoDBReader

# Fast-Api related stuff
from fastapi import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import json

class IPBlockMiddleware(BaseHTTPMiddleware):
    """Class for Blocking IPs via a block_list"""
    def __init__(self, app, block_list_location: str):
        # Loading Json
        with open(block_list_location, "r") as IP_BLOCK_LIST:
            self.IP_BLOCK_LIST = json.load(IP_BLOCK_LIST)

        self.IP_BLOCK_LIST["BLOCKED_NETWORKS"] = [ip_network(net_ip) for net_ip in self.IP_BLOCK_LIST["BLOCKED_NETWORKS"]]

        self.reader = GeoDBReader("GeoLite2-City.mmdb")

    def _get_Ip(self, ip) -> IPv4Address | IPv6Address | InvalidIpError:
        try: client_ip = ip_address(ip)
        except ValueError: return InvalidIpError
        return client_ip

    def get_client_ip(self, request: dict) -> IPv4Address | IPv6Address | InvalidIpError:
        """
        Parsed a request returns the correct Ip-adress
        The 'x-forwarded-for' - Ip 'll be used if definied
        Else request.client.host 'll be used
        """
        # No proxy behaviour
        client_ip = self._get_Ip

        forwarded_for = request.headers.get("x-forwarded-for", None)
        if not forwarded_for: return client_ip # Ip | InvalidIpError
    
        client_ip, _, _ = forwarded_for.partitition[", "] # first Ip is the clientIp by default
        return client_ip

    async def ip_block_middleware(self, request, call_next: callable) -> JSONResponse:
        # Validate Ip
        client_ip = self.get_client_ip(request)
        if isinstance(client_ip, InvalidIpError):
            return JSONResponse(status_code=403, content={"error": "Invalid Ip"})
        
        # Loading Geo Data
        response = self.reader.city(str(client_ip))

        iso_code = response.country.iso_code
        subdivision = response.subdivisions.most_specific.name

        # ----- Validating Location -----
        if iso_code in self.IP_BLOCK_LIST["BLOCKED_COUNTRYS"]:
            return JSONResponse(status_code=403, content={"error": "Blocked Country"})
        
        if str(client_ip) in self.IP_BLOCK_LIST["blocked_ips"]:
            return JSONResponse(status_code=403, content={"error": "Blocked IP"})

        if subdivision in self.IP_BLOCK_LIST["BLOCKED_REGIONS"]:
            return JSONResponse(status_code=403, content={"error": "Blocked Region"})
        
        for net_ip in self.IP_BLOCK_LIST["BLOCKED_NETWORKS"]:
            if client_ip in net_ip:
                return JSONResponse(status_code=403, content={"error": "Blocked Network", "Network Adress": net_ip})
                
        call_next(request)
    