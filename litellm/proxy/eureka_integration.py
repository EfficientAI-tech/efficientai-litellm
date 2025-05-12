"""
Eureka integration for LiteLLM Proxy Server. 
This module helps register the LiteLLM proxy with Eureka service registry as a microservice.
"""

import asyncio
import os
import socket
import logging
from typing import Optional, List, Dict, Any, Union, Callable

try:
    import py_eureka_client.eureka_client as eureka_client
    from py_eureka_client.eureka_client import EurekaClient
    HAS_EUREKA = True
except ImportError:
    HAS_EUREKA = False

# Setup logger for Eureka integration
eureka_logger = logging.getLogger("litellm.proxy.eureka")
eureka_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
eureka_logger.addHandler(handler)

# Import verbose_proxy_logger if available
try:
    from litellm._logging import verbose_proxy_logger
except ImportError:
    # Define a fallback logger if the import fails
    verbose_proxy_logger = logging.getLogger("litellm.proxy.verbose")
    verbose_proxy_logger.setLevel(logging.INFO)
    verbose_proxy_logger.addHandler(handler)

class EurekaIntegration:
    def __init__(
        self,
        app_name: str,
        host: str,
        port: int,
        eureka_server_urls: Union[str, List[str]],
        health_check_url: Optional[str] = None,
        status_page_url: Optional[str] = None,
        home_page_url: Optional[str] = None,
        instance_id: Optional[str] = None,
        zone: Optional[str] = None,
        eureka_availability_zones: Optional[Dict[str, str]] = None,
        data_center_name: Optional[str] = "MyOwn",
        ip_addr: Optional[str] = None,
        on_error: Optional[Callable[[str, Exception], None]] = None
    ):
        """
        Initialize Eureka integration for LiteLLM proxy.

        Args:
            app_name: The name of the application to register with Eureka
            host: Hostname of the service
            port: Port number the service runs on
            eureka_server_urls: Comma-separated string or list of Eureka server URLs
            health_check_url: URL for health checks (default: None, will be constructed)
            status_page_url: URL for status page (default: None, will be constructed)
            home_page_url: URL for home page (default: None, will be constructed)
            instance_id: Unique identifier for this instance (default: None, will be constructed)
            zone: Availability zone (if using zones)
            eureka_availability_zones: Dict mapping zone names to Eureka server URLs
            data_center_name: Name of the data center (default: "MyOwn")
            ip_addr: IP address of the service (default: None, will be detected)
            on_error: Callback function for error handling
        """
        eureka_logger.debug("Initializing EurekaIntegration")
        if not HAS_EUREKA:
            eureka_logger.error("py-eureka-client is required for Eureka integration")
            raise ImportError("py-eureka-client is required for Eureka integration. Install with 'pip install py-eureka-client'")
        
        self.app_name = app_name
        self.host = host
        self.port = port
        self.eureka_client = None
        self.instance_id = instance_id or f"{socket.gethostname()}:{app_name}:{port}"
        
        # Get IP address if not provided
        self.ip_addr = ip_addr or self._get_ip()
        
        # Construct URLs if not provided
        base_url = f"http://{self.host}:{self.port}"
        self.health_check_url = health_check_url or f"{base_url}/health"
        self.status_page_url = status_page_url or f"{base_url}/info"
        self.home_page_url = home_page_url or base_url
        
        # Error handler
        self.on_error = on_error
        
        # Eureka server configuration
        self.eureka_server_urls = eureka_server_urls
        self.zone = zone
        self.eureka_availability_zones = eureka_availability_zones
        self.data_center_name = data_center_name
        
        eureka_logger.debug(f"EurekaIntegration initialized with app_name={app_name}, host={host}, port={port}")
    
    def _get_ip(self) -> str:
        """Get the local non-loopback IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback to localhost if unable to determine IP
            return "127.0.0.1"
    
    async def register(self) -> None:
        """Register the service with Eureka"""
        try:
            eureka_logger.debug("Starting Eureka registration process")
            if isinstance(self.eureka_server_urls, list):
                eureka_server = ",".join(self.eureka_server_urls)
                eureka_logger.debug(f"Using Eureka server URLs from list: {eureka_server}")
            else:
                eureka_server = self.eureka_server_urls
                eureka_logger.debug(f"Using Eureka server URL: {eureka_server}")
            
            # Initialize client with zone information if provided
            if self.zone and self.eureka_availability_zones:
                eureka_logger.debug(f"Initializing with zones: zone={self.zone}, availability_zones={self.eureka_availability_zones}")
                self.eureka_client = await eureka_client.init_async(
                    eureka_availability_zones=self.eureka_availability_zones,
                    zone=self.zone,
                    app_name=self.app_name,
                    instance_id=self.instance_id,
                    instance_host=self.host,
                    instance_ip=self.ip_addr,
                    instance_port=self.port,
                    data_center_name=self.data_center_name,
                    status_page_url=self.status_page_url,
                    health_check_url=self.health_check_url,
                    home_page_url=self.home_page_url,
                    on_error=self.on_error
                )
            else:
                # Standard initialization
                eureka_logger.debug(f"Initializing standard Eureka client with server={eureka_server}")
                self.eureka_client = await eureka_client.init_async(
                    eureka_server=eureka_server,
                    app_name=self.app_name,
                    instance_id=self.instance_id,
                    instance_host=self.host,
                    instance_ip=self.ip_addr,
                    instance_port=self.port,
                    data_center_name=self.data_center_name,
                    status_page_url=self.status_page_url,
                    health_check_url=self.health_check_url,
                    home_page_url=self.home_page_url,
                    on_error=self.on_error
                )
            
            eureka_logger.info(f"Successfully registered {self.app_name} with Eureka at {eureka_server}")
            verbose_proxy_logger.info(f"Successfully registered {self.app_name} with Eureka at {eureka_server}")
        except Exception as e:
            eureka_logger.error(f"Failed to register with Eureka: {str(e)}", exc_info=True)
            verbose_proxy_logger.error(f"Failed to register with Eureka: {str(e)}")
            if self.on_error:
                self.on_error("EUREKA_REGISTRATION_ERROR", e)
            else:
                raise
    
    async def stop(self) -> None:
        """Stop the Eureka client and deregister the service"""
        if self.eureka_client:
            try:
                eureka_logger.debug("Deregistering from Eureka")
                await self.eureka_client.stop()
                eureka_logger.info(f"Successfully deregistered {self.app_name} from Eureka")
                verbose_proxy_logger.info(f"Successfully deregistered {self.app_name} from Eureka")
            except Exception as e:
                eureka_logger.error(f"Error deregistering from Eureka: {str(e)}", exc_info=True)
                verbose_proxy_logger.error(f"Error deregistering from Eureka: {str(e)}")
                if self.on_error:
                    self.on_error("EUREKA_DEREGISTRATION_ERROR", e)

def eureka_error_handler(err_type: str, err: Exception) -> None:
    """Default error handler for Eureka client errors"""
    eureka_logger.error(f"Eureka error ({err_type}): {str(err)}", exc_info=True)
    verbose_proxy_logger.error(f"Eureka error ({err_type}): {str(err)}")