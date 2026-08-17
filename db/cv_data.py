import sqlite3
from db.utils import get_db
from typing import List, Dict, Any

def get_user_profile(user_id:int)->Dict[str, Any]:
    with get_db() as conn:
        row = conn.cursor().execute("""
        SELECT full_name, email, phone, linkedin_url, github_url, portfolio_url 
        FROM users WHERE id = ?
    """, (user_id,)).fetchone()
        return dict(row) if row else {}

    

def get_work_exp(user_id:int)->List[Dict[str, Any]]:
    with get_db() as conn:
            rows = conn.cursor().execute("""
            SELECT company, role, location, start_date, end_date, description_bullets 
        FROM work_experiences WHERE user_id = ? ORDER BY start_date DESC
    """, (user_id,)).fetchall()
            return [dict(row) for row in rows]



def get_projects(user_id:int)->List[Dict[str, Any]]:
     with get_db() as conn:
          rows = conn.cursor().execute("""
        SELECT title, technologies, description_bullets 
        FROM projects WHERE user_id = ?
    """, (user_id,)).fetchall()

          return [dict(row) for row in rows]



def get_education(user_id:int)->List[Dict[str, Any]]:
     with get_db() as conn:
               rows = conn.cursor().execute("""
             SELECT institution, degree, location, graduation_year 
        FROM education WHERE user_id = ? ORDER BY graduation_year DESC
        """, (user_id,)).fetchall()
     
               return [dict(row) for row in rows]


def get_certifications(user_id:int)->List[Dict[str, Any]]:
      with get_db() as conn:
                     rows = conn.cursor().execute("""
                    SELECT name, issuing_organization, issue_date, expiration_date, credential_id_or_url 
                    FROM certifications WHERE user_id = ? ORDER BY issue_date DESC
                    """, (user_id,)).fetchall()
           
                     return [dict(row) for row in rows]



def get_skills(user_id:int)->List[Dict[str, Any]]:
      with get_db() as conn:
                     rows = conn.cursor().execute("""
                    SELECT category, skills_list 
        FROM skills WHERE user_id = ?
    """, (user_id,)).fetchall()
           
                     return [dict(row) for row in rows]


def fetch_complete_user_cv_data(user_id: int) -> Dict[str, Any]:
    """Retrieves all candidate records for the user from cv_builder.db."""
    try:
        return {"profile":get_user_profile(user_id),
                "work_experience":get_work_exp(user_id),
                "projects":get_projects(user_id),
                "education":get_education(user_id),
                "certifications":get_certifications(user_id),
                "skills":get_skills(user_id)}
    except Exception as e:
           return {"error":f"Falied to get data from db\nError {str(e)}"}