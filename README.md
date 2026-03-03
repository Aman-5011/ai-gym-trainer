🤖 AI Gym Trainer: Your Computer Vision Fitness Coach
Welcome to the AI Gym Trainer! 
This is a full-stack Flask application that uses Mediapipe and OpenCV to monitor your workout form in real-time. 
It doesn't just count your reps; it uses Google Gemini AI to act as a personal coach, giving you live feedback and customized daily diet/workout plans.


🌟 Key Features
1.Real-Time Pose Estimation: Uses Mediapipe to track joints and calculate angles for exercises like Squats, Pushups, and Bicep Curls.

2.AI Personal Advisor: Integrated with Gemini 2.0 Flash to generate personalized daily plans based on your BMI, fitness level, and goals.

3.Smart HUD: A live OpenCV overlay that gives you specific coaching cues (e.g., "Lower your hips") while you exercise.

4.Progress Analytics: A comprehensive dashboard that tracks your total reps, calories burned, and average form accuracy over time.

5.Automated Daily Plans: Every day you log in, the system checks if you need a new plan and generates one if the previous day is completed.



🏗️ Technical Stack
1.Frontend: HTML5, Modern CSS (Grid/Flexbox), JavaScript.

2.Backend: Flask (Python).

3.Database: SQLite3 with a centralized Manager for data integrity.

4.AI/ML: Google GenAI (Gemini SDK) & Mediapipe.

5.Computer Vision: OpenCV.



📊 How it Works (Logic Flow)
Authentication: Users sign up and set their biometrics (Age, Height, Weight).

AI Planning: The DailyPlanSystem asks Gemini to create a structured plan for the user's specific "Day X".

Workout Session: When a user starts a workout, app.py launches engine.py as a subprocess.

Feedback Loop: The engine tracks movement, calculates accuracy, and saves the session to a JSON file, which is then moved to the SQLite database.



🚀 Getting Started
1. Prerequisites
Make sure you have Python 3.10+ installed and a working webcam.

2. Environment Setup
You'll need a Google Gemini API Key. Set it in your environment

3. Installation
git clone https://github.com/yourusername/ai-gym-trainer.git
cd ai-gym-trainer
pip install -r requirements.txt

4. Running the App:python app.py



📁 Project Structure
app.py: The central hub and Flask routes.

engine.py: The "Brain"—OpenCV and Mediapipe logic for exercise tracking.

gemini_service.py: Specialist for all AI-generated coaching and content.

database.py: Handles all SQL schema and connections.

workout_system.py: Manages history and aggregated progress stats.

daily_plan_system.py: Manages the logic for day-to-day fitness calendars.
