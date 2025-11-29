import parsers
from fastapi import FastAPI, HTTPException
from typing import Union
from pydantic import BaseModel
from classes import Student, Faculty, User
import parsers


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "University System API is running"}


def get_next_id(users):
    if not users:
        return 1

    ids = [u.id for u in users if u.id is not None]
    if not ids:
        return 1
    return max(ids) + 1


@app.post("/register/student", response_model=Student)
def register_student(student: Student):
    users = parsers.load_users()
    student.id = get_next_id(users)
    student.type = "student"
    users.append(student)
    parsers.save_users(users)
    return student


@app.post("/register/faculty", response_model=Faculty)
def register_faculty(faculty: Faculty):
    users = parsers.load_users()
    faculty.id = get_next_id(users)
    faculty.type = "faculty"
    users.append(faculty)
    parsers.save_users(users)
    return faculty


@app.post("/login")
def login(data: dict):
    users = parsers.load_users()
    user_id = data.get("id")
    password = data.get("password")

    for u in users:
        if u.id == user_id:
            if u.password == password:
                return {
                    "status": "success",
                    "message": f"Welcome {u.name}",
                    "user": u.model_dump(),
                }
            else:
                raise HTTPException(status_code=401, detail="Wrong Password")

    raise HTTPException(status_code=404, detail="User not found")


@app.put("/update/user/{user_id}")
def update_user(user_id: int, updated_data: dict):
    users = parsers.load_users()
    found = False
    updated_user = None

    for i, u in enumerate(users):
        if u.id == user_id:

            current_data = u.model_dump()

            current_data.update(updated_data)

            if u.type == "student":
                users[i] = Student(**current_data)
            else:
                users[i] = Faculty(**current_data)

            updated_user = users[i]
            found = True
            break

    if not found:
        raise HTTPException(404, "User not found")

    parsers.save_users(users)
    return {"status": "updated", "data": updated_user}


# --- ekhne crs management ---

@app.get("/courses")
def get_all_courses():
    # c.txt theke course gula read korbe
    courses = parsers.populate()
    return {"courses": courses}

@app.post("/student/enroll")
def enroll_course(data: dict):
    # data theke student ID ar Course Code nibo
    student_id = data.get("student_id")
    course_code = data.get("course_code")
    
    users = parsers.load_users()
    found_student = None
    
    # User khuje ber kora
    for i, u in enumerate(users):
        if u.id == student_id and u.type == "student":
            found_student = users[i]
            break
            
    if not found_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Course ta already niyeche kina check kora
    if course_code in found_student.current_courses:
        raise HTTPException(status_code=400, detail="Course already enrolled")
        
    # Course ta add kora
    found_student.current_courses.append(course_code)
    
    # Save kora
    parsers.save_users(users)
    
    return {"status": "success", "message": f"Enrolled in {course_code}", "data": found_student}


# --- main.py UPDATE ---



# 1. Marks to GPA Conversion Helper
def calculate_gpa_point(marks: int):
    if marks >= 90: return 4.00   # A+
    elif marks >= 85: return 3.75 # A
    elif marks >= 80: return 3.50 # B+
    elif marks >= 75: return 3.25 # B
    elif marks >= 70: return 3.00 # C+
    elif marks >= 65: return 2.75 # C
    elif marks >= 60: return 2.50 # D+
    elif marks >= 50: return 2.25 # D
    else: return 0.00             # F

# 2. input model
class MarksUpload(BaseModel):
    student_id: int
    course_code: str
    marks: int

# 3. api endpoint
@app.post("/faculty/upload_marks")
def upload_marks(data: MarksUpload):
    users = parsers.load_users()
    found_student = None
    idx = -1
    
    # User khoja
    for i, u in enumerate(users):
        if u.id == data.student_id and u.type == "student":
            found_student = u
            idx = i
            break
            
    if not found_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Student ei course e enroll kora ache kina check
    if data.course_code not in found_student.current_courses:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    # Logic: Marks -> Grade Point
    gpa_point = calculate_gpa_point(data.marks)
    
    # Result Dictionary te save kora
    # Example: results = {"CS101": 4.00}
    found_student.results[data.course_code] = gpa_point
    
    # cgpa Recalculation (Average of all courses)
    total_points = sum(found_student.results.values())
    total_subjects = len(found_student.results)
    
    if total_subjects > 0:
        found_student.gpa = round(total_points / total_subjects, 2)
    
    # Save hobe db te
    users[idx] = found_student
    parsers.save_users(users)
    
    return {
        "status": "success", 
        "message": f"Marks: {data.marks} converted to GPA: {gpa_point}",
        "current_cgpa": found_student.gpa
    }