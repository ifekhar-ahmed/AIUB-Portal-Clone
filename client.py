import requests
import time
from classes import BloodGroup, Religion, Level, Department
from helper import print_enum_choice, printChoice, prettyPrint, coloredPrint

URL = "http://127.0.0.1:8000"

def enroll_course_ui(user_data):
    print("\n--- Available Courses ---")
    try:
        # server theke course list ansi
        res = requests.get(f"{URL}/courses")
        if res.status_code == 200:
            courses = res.json().get("courses", [])
            # Course gula sundor kore show korsi
            for i, c in enumerate(courses):
                print(f"{i+1}. {c.get('Code')} - {c.get('Name')} (Cr: {c.get('Credits')})")
            
            # Input nisi ekhan theeke 
            choice_idx = input("\nEnter row number to enroll (or press Enter to cancel): ")
            if choice_idx.isdigit() and 0 < int(choice_idx) <= len(courses):
                selected_course = courses[int(choice_idx)-1]
                code = selected_course.get("Code")
                
                # Enrollment Request pathaisi
                payload = {"student_id": user_data['id'], "course_code": code}
                enroll_res = requests.post(f"{URL}/student/enroll", json=payload)
                
                if enroll_res.status_code == 200:
                    coloredPrint(f"Successfully Enrolled in {code}!", "green")
                else:
                    err = enroll_res.json().get('detail')
                    coloredPrint(f"Failed: {err}", "red")
        else:
            print("Could not fetch course list.")
    except Exception as e:
        print("Error:", e)


 # upload marks ekhane korsi
def upload_marks_ui():
    print("\n--- Upload Student Marks ---")
    s_id = input("Enter Student ID: ")
    course = input("Enter Course Code (e.g. CSC1102): ")
    
    try:
        marks_input = input("Enter Marks (0-100): ")
        if not marks_input.isdigit():
            print("Marks must be a number.")
            return
            
        marks = int(marks_input)
        if marks < 0 or marks > 100:
            print("Marks must be between 0 and 100")
            return

        payload = {
            "student_id": int(s_id),
            "course_code": course,
            "marks": marks
        }
        
        # Server Call korsi ekhan theke 
        res = requests.post(f"{URL}/faculty/upload_marks", json=payload)
        
        if res.status_code == 200:
            data = res.json()
            coloredPrint(f"Success! {data['message']}", "green")
            coloredPrint(f"Student's New CGPA: {data['current_cgpa']}", "yellow")
        else:
            err = res.json().get('detail')
            coloredPrint(f"Failed: {err}", "red")
            
    except Exception as e:
        print("Error:", e)



def collect_base_class_info():
    print("\n--- Personal Details ---")
    name = input("Name: ")
    pwd = input("Password: ")
    addr = input("Address: ")
    email = input("Email: ")
    bg = print_enum_choice(BloodGroup, "Blood Group")
    rel = print_enum_choice(Religion, "Religion")
    return {
        "name": name,
        "password": pwd,
        "address": addr,
        "email": email,
        "blood_group": bg,
        "religion": rel,
    }


def register():
    print("\n--- Register ---")
    print("1. Student")
    print("2. Faculty")
    type_choice = input("Select type: ")

    data = collect_base_class_info()
    endpoint = ""

    if type_choice == "1":
        endpoint = "/register/student"
        data["semester"] = int(input("Semester (1-8): ") or 1)
        data["dept"] = print_enum_choice(Department, "Department")
    elif type_choice == "2":
        endpoint = "/register/faculty"
        data["salary"] = int(input("Salary: ") or 0)
        data["level"] = print_enum_choice(Level, "Level")
        data["dept"] = print_enum_choice(Department, "Department")
    else:
        print("Invalid user type selection.")
        return

    try:
        response = requests.post(f"{URL}{endpoint}", json=data)
        if response.status_code == 200:
            user = response.json()
            coloredPrint(f"\nSuccess! Your User ID is: {user['id']}", "green")
            print("Please remember this ID to login.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        coloredPrint("Cannot connect to server. Is main.py running?", "red")


def edit_user(user_data):
    prettyPrint("Edit Mode")
    print(f"Editing: {user_data['name']} ({user_data['type']})")

    new_data = {}

    name = input(f"Name [{user_data['name']}]: ")
    if name:
        new_data["name"] = name

    addr = input(f"Address [{user_data['address']}]: ")
    if addr:
        new_data["address"] = addr

    email = input(f"Email [{user_data.get('email', '')}]: ")
    if email:
        new_data["email"] = email

    if user_data["type"] == "faculty":
        sal = input(f"Salary [{user_data.get('salary', 0)}]: ")
        if sal:
            new_data["salary"] = int(sal)

    if user_data["type"] == "student":
        gpa = input(f"GPA [{user_data.get('gpa', 0.0)}]: ")
        if gpa:
            new_data["gpa"] = float(gpa)

    if not new_data:
        print("No changes made.")
        return

    try:
        res = requests.put(f"{URL}/update/user/{user_data['id']}", json=new_data)
        if res.status_code == 200:
            coloredPrint("Update Successful!", "green")
            
            return res.json().get("data")
        else:
            print("Update failed:", res.text)
    except Exception as e:
        print("Error:", e)
    return user_data


def login():
    print("\n--- Login ---")
    try:
        uid_input = input("User ID: ")
        if not uid_input.isdigit():
            print("ID must be a number.")
            return
        uid = int(uid_input)
        pwd = input("Password: ")
    except ValueError:
        print("Invalid input.")
        return

    try:
        res = requests.post(f"{URL}/login", json={"id": uid, "password": pwd})
        if res.status_code == 200:
            data = res.json()
            user = data["user"]
            coloredPrint(data["message"], "green")

             # --- AGER CODE ---
             

            while True:
                print(f"\n--- User Menu ({user['type'].upper()}) ---")
                
                # [CHANGE 1] Menu te 'Upload Marks' add korar jonno (Faculty der jonno)
                if user['type'] == 'student':
                    act = printChoice(["View Info", "Edit Info", "Enroll Course", "Logout"])
                else:
                    act = printChoice(["View Info", "Edit Info", "Upload Marks", "Logout"])

                if act == "1":
                    # ... (View Info code same thakbe) ...
                    pass 

                elif act == "2":
                    # ... (Edit Info code same thakbe) ...
                    pass
                
                # [ CHANGE 2] 3 number option handle kora
                elif act == "3":
                    if user['type'] == 'student':
                        enroll_course_ui(user)
                    elif user['type'] == 'faculty':
                        upload_marks_ui()  # <--- Ei line ta notun

                # [CHANGE 3] Logout handle kora
                elif act == "4":
                    break
        else:
            coloredPrint("Login Failed: Wrong ID or Password", "red")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the server is running.")


if __name__ == "__main__":
    prettyPrint("Uni System")
    while True:
        print("\n--- Main Menu ---")
        op = printChoice(["Login", "Register", "Quit"])

        if op == "1":
            login()
        elif op == "2":
            register()
        elif op == "3":
            print("Goodbye!")
            break