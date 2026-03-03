import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session
from auth_system import AuthSystem
from profile_system import ProfileSystem
from daily_plan_system import DailyPlanSystem
from workout_system import WorkoutSystem

app = Flask(__name__)
app.secret_key = "super_secret_gym_key_123"
daily_plan_system = DailyPlanSystem()
auth = AuthSystem()
profile_system = ProfileSystem()
work_sys=WorkoutSystem()

@app.route("/")
def home():
    return render_template("welcome.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username") #ye username laake dega form se 
        password = request.form.get("password")
        
        result = auth.create_user(username, password) #ye authenticate karega ki vo valid he ya nahi or valid hoga to new user register ho jayega
        
        if result["success"]:
            return redirect(url_for("login")) #agar signup successful he to login par bhejdegaa
        else:
            error = result["error"] #otherwise kuch nahi hoga
            
    return render_template("signup.html", error=error) 

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = auth.login_user(username, password) 
        
        if user:
            session["user"] = user #user login karliya he
            
            if not profile_system.profile_exists(user):  #kya uske paas profile nahi he pehle se to profile setup par bhejo
                return redirect(url_for("setup_profile"))
            else:
                return redirect(url_for("dashboard")) #otherwise dashboard par bhejdo
        else:
            error = "Invalid username or password."
            
    return render_template("login.html", error=error)

@app.route("/setup-profile", methods=["GET", "POST"])
def setup_profile():
    if "user" not in session:
        return redirect(url_for("login"))

    error = None

    if request.method == "POST":
        full_name = request.form.get("full_name")
        
        # Data conversion for ProfileSystem validators
        try:
            age = int(request.form.get("age") or 0)
            height = float(request.form.get("height") or 0)
            weight = float(request.form.get("weight") or 0)
        except ValueError:
            error = "Age, height, and weight must be numeric values."
            return render_template("setup_profile.html", error=error)

        goal = request.form.get("goal")
        fitness_level = request.form.get("fitness_level")

        # data to leliya he variables me but ab file bnane ke liye profile_system help karega
        result = profile_system.create_profile(
            session["user"],
            full_name,
            age,
            height,
            weight,
            goal,
            fitness_level
        )

        if result["success"]:
            return redirect(url_for("dashboard"))
        else:
            error = result["error"]

    return render_template("setup_profile.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]

    # Check for pending workout results from engine.py
    session_file = "last_session.json"
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
            
            exercise = data.get("exercise", "unknown")
            reps = data.get("reps", 0)
            accuracy = data.get("accuracy", 0.0)
            calories = data.get("calories", 0.0)

            # Save to Database using auth_system instance
            work_sys.save_workout(
                username=username,
                exercise=exercise,
                reps=reps,
                accuracy=accuracy,
                calories_burned=calories,
                target_completed=1 if reps >= 10 else 0
            )
            
            os.remove(session_file)
        except Exception as e:
            print(f"Error processing session file: {e}")

    # Fetch Profile, Plan, and Latest Workout data
    profile = profile_system.get_profile(username)
    if profile is None:
        return redirect(url_for("setup_profile"))
    
    latest_day = daily_plan_system.get_latest_day(username)
    plan = daily_plan_system.get_plan_for_day(username, latest_day) if latest_day > 0 else None
    
    # Requirement: Fetch latest workout for current user
    latest_workout = work_sys.get_latest_workout(username)
    
    return render_template(
        "dashboard.html", 
        username=username, 
        profile=profile, 
        plan=plan,
        latest_workout=latest_workout,
        active_page="dashboard"
    )

@app.route("/logout")
def logout():
    """Clears user session and redirects to login."""
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/diet-plan", methods=["GET", "POST"])
def diet_plan():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    profile = profile_system.get_profile(username)

    if profile is None:
        return redirect(url_for("setup_profile"))

    latest_day = daily_plan_system.get_latest_day(username)

    if latest_day == 0:
        # Generate Day 1 AI workout and diet plan
        plan_text = daily_plan_system.generate_daily_plan(
            profile["full_name"],
            profile["age"],
            profile["height"],
            profile["weight"],
            profile["fitness_level"],
            profile["goal"],
            1
        )
        daily_plan_system.create_new_day_plan(username, plan_text)
        latest_day = 1

    plan = daily_plan_system.get_plan_for_day(username, latest_day)

    if request.method == "POST":
        # Mark the current day's plan as completed
        daily_plan_system.mark_completed(username, latest_day)
        return redirect(url_for("diet_plan"))

    return render_template(
        "ai_guidance.html",  # Updated template name
        day_number=latest_day,
        plan=plan["plan_text"],
        completed=plan["completed"],
        active_page="ai_guidance"  # Updated for sidebar highlighting
    )

@app.route("/workout")
def workout():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    profile = profile_system.get_profile(username)
    
    if profile is None:
        return redirect(url_for("setup_profile"))
    
    return render_template(
        "workout.html", 
        profile=profile, 
        active_page="workout"
    )

@app.route("/start-workout", methods=["POST"])
def start_workout():
    if "user" not in session:
        return redirect(url_for("login"))
    
    exercise = request.form.get("exercise")
    username = session["user"]
    profile = profile_system.get_profile(username)
    fitness_level = profile.get("fitness_level", "beginner")

    # Launch engine.py as a separate process
    subprocess.Popen([
        "python",
        "engine.py",
        exercise,
        fitness_level
    ])
    return redirect(url_for("dashboard"))

@app.route("/progress")
def progress():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    summary = work_sys.get_user_progress(username)
    workouts = work_sys.get_all_workouts(username)

    return render_template(
        "progress.html",
        summary=summary,
        workouts=workouts,
        active_page="progress"
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if request.method == "POST":
        full_name = request.form.get("full_name")
        age = request.form.get("age")
        height = request.form.get("height")
        weight = request.form.get("weight")
        fitness_level = request.form.get("fitness_level")
        goal = request.form.get("goal")

        # Requirement: Use existing profile_system
        profile_system.update_profile(
            username,
            full_name,
            age,
            height,
            weight,
            fitness_level,
            goal
        )

        return redirect(url_for("profile"))

    profile_data = profile_system.get_profile(username)

    return render_template(
        "profile.html",
        profile=profile_data,
        active_page="profile"
    )

@app.route("/heartbeat")
def heartbeat():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "heartbeat.html",
        active_page="heartbeat"
    )

if __name__ == "__main__":
    app.run(debug=True)