# kasa_smart_home_server.py

# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================
from mcp.server.fastmcp import FastMCP
from kasa import SmartPlug # Used for direct connection to Kasa devices
import asyncio             # For asynchronous operations
import sys                 # For system-related functions like exit
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
load_dotenv()

# ==============================================================================
# SECTION 2: CONFIGURATION
# ==============================================================================
print("CONFIG: Initializing Kasa Smart Home MCP Server script...")

# Configure your Kasa device's exact details here.
KASA_DEVICE_ALIAS = "Outdoor plug"       # <--- SET YOUR KASA DEVICE'S ALIAS HERE
KASA_DEVICE_IP = os.getenv("KASA_DEVICE_IP")    # <--- SET YOUR KASA DEVICE'S IP HERE

# ==============================================================================
# SECTION 3: MCP SERVER SETUP
# ==============================================================================
mcp = FastMCP("KasaSmartHomeServer")
print("STATUS: MCP server 'KasaSmartHomeServer' instance created.")

# Cache for the SmartPlug object to avoid recreating it on every call.
# This will hold the single SmartPlug instance for your configured device.
kasa_plug_instance: Optional[SmartPlug] = None

async def get_kasa_plug() -> Optional[SmartPlug]:
    """Helper function to get or create the SmartPlug instance."""
    global kasa_plug_instance
    print(f"DEBUG: Attempting to get SmartPlug instance for '{KASA_DEVICE_ALIAS}' at {KASA_DEVICE_IP}.")

    if kasa_plug_instance:
        print(f"DEBUG: SmartPlug instance already in cache. Attempting to update its state.")
        try:
            await kasa_plug_instance.update() # Refresh state to ensure connection is live
            return kasa_plug_instance
        except Exception as e:
            print(f"WARNING: Could not update cached plug '{KASA_DEVICE_ALIAS}': {e}. Attempting re-creation.")
            kasa_plug_instance = None # Invalidate cache if connection is stale

    # If not in cache or update failed, create a new SmartPlug object
    try:
        print(f"DEBUG: Creating new SmartPlug object for '{KASA_DEVICE_ALIAS}' at IP: {KASA_DEVICE_IP}.")
        plug = SmartPlug(KASA_DEVICE_IP)
        await plug.update() # Test connection and populate initial state
        kasa_plug_instance = plug # Cache the new object
        print(f"DEBUG: Successfully created and cached SmartPlug object for '{KASA_DEVICE_ALIAS}'.")
        return plug
    except Exception as e:
        print(f"ERROR: Failed to connect directly to Kasa device at {KASA_DEVICE_IP}: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==============================================================================
# SECTION 4: MCP TOOLS DEFINITIONS
# ==============================================================================

@mcp.tool()
async def turn_kasa_device_on() -> Dict:
    """
    Turns on the configured Kasa smart plug.
    Returns the device's current state.
    """
    print(f"DEBUG: MCP Tool 'turn_kasa_device_on' called for '{KASA_DEVICE_ALIAS}'.")
    plug = await get_kasa_plug()
    if plug:
        try:
            print(f"DEBUG: Attempting to turn on Kasa device: '{plug.alias}' (IP: {plug.host})")
            await plug.turn_on()
            await plug.update() # Get updated state
            print(f"DEBUG: Successfully turned on device '{plug.alias}'. New state: is_on={plug.is_on}")
            return {"alias": plug.alias, "is_on": plug.is_on, "status": "success"}
        except Exception as e:
            print(f"ERROR: Error turning on device '{plug.alias}': {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to turn on device '{plug.alias}': {e}"}
    print(f"ERROR: Kasa device '{KASA_DEVICE_ALIAS}' not found or unreachable for 'turn_on' operation.")
    return {"error": f"Kasa device '{KASA_DEVICE_ALIAS}' not found or unreachable."}

@mcp.tool()
async def turn_kasa_device_off() -> Dict:
    """
    Turns off the configured Kasa smart plug.
    Returns the device's current state.
    """
    print(f"DEBUG: MCP Tool 'turn_kasa_device_off' called for '{KASA_DEVICE_ALIAS}'.")
    plug = await get_kasa_plug()
    if plug:
        try:
            print(f"DEBUG: Attempting to turn off Kasa device: '{plug.alias}' (IP: {plug.host})")
            await plug.turn_off()
            await plug.update() # Get updated state
            print(f"DEBUG: Successfully turned off device '{plug.alias}'. New state: is_on={plug.is_on}")
            return {"alias": plug.alias, "is_on": plug.is_on, "status": "success"}
        except Exception as e:
            print(f"ERROR: Error turning off device '{plug.alias}': {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to turn off device '{plug.alias}': {e}"}
    print(f"ERROR: Kasa device '{KASA_DEVICE_ALIAS}' not found or unreachable for 'turn_off' operation.")
    return {"error": f"Kasa device '{KASA_DEVICE_ALIAS}' not found or unreachable."}

@mcp.tool()
async def get_kasa_device_status() -> Dict:
    """
    Gets the current power status of the configured Kasa smart plug.
    Returns the device's current state.
    """
    print(f"DEBUG: MCP Tool 'get_kasa_device_status' called for '{KASA_DEVICE_ALIAS}'.")
    plug = await get_kasa_plug()
    if plug:
        try:
            print(f"DEBUG: Attempting to get status for Kasa device: '{plug.alias}' (IP: {plug.host})")
            await plug.update() # Refresh state
            print(f"DEBUG: Successfully retrieved status for device '{plug.alias}'. Is On: {plug.is_on}")
            return {"alias": plug.alias, "is_on": plug.is_on, "status": "success"}
        except Exception as e:
            print(f"ERROR: Error getting status for device '{plug.alias}': {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to get status for device '{plug.alias}': {e}"}
    print(f"ERROR: Kasa device '{KASA_DEVICE_ALIAS}' not found or unreachable for 'get_status' operation.")
    return {"error": f"Kasa device '{KASA_DEVICE_ALIAS}' not found or unreachable."}

@mcp.tool()
async def list_kasa_devices() -> List[Dict]:
    """
    Lists the configured Kasa smart plug and its current status.
    Returns a list containing details of the plug if reachable.
    """
    print("DEBUG: MCP Tool 'list_kasa_devices' called.")
    device_list = []
    plug = await get_kasa_plug() # Try to connect to the single configured plug
    if plug:
        print(f"DEBUG: Configured Kasa device '{plug.alias}' reachable. Adding to list.")
        device_list.append({"alias": plug.alias, "is_on": plug.is_on, "host": plug.host})
    else:
        print(f"WARNING: Configured Kasa device '{KASA_DEVICE_ALIAS}' is not reachable for listing.")
    
    print(f"DEBUG: Finished listing Kasa devices. Total listed: {len(device_list)}")
    return device_list

# ==============================================================================
# SECTION 5: SERVER EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("STATUS: Starting Kasa Smart Home MCP Server.")
    try:
        mcp.run(transport="streamable-http")
        print("STATUS: Kasa Smart Home MCP Server started successfully on port 8000.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to start Kasa Smart Home MCP Server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)