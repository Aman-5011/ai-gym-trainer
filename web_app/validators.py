import re

def validate_full_name(name):
    """Validates that the name contains only alphabets and spaces, length 2-50."""
    if not isinstance(name, str) or not (2 <= len(name) <= 50):
        raise ValueError("Full name must be a string between 2 and 50 characters.")
    if not re.match(r"^[a-zA-Z\s]+$", name):
        raise ValueError("Full name can only contain alphabets and spaces.")
    return True

def validate_age(age):
    """Validates that age is an integer between 10 and 80."""
    if not isinstance(age, int):
        raise ValueError("Age must be an integer.")
    if not (10 <= age <= 80):
        raise ValueError("Age must be between 10 and 80.")
    return True

def validate_height(height):
    """Validates that height is a float between 100 and 250 cm."""
    try:
        h = float(height)
    except (ValueError, TypeError):
        raise ValueError("Height must be a numeric value.")
    if not (100 <= h <= 250):
        raise ValueError("Height must be between 100 and 250 cm.")
    return True

def validate_weight(weight):
    """Validates that weight is a float between 30 and 250 kg."""
    try:
        w = float(weight)
    except (ValueError, TypeError):
        raise ValueError("Weight must be a numeric value.")
    if not (30 <= w <= 250):
        raise ValueError("Weight must be between 30 and 250 kg.")
    return True

def validate_goal(goal):
    """Validates that the goal is one of the four allowed primary objectives."""
    valid_goals = ["fat_loss", "muscle_gain", "endurance", "general_fitness"]
    if goal not in valid_goals:
        raise ValueError("Goal must be one of: fat_loss, muscle_gain, endurance, general_fitness.")
    return True

def validate_fitness_level(level):
    """Validates that the fitness level is within the three allowed categories."""
    valid_levels = ["beginner", "intermediate", "advanced"]
    if level not in valid_levels:
        raise ValueError("Fitness level must be one of: beginner, intermediate, advanced.")
    return True


def validate_username(username):
        """Validates username: 4-20 chars, alphanumeric and underscores only."""
        if not (4 <= len(username) <= 20):
            raise ValueError("Username must be between 4 and 20 characters.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValueError("Username can only contain letters, numbers, and underscores.")
        return True

def validate_password(password):
    """Validates password: Min 8 chars, 1 digit, 1 special character."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character.")
    return True

def validate_profile_data(age, height, weight):
    """Validates numeric ranges for profile data."""
    if not (5 <= age <= 100):
        raise ValueError("Age must be between 5 and 100.")
    if not (100 <= height <= 250):
        raise ValueError("Height must be between 100 and 250 cm.")
    if not (20 <= weight <= 250):
        raise ValueError("Weight must be between 20 and 250 kg.")
    return True