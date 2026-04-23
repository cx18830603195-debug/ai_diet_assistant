from mcp.server import FastMCP

mcp = FastMCP("饮食助手MCP工具")

@mcp.tool()
def record_diet(meal_type: str, food: str) -> str:
    """MCP标准工具：记录饮食"""
    return f"✅ [MCP] 已记录 {meal_type}：{food}"

@mcp.tool()
def get_ai_answer(prompt: str) -> str:
    """MCP标准工具：让AI自由回答"""
    return ""

if __name__ == "__main__":
    mcp.run()