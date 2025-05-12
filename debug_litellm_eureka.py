#!/usr/bin/env python3
"""
Debug script to trace through LiteLLM proxy startup and verify Eureka registration
"""
import os
import sys
import asyncio
import logging
import yaml
import subprocess
import time
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("debug_litellm_eureka")

# Update eureka_integration.py to add debug logging
def add_debug_logging_to_eureka_integration():
    eureka_path = os.path.join("litellm", "proxy", "eureka_integration.py")
    
    if not os.path.exists(eureka_path):
        logger.error(f"Cannot find {eureka_path}")
        return False
    
    try:
        with open(eureka_path, 'r') as f:
            content = f.read()
        
        # Check if we've already modified this file
        if "DEBUG ADDED BY debug_litellm_eureka.py" in content:
            logger.info("Debug logging already added to eureka_integration.py")
            return True
        
        # Add debug logging to the register method
        content = content.replace(
            "async def register(self) -> None:",
            '''async def register(self) -> None:
        print("DEBUG ADDED BY debug_litellm_eureka.py: eureka_integration.register() called")
        import traceback
        print(f"Called from:\\n{traceback.format_stack()}")'''
        )
        
        # Add debug logging to the init method
        content = content.replace(
            "def __init__(",
            '''def __init__(
        print("DEBUG ADDED BY debug_litellm_eureka.py: EurekaIntegration instantiated")
        import traceback 
        print(f"Initialized from:\\n{traceback.format_stack()}")'''
        )
        
        # Write the modified content back to the file
        with open(eureka_path, 'w') as f:
            f.write(content)
        
        logger.info("Added debug logging to eureka_integration.py")
        return True
    except Exception as e:
        logger.error(f"Failed to add debug logging to eureka_integration.py: {e}")
        return False

def add_debug_logging_to_proxy_server():
    proxy_path = os.path.join("litellm", "proxy", "proxy_server.py")
    
    if not os.path.exists(proxy_path):
        logger.error(f"Cannot find {proxy_path}")
        return False
    
    try:
        with open(proxy_path, 'r') as f:
            content = f.read()
        
        # Check if we've already modified this file
        if "DEBUG ADDED BY debug_litellm_eureka.py" in content:
            logger.info("Debug logging already added to proxy_server.py")
            return True
        
        # Add a debug statement to check HAS_EUREKA
        content = content.replace(
            "if HAS_EUREKA and general_settings.get(\"eureka\", None) is not None:",
            '''print("DEBUG ADDED BY debug_litellm_eureka.py: checking Eureka conditions")
            print(f"HAS_EUREKA={HAS_EUREKA}, eureka_settings={general_settings.get('eureka', None)}")
            if HAS_EUREKA and general_settings.get("eureka", None) is not None:
                print("DEBUG ADDED BY debug_litellm_eureka.py: Eureka conditions met, will initialize")'''
        )
        
        # Write the modified content back to the file
        with open(proxy_path, 'w') as f:
            f.write(content)
        
        logger.info("Added debug logging to proxy_server.py")
        return True
    except Exception as e:
        logger.error(f"Failed to add debug logging to proxy_server.py: {e}")
        return False

# Start LiteLLM proxy with debug flags
def start_proxy():
    # Find the proxy CLI script
    if os.path.exists(os.path.join("litellm", "proxy", "proxy_cli.py")):
        proxy_script = os.path.join("litellm", "proxy", "proxy_cli.py")
    else:
        proxy_script = "litellm"  # assume it's installed in the environment
    
    logger.info(f"Starting LiteLLM proxy with {proxy_script}")
    
    cmd = [
        sys.executable,
        proxy_script,
        "--config", "litellm_config.yaml",
        "--debug",
        "--verbose",
    ]
    
    try:
        # Add appropriate environment variables to increase verbosity
        env = os.environ.copy()
        env["LITELLM_VERBOSE"] = "1"
        
        # Run the process and capture the output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )
        
        # Process will run in the background while we monitor its output
        logger.info("Proxy started, monitoring for Eureka-related messages...")
        
        # Read output continuously for 10 seconds
        start_time = time.time()
        output = []
        
        while time.time() - start_time < 10:
            # Read a line from the process output
            line = process.stdout.readline()
            if line:
                output.append(line)
                print(line.strip())  # Display in real-time
                
                # If we see Eureka-related messages, note them
                if "eureka" in line.lower() or "HAS_EUREKA" in line:
                    logger.info(f"Found Eureka-related message: {line.strip()}")
            
            # Check if process is still running
            if process.poll() is not None:
                break
                
        # Check if the process is still running
        if process.poll() is None:
            logger.info("Process still running, sending termination signal...")
            
            # Send SIGINT to gracefully terminate
            process.send_signal(signal.SIGINT)
            
            # Wait for the process to exit and collect any remaining output
            try:
                remaining_output, _ = process.communicate(timeout=5)
                if remaining_output:
                    output.append(remaining_output)
            except subprocess.TimeoutExpired:
                # If it doesn't exit gracefully, force kill
                process.kill()
                remaining_output, _ = process.communicate()
                if remaining_output:
                    output.append(remaining_output)
        else:
            # Process already exited, get any remaining output
            remaining_output, _ = process.communicate()
            if remaining_output:
                output.append(remaining_output)
            
            if process.returncode != 0:
                logger.error(f"Proxy exited with error code {process.returncode}")
        
        # Save output to a file for analysis
        with open("litellm_eureka_debug_output.log", "w") as f:
            f.write("".join(output))
        
        logger.info("Saved output to litellm_eureka_debug_output.log")
        
    except Exception as e:
        logger.error(f"Error starting/monitoring proxy: {e}")

# Main function
async def main():
    # Add debug logging
    add_debug_logging_to_eureka_integration()
    add_debug_logging_to_proxy_server()
    
    # Start proxy and monitor
    start_proxy()
    
    logger.info("Debug completed")

if __name__ == "__main__":
    asyncio.run(main()) 