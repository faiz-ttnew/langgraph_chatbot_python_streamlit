from __future__ import annotations
from mcp.server.fastmcp import FastMCP

# create mcp server
mcp = FastMCP('CalculatorServer')

def _as_number(x):
    # Accept ints/floats or numeric strings; raise clean errors otherwise
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        return float(x.strip())
    raise TypeError("Expected a number (int/float or number string)")

# 1. addition
@mcp.tool()
def add(first_num: float, second_num: float) -> float:
     """Add two numbers."""
     return _as_number(first_num) + _as_number(second_num)

# 2. Subtraction
@mcp.tool()
def subtract(first_num: float, second_num: float) -> float:
    """Subtract second number from first number."""
    return _as_number(first_num) - _as_number(second_num)


# 3. Multiplication
@mcp.tool()
def multiply(first_num: float, second_num: float) -> float:
    """Multiply two numbers."""
    return _as_number(first_num) * _as_number(second_num)


# 4. Division
@mcp.tool()
def divide(first_num: float, second_num: float) -> dict:
    """Divide first number by second number."""

    a = _as_number(first_num)
    b = _as_number(second_num)

    if b == 0:
        return {"error": "Division by zero is not allowed"}

    return {"result": a / b}


# 5. Power
@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Calculate base raised to the power of exponent."""
    return _as_number(base) ** _as_number(exponent)


# 6. Modulus
@mcp.tool()
def modulus(first_num: float, second_num: float) -> dict:
    """Find the remainder when dividing two numbers."""

    a = _as_number(first_num)
    b = _as_number(second_num)

    if b == 0:
        return {"error": "Modulo by zero is not allowed"}

    return {"result": a % b}

# Start MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
