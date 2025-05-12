#!/usr/bin/env python3
# update_cleanup.py - Update the cleanup_router_config_variables function

with open('litellm/proxy/proxy_server.py', 'r') as f:
    content = f.readlines()

# Find the cleanup_router_config_variables function
for i, line in enumerate(content):
    if "def cleanup_router_config_variables():" in line:
        # Update the global declaration line
        if "global " in content[i+1]:
            content[i+1] = content[i+1].rstrip() + ", eureka_integration\n"
        
        # Find where the variables are set to None
        for j in range(i+2, len(content)):
            if "prisma_client = None" in content[j]:
                # Add eureka_integration = None after it
                content.insert(j+1, "    eureka_integration = None\n")
                break
        break

# Write back to file
with open('litellm/proxy/proxy_server.py', 'w') as f:
    f.writelines(content)

print("Cleanup function updated successfully") 