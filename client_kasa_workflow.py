# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
import asyncio
from dotenv import load_dotenv
import os
import sys

# ==============================================================================
# SECTION 2: ENVIRONMENT SETUP
# ==============================================================================
print("Initializing client_kasa_workflow script...")

load_dotenv()
print("STATUS: Environment variables loaded.")

# Ensure GROQ_API_KEY is set
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("CRITICAL ERROR: GROQ_API_KEY environment variable not set. Please set it in your .env file or environment.")
    sys.exit(1)
os.environ["GROQ_API_KEY"] = groq_api_key
print("STATUS: GROQ_API_KEY confirmed.")

# ==============================================================================
# SECTION 3: MAIN WORKFLOW
# ==============================================================================
async def main():
    print("STATUS: Starting client_kasa_workflow main function.")
    try:
        print("DEBUG: Initializing MultiServerMCPClient with Kasa server configuration.")
        client = MultiServerMCPClient(
            {
                "kasa_home": {
                    "transport": "streamable_http",
                    "url": "http://localhost:8000/mcp",
                }
            }
        )
        print('STATUS: MultiServerMCPClient instance created.')
        
        print('STATUS: Attempting to get tools from connected MCP servers...')
        tools = await client.get_tools()
        if tools:
            print(f'STATUS: Successfully retrieved {len(tools)} tools from MCP servers.')
            for tool in tools:
                print(f"  DEBUG: - Tool: {tool.name}, Description: {tool.description}")
        else:
            print("WARNING: No tools were retrieved from MCP servers. This might indicate a server connection issue or no tools defined.")

        print('STATUS: Initializing ChatGroq model.')
        model = ChatGroq(model="qwen/qwen3-32b")
        print('STATUS: ChatGroq model created successfully.')
        
        print('STATUS: Creating ReAct agent.')
        agent = create_react_agent(
            model=model,
            tools=tools
        )
        print('STATUS: ReAct agent created successfully.')

        kasa_device_alias = "Outdoor plug" # <--- **MAKE SURE THIS MATCHES YOUR ALIAS IN THE SERVER FILE**

# ==============================================================================
# SECTION 4: TEST STEPS
# ==============================================================================
        print("\n--- TEST STEP 1: Listing Smart Home Devices ---")
        print(f"DEBUG: Agent invocation: 'Can you list all the smart home devices you can control?' (Expecting '{kasa_device_alias}')")
        list_response = await agent.ainvoke(
            {"messages":[{"role":"user", "content":"Can you list all the smart home devices you can control? Do not show IP address."}]})
        print("STATUS: Agent invocation completed for listing devices.")
        print("Agent's final response for listing devices:")
        print(list_response['messages'][-1].content)
        print("-" * 60)

        print(f"\n--- TEST STEP 2: Turning on '{kasa_device_alias}' ---")
        print(f"DEBUG: Agent invocation: 'Turn on the '{kasa_device_alias}' smart plug.'")
        turn_on_response = await agent.ainvoke(
            {"messages":[{"role":"user", "content":f"Turn on the '{kasa_device_alias}' smart plug."}]})
        print(f"STATUS: Agent invocation completed for turning on '{kasa_device_alias}'.")
        print(f"Agent's final response for turning on '{kasa_device_alias}':")
        print(turn_on_response['messages'][-1].content)
        print("-" * 60)

        print(f"\n--- TEST STEP 3: Checking status of '{kasa_device_alias}' ---")
        print(f"DEBUG: Agent invocation: 'What is the status of '{kasa_device_alias}'?'")
        status_response = await agent.ainvoke(
            {"messages":[{"role":"user", "content":f"What is the status of '{kasa_device_alias}'?"}]})
        print(f"STATUS: Agent invocation completed for checking status of '{kasa_device_alias}'.")
        print(f"Agent's final response for status of '{kasa_device_alias}':")
        print(status_response['messages'][-1].content)
        print("-" * 60)

        print(f"\n--- TEST STEP 4: Turning off '{kasa_device_alias}' ---")
        print(f"DEBUG: Agent invocation: 'Turn off '{kasa_device_alias}'.'")
        turn_off_response = await agent.ainvoke(
            {"messages":[{"role":"user", "content":f"Turn off '{kasa_device_alias}'."}]})
        print(f"STATUS: Agent invocation completed for turning off '{kasa_device_alias}'.")
        print(f"Agent's final response for turning off '{kasa_device_alias}':")
        print(turn_off_response['messages'][-1].content)
        print("-" * 60)

    except Exception as e:
        print(f"CRITICAL ERROR: An unhandled error occurred in main: {e}")
        import traceback
        traceback.print_exc()
    
    print("STATUS: Client workflow finished.")

# ==============================================================================
# SECTION 5: SCRIPT EXECUTION
# ==============================================================================
if __name__ == "__main__":
    asyncio.run(main())