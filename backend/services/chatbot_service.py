def get_chatbot_response(message):

    message = message.lower()

    if "hello" in message or "hi" in message:
        return "Hello! I am HireLens AI. How can I help you today?"

    elif "strength" in message:
        return "Focus on highlighting your technical skills, communication, teamwork, and problem-solving abilities."

    elif "weakness" in message:
        return "Choose a genuine weakness and explain how you are actively improving it."

    elif "tell me about yourself" in message:
        return (
            "Start with your education, mention your skills, projects, "
            "and finish with why you are excited for this opportunity."
        )

    elif "interview" in message:
        return "Stay confident, maintain eye contact, and answer calmly."

    else:
        return "Sorry, I couldn't understand that. Please ask another interview-related question."