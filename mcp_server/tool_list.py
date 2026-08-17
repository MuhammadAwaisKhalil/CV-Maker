from fastmcp import FastMCP
from db.cv_data import fetch_complete_user_cv_data
from typing import Dict,List,Any
import docx
import sys
import io
import os


mcp = FastMCP(name="CV Agent Tools")

@mcp.tool
def get_complete_user_data(user_id:int)->Dict[str,Any]:
    """MAP TOOL:
    Fetches complete user data from database
    Args:
    user_id:int
    Curremt id of user logged into the system
    
    Response:
    Dictionary containing all user data"""


    return fetch_complete_user_cv_data(user_id)

@mcp.tool
def execute_dynamic_cv_code(generated_python_code:str, output_filepath:str)->Dict[str, Any]:
    """Executes dynamically generated python-docx code inside a sandbox environment 
    to create and save a Microsoft Word (.docx) CV."""
    sandbox_globals = {
        "docx": docx,
        "Document": docx.Document,
        "Inches": docx.shared.Inches,
        "Pt": docx.shared.Pt,
        "RGBColor": docx.shared.RGBColor,
        "WD_ALIGN_PARAGRAPH": docx.enum.text.WD_ALIGN_PARAGRAPH,
        "WD_TABLE_ALIGNMENT": docx.enum.table.WD_TABLE_ALIGNMENT,
        "OUTPUT_PATH": output_filepath,
        "__builtins__": {
            "range": range,
            "len": len,
            "enumerate": enumerate,
            "dict": dict,
            "list": list,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "print": print
        }
    }

    stdout_capture = io.StringIO()
    sys.stdout = stdout_capture

    try:
        exec(generated_python_code, sandbox_globals)
        sys.stdout = sys.__stdout__

        if os.path.exists(output_filepath):
            return {
                "success": True, 
                "filepath": output_filepath, 
                "logs": stdout_capture.getvalue()
            }
        else:
            return {
                "success": False, 
                "error": f"File was not created at expected path: {output_filepath}",
                "logs": stdout_capture.getvalue()
            }

    except Exception as err:
        sys.stdout = sys.__stdout__
        # Return exact exception trace so Gemini can see why the script failed
        return {
            "success": False, 
            "error": f"{type(err).__name__}: {str(err)}", 
            "logs": stdout_capture.getvalue()
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")

