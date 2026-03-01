class PersonalizedFitnessAdvisor:

    def __init__(self, api_key):
        from google import genai
        self.client = genai.Client(api_key=api_key)

    # ===============================
    # 1️⃣ Initial Detailed Guidance
    # ===============================
    def get_initial_guidance(self, name, age, height, weight, fitness_level, goal):

        prompt = f"""
You are a professional certified fitness coach.

Create a personalized fitness roadmap for:

Name: {name}
Age: {age}
Height: {height} cm
Weight: {weight} kg
Fitness Level: {fitness_level}
Goal: {goal}

Structure response clearly into:

1. Overall Training Strategy
2. Weekly Workout Structure
3. Nutrition Focus
4. Recovery Advice
5. Motivation

Keep it between 120–180 words.
Friendly but professional tone.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:
            return f"Error occurred: {str(e)}"


    # ===============================
    # 2️⃣ Live Short Advice
    # ===============================
    def get_live_advice(self, name, age, height, weight,
                        fitness_level, goal, exercise, rep_count):

        prompt = f"""
You are a strict fitness coach giving short live workout feedback.

Exercise: {exercise}
Reps completed: {rep_count}
Goal: {goal}
Fitness Level: {fitness_level}

Give very short advice (maximum 20 words).
Important:
- Speak like a human trainer standing next to them.
- Do NOT repeat previous advice.
- Give a very specific body-part correction.
- Avoid generic advice like "maintain proper form".
- Use natural short coaching tone.
Be concise.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()

            # Hard enforce 20-word limit
            words = text.split()
            if len(words) > 20:
                text = " ".join(words[:20])

            return text

        except Exception as e:
            return f"Error occurred: {str(e)}"