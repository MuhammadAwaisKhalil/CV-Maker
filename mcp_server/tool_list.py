from fastmcp import FastMCP
from db.database import get_db
from schema.models import (UserFullProfile, UserResponse, WorkExperienceBase, 
    ProjectBase, EducationBase, CertificationBase, SkillBase)

mcp = FastMCP("CV Data Server")

@mcp.tool
def get_user(user_id:int)->UserFullProfile:
    """Whenever The user's description/professional knowledge is needed, call this tool to get info from database
        
        Args: user_id
        
        Response:
        Whole user data"""
    with get_db() as conn:
        u = conn.cursor().execute("SELECT * FROM users WHERE id = ?",(user_id,)).fetchone()
        user_res = UserResponse(**dict(u))

        exp = [WorkExperienceBase(**dict(r)) for r in conn.cursor().execute("SELECT * FROM work_experiences WHERE user_id = ?",(user_id,))]
        proj = [ProjectBase(**dict(r)) for r in conn.cursor.execute("SELECT * FROM projects WHERE user_id = ?",(user_id,))]
        edu = [EducationBase(**dict(r)) for r in conn.cursor().execute("SELECT * FROM education WHERE user_id = ?",(user_id,))]
        cert = [CertificationBase(**dict(r)) for r in conn.cursor.execute("SELECT * FROM certifications WHERE user_id = ?",(user_id,))]
        skills = [SkillBase(**dict(r)) for r in conn.cursor().execute("SELECT * FROM skills WHERE user_id = ?",(user_id,))]

        return UserFullProfile(user=user_res,
                               experiences=exp,
                               projects=proj,
                               education=edu,
                               certifications=cert,
                               skills=skills)
