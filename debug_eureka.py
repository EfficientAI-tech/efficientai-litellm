# debug_eureka.py
import asyncio
import logging
import os

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("eureka_debug")

# Import the Eureka integration class from LiteLLM
from litellm.proxy.eureka_integration import EurekaIntegration, eureka_error_handler

async def test_eureka_registration():
    try:
        # Use the same config values you have in your litellm_config.yaml
        eureka_integration = EurekaIntegration(
            app_name="litellm-proxy",
            host="localhost",  # or whatever host you're using
            port=4000,
            eureka_server_urls="http://localhost:8762/eureka",
            # Add any other parameters from your config
            on_error=eureka_error_handler
        )
        
        logger.debug("Attempting to register with Eureka...")
        await eureka_integration.register()
        logger.debug("Successfully registered with Eureka")
        
        # Wait a bit to keep the process alive
        await asyncio.sleep(50)
        
        # Deregister
        logger.debug("Attempting to deregister from Eureka...")
        await eureka_integration.stop()
        logger.debug("Successfully deregistered from Eureka")
    
    except Exception as e:
        logger.error(f"Error during Eureka registration: {str(e)}", exc_info=True)

# Run the test
if __name__ == "__main__":
    asyncio.run(test_eureka_registration())