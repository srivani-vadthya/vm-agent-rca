import socket
import requests
import os
import psutil  # Good for checking generic processes
import inspect
from typing import Callable, Dict, Any

# ==========================================
# 1. GENERAL PURPOSE DIAGNOSTICS TOOLS
# ==========================================

def check_network_port(host: str, port: int) -> bool:
    """
    Checks network connectivity to any host and port. 
    Use this when logs indicate connection timeouts, refused connections, or database unreachable errors.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False

def check_http_endpoint(url: str) -> bool:
    """
    Sends a GET request to a specific URL or web API.
    Use this when logs report HTTP errors (500, 404, bad gateways) or microservice communication failures.
    """
    try:
        res = requests.get(url, timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def inspect_file_or_log(filepath: str) -> str:
    """
    Checks if a configuration, data, or log file exists and returns its size or basic status.
    Use this when logs report 'File Not Found', permissions errors, or missing environment files.
    """
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return f"File exists. Size: {size} bytes."
    return "File does not exist."

def check_system_process(process_name: str) -> bool:
    """
    Checks if a specific background service or process is currently running on the operating system.
    Use this when logs indicate that a dependent daemon, server, or application process has crashed or is missing.
    """
    process_name = process_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if process_name in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


# ==========================================
# 2. DYNAMIC TOOL REGISTRY
# ==========================================

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, func: Callable):
        """Registers a function as an available tool."""
        self.tools[func.__name__] = func
        return func

    def get_agent_schema(self) -> list:
        """Converts registered Python functions into standard LangChain/OpenAI function schemas."""
        schemas = []
        for name, func in self.tools.items():
            sig = inspect.signature(func)
            doc = inspect.getdoc(func) or "No description provided."
            
            properties = {}
            required = []
            for param_name, param in sig.parameters.items():
                param_type = "string"
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                
                properties[param_name] = {"type": param_type}
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": doc,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            })
        return schemas

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Executes the tool by name using parameters dynamically extracted by the LLM."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered.")
        return self.tools[tool_name](**kwargs)


# Initialize and register the generic tool suite
registry = ToolRegistry()
registry.register(check_network_port)
registry.register(check_http_endpoint)
registry.register(inspect_file_or_log)
registry.register(check_system_process)