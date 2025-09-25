import asyncio
from app.crew import initialize_crew


async def main():
    user_data = {
            "Job_title": "Machine learning Engineer",
            "email_address": "ziadwaleedmohamed2003@gmail.com",
            "preferred_skills": ["python"],
            "experience_level": "Fresh",
            "min_years_experience": 1,
            "locations": ["Egypt"],
            "remote_preference": ["remote"],
            "job_type": ["Full-Time"]
    }
    
    res = await initialize_crew(user_input_data=user_data)
    print(f"Result: {res}")


if __name__ == "__main__":
    asyncio.run(main())
