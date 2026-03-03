import os 
class PersonalizedFitnessAdvisor:
    def __init__(self, api_key=None):
        from google import genai
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def generate_daily_plan_text(self, name, age, height, weight, level, goal, day):
        prompt = f"""You are a professional fitness coach.
        Create Day {day} structured plan for {name}.
        User Profile: Age {age}, Height {height}cm, Weight {weight}kg, Level: {level}, Goal: {goal}.

        Include:
        1. Workout Focus
        2. Exercise List (5-7 exercises)
        3. Estimated Calories Burn
        4. Diet Recommendation for Today
        5. One Motivational Line

        Keep between 150-220 words.
        Clear formatting using Markdown.
        Friendly but professional tone."""

        try:
            # Using the latest stable flash model for fast responses
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"AI Generation Error: {str(e)}"

    def get_live_advice(self, exercise, rep_count, goal, level):
        prompt = f"""
        You are a strict fitness coach giving short live workout feedback.
        Exercise: {exercise} | Reps: {rep_count} | Goal: {goal} | Level: {level}

        Give very short, specific body-part correction advice (max 15 words).
        Speak like a trainer standing next to them. 
        Avoid generic phrases like 'maintain proper form'.
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()
            # Enforce strict word limit for the OpenCV HUD display
            words = text.split()
            if len(words) > 15:
                text = " ".join(words[:15])

            return text
        except Exception as e:
            return "Keep pushing! Focus on your breathing."