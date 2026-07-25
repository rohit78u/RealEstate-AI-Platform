import os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content("Say only: Hello")

print(response.text)