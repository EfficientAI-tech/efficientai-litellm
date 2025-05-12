#!/usr/bin/env python3
"""
Test script focused only on LiteLLM's Eureka integration
"""
import asyncio
import logging
import sys
import os
import yaml
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)
logger = logging.getLogger("litellm_eureka_test")

# Check for required package
try:
    import py_eureka_client
    logger.info("✅ py-eureka-client is installed")
except ImportError:
    logger.error("❌ py-eureka-client is NOT installed. Run: pip install py-eureka-client")
    sys.exit(1)

# Read config
def read_config():
    try:
        with open('litellm_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"❌ Error reading config file: {e}")
        return None

# A simplified version of EurekaIntegration class adapted from litellm/proxy/eureka_integration.py
class SimplifiedEurekaIntegration:
    def __init__(
        self,
        app_name: str,
        host: str,
        port: int,
        eureka_server_urls: str,
        health_check_url: str = None,
        status_page_url: str = None,
        home_page_url: str = None,
        on_error = None
    ):
        self.app_name = app_name
        self.host = host
        self.port = port
        self.eureka_server_urls = eureka_server_urls
        self.health_check_url = health_check_url or f"http://{host}:{port}/health"
        self.status_page_url = status_page_url or f"http://{host}:{port}/info"
        self.home_page_url = home_page_url or f"http://{host}:{port}/"
        self.on_error = on_error
        self.eureka_client = None
        
    def _get_ip(self) -> str:
        import socket
        try:
            # Get local IP by creating a socket and connecting to a public address
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception as e:
            if self.on_error:
                self.on_error("ip_lookup", e)
            return self.host  # fallback to hostname

    async def register(self) -> None:
        try:
            import py_eureka_client.eureka_client as eureka_client
            
            # Get the IP address
            ip_addr = self._get_ip()
            logger.info(f"Using IP address for registration: {ip_addr}")
            
            # Initialize Eureka client
            self.eureka_client = await eureka_client.init_async(
                eureka_server=self.eureka_server_urls,
                app_name=self.app_name,
                instance_port=self.port,
                instance_host=ip_addr,
                instance_ip=ip_addr,
                status_page_url=self.status_page_url,
                health_check_url=self.health_check_url,
                home_page_url=self.home_page_url
            )
            
            logger.info(f"Successfully registered {self.app_name} with Eureka at {self.eureka_server_urls}")
        except Exception as e:
            logger.error(f"Failed to register with Eureka: {str(e)}")
            if self.on_error:
                self.on_error("registration", e)
            raise

    async def stop(self) -> None:
        try:
            if self.eureka_client:
                await self.eureka_client.stop()
                logger.info(f"Successfully deregistered {self.app_name} from Eureka")
        except Exception as e:
            logger.error(f"Failed to deregister from Eureka: {str(e)}")
            if self.on_error:
                self.on_error("deregistration", e)

# Main test function
async def test_litellm_eureka():
    config = read_config()
    if not config:
        return
    
    # Extract Eureka settings
    eureka_settings = config.get('general_settings', {}).get('eureka', {})
    if not eureka_settings:
        logger.error("❌ No Eureka settings found in litellm_config.yaml")
        return
    
    logger.info(f"🔍 Found Eureka settings: {eureka_settings}")
    
    # Extract settings
    app_name = eureka_settings.get('app_name', 'litellm-proxy')
    host = eureka_settings.get('host', 'localhost')
    port = eureka_settings.get('port', 4000)
    eureka_server_urls = eureka_settings.get('eureka_server_urls', 'http://localhost:8762/eureka')
    
    # Test connection to Eureka server
    import urllib.request
    import urllib.error
    
    try:
        # Remove /eureka suffix for the connection test
        if isinstance(eureka_server_urls, str):
            test_url = eureka_server_urls.split('/eureka')[0]
            logger.info(f"🔄 Testing connection to Eureka server at: {test_url}")
            response = urllib.request.urlopen(test_url, timeout=5)
            status = response.status
            logger.info(f"✅ Connection to Eureka server successful! Status code: {status}")
        else:
            # Handle multiple Eureka servers
            for url in eureka_server_urls:
                test_url = url.split('/eureka')[0]
                logger.info(f"🔄 Testing connection to Eureka server at: {test_url}")
                response = urllib.request.urlopen(test_url, timeout=5)
                status = response.status
                logger.info(f"✅ Connection to Eureka server successful! Status code: {status}")
    except urllib.error.URLError as e:
        logger.error(f"❌ Connection to Eureka server failed! Error: {e}")
        logger.error("❗ Make sure your Eureka server is running and accessible")
        return
    
    # Test Eureka integration
    integration = None
    try:
        def error_handler(error_type, exception):
            logger.error(f"❌ Eureka error: {error_type} - {exception}")
        
        logger.info(f"🔄 Creating Eureka integration instance with app_name={app_name}, host={host}, port={port}")
        
        integration = SimplifiedEurekaIntegration(
            app_name=app_name,
            host=host,
            port=port,
            eureka_server_urls=eureka_server_urls,
            on_error=error_handler
        )
        
        logger.info("🔄 Registering with Eureka...")
        await integration.register()
        logger.info("✅ Successfully registered with Eureka!")
        
        # Wait for the service to be registered
        logger.info("⏳ Waiting for 10 seconds...")
        await asyncio.sleep(10)
        
        # Deregister
        logger.info("🔄 Deregistering from Eureka...")
        await integration.stop()
        logger.info("✅ Successfully deregistered from Eureka!")
        
    except Exception as e:
        logger.error(f"❌ Error during Eureka test: {str(e)}")
        traceback.print_exc()
    finally:
        # Extra safety check for deregistration
        if integration is not None:
            try:
                logger.info("🔄 Making one final deregistration attempt in finally block")
                await integration.stop()
            except Exception as e:
                logger.error(f"❌ Final deregistration attempt failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_litellm_eureka()) 