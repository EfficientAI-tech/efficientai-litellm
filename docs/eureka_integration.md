# LiteLLM Proxy with Eureka Service Registry Integration

This guide explains how to integrate LiteLLM proxy with Eureka service registry for microservice deployments.

## Overview

When running LiteLLM proxy in a microservice architecture, you can register it with Eureka service registry to enable service discovery, load balancing, and failover capabilities. This allows other services to dynamically discover and communicate with the LiteLLM proxy without hardcoding URLs.

## Prerequisites

1. A running Eureka server (can be standalone or part of a Spring Cloud environment)
2. LiteLLM proxy server installed with required dependencies
3. Install the py-eureka-client library:

```bash
pip install py-eureka-client
```

## Configuration

### Basic Setup

To enable Eureka integration, you need to add Eureka configuration to your `config.yaml` file. Here's a minimal example:

```yaml
general_settings:
  eureka:
    app_name: litellm-proxy
    host: localhost
    port: 4000
    eureka_server_urls: http://eureka-server:8761/eureka
```

### Complete Configuration

Here's a more comprehensive configuration example showing all available options:

```yaml
general_settings:
  eureka:
    # Required settings
    app_name: litellm-proxy                                # Application name to register with Eureka
    host: ${LITELLM_SERVICE_HOST}                          # Host name or IP address of this service
    port: ${LITELLM_SERVICE_PORT}                          # Port the service is running on
    eureka_server_urls: ${EUREKA_SERVER_URLS}              # Eureka server URLs, comma-separated
    
    # Optional settings
    instance_id: litellm-proxy-instance-1                  # Custom instance ID (auto-generated if not provided)
    data_center_name: MyOwn                                # Data center name (default: "MyOwn")
    health_check_url: http://localhost:4000/health         # Health check URL (auto-generated if not provided)
    status_page_url: http://localhost:4000/info            # Status page URL (auto-generated if not provided)
    home_page_url: http://localhost:4000                   # Home page URL (auto-generated if not provided)
    
    # Multi-zone deployment (optional)
    zone: us-east-1c                                       # Availability zone
    eureka_availability_zones:                             # Mapping of zones to Eureka servers
      us-east-1c: http://eureka-1:8761/eureka,http://eureka-2:8761/eureka
      us-east-1d: http://eureka-3:8761/eureka
```

## Environment Variables

You can use environment variables in your configuration to make it more portable:

```yaml
environment_variables:
  EUREKA_SERVER_URLS: http://eureka-server:8761/eureka
  LITELLM_SERVICE_HOST: localhost
  LITELLM_SERVICE_PORT: 4000
```

## Running LiteLLM with Eureka Integration

When you start the LiteLLM proxy server with a configuration file that includes Eureka settings, it will automatically register with the Eureka server:

```bash
litellm --config config.yaml
```

## How it Works

1. When LiteLLM proxy starts, it checks for Eureka configuration in the `general_settings` section
2. If Eureka configuration is found, it creates an instance of `EurekaIntegration` and registers with the Eureka server
3. LiteLLM proxy regularly sends heartbeats to Eureka to maintain its registration
4. When LiteLLM proxy shuts down, it deregisters from Eureka

## Accessing LiteLLM from Other Services

Other services can discover and use the LiteLLM proxy via Eureka service registry:

### From Java/Spring Services

```java
@FeignClient(name = "litellm-proxy")
public interface LiteLLMClient {
    @PostMapping("/chat/completions")
    ChatCompletionResponse getChatCompletions(@RequestBody ChatCompletionRequest request);
}
```

### From Python Services

```python
import py_eureka_client.eureka_client as eureka_client

# Initialize eureka client
eureka_client.init(eureka_server="http://eureka-server:8761/eureka",
                  app_name="my-python-service")

# Discover litellm-proxy service
service_url = eureka_client.get_service_url(app_name="litellm-proxy")

# Now you can make requests to the service
import requests
response = requests.post(f"{service_url}/chat/completions", json={
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello world"}]
})
```

## Full Example Configuration

See the [examples/eureka_config.yaml](../examples/eureka_config.yaml) file for a complete working example.

## Troubleshooting

### Registration Issues

If LiteLLM is not registering with Eureka, check:

1. Eureka server is running and accessible
2. The `eureka_server_urls` is correctly configured
3. The `host` and `port` values are correctly set
4. Check LiteLLM proxy logs for any connection errors

### Discovery Issues

If other services can't discover LiteLLM, check:

1. The application name in Eureka matches (`app_name` in configuration)
2. LiteLLM proxy is still registered with Eureka (check Eureka dashboard)
3. The client service is correctly configured to use Eureka for service discovery

## Additional Resources

- [Spring Cloud Netflix Eureka](https://cloud.spring.io/spring-cloud-netflix/reference/html/)
- [py-eureka-client Documentation](https://github.com/keijack/python-eureka-client) 