 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

 
students_db = {
    "22-101-1": {"password": "123", "name": "Ifti", "courses": {"CS101": "A", "ENG101": "B+"}, "balance": 5000},
    "22-102-1": {"password": "456", "name": "ibrar", "courses": {"CS101": "B"}, "balance": 0}
    
}

teachers_db = {
    "T-501": {"password": "admin", "name": "Mr. Abdus Salam", "courses": ["CS101"]}
}

notices = ["Welcome to Summer 24-25 semester."]

# --- Pydantic Models (Data Validation) ---
class LoginRequest(BaseModel):
    user_id: str
    password: str

class NoticeRequest(BaseModel):
    notice_text: str

# --- API Endpoints ---

# 1. Login Endpoint
@app.post("/login")
def login(request: LoginRequest):
    u_id = request.user_id
    pwd = request.password

    if u_id in students_db and students_db[u_id]["password"] == pwd:
        return {"status": "success", "role": "Student", "name": students_db[u_id]["name"]}
    elif u_id in teachers_db and teachers_db[u_id]["password"] == pwd:
        return {"status": "success", "role": "Teacher", "name": teachers_db[u_id]["name"]}
    
    return {"status": "failed", "message": "Invalid ID or Password"}

# 2. get grades (Student Only)
@app.get("/student/grades/{student_id}")
def get_grades(student_id: str):
    if student_id in students_db:
        return {"status": "success", "grades": students_db[student_id]["courses"]}
    raise HTTPException(status_code=404, detail="Student not found")

# 3. post notice (teacher Only)
@app.post("/teacher/notice")
def post_notice(req: NoticeRequest):
    notices.append(req.notice_text)
    return {"status": "success", "message": "Notice Posted!"}

# 4. get notices (Public)
@app.get("/notices")
def get_notices():
    return {"notices": notices}

 