from google import genai
from google.genai import errors
from config import GEMINI_API_KEY
from datetime import date
from textwrap import dedent

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_study_plan(tasks):
    try:

        if not tasks:
            return "No tasks available to generate a study plan."               
        
        task_text = ""

        for task in tasks:
            deadline_str = task['deadline'].strftime("%Y-%m-%d") if task['deadline'] else "No deadline"
            task_text += (
                f"Task Title: {task['title']}\n"
                f"Task Category: {task['category']}\n"
                f"Task Priority: {task['priority']}\n"
                f"Task Deadline: {deadline_str}\n"
                f"Status: {task['status']}\n"
                f"Estimated Hours: {task['estimated_hours']}\n\n"
            )

        today = date.today()
        prompt = dedent(f"""
        Current Date: {today.strftime("%Y-%m-%d")}

        You are SmartDay, an AI-powered student planner and academic productivity assistant helping a university student manage their workload.
        Your goal is not only to maximize productivity but also to maintain a healthy study-life balance.
        The study plan should begin from the current date and continue forward.

        CRITICAL INSTRUCTION: You must strictly use ONLY the tasks listed below. Do not invent external subjects, chapters, or generic academic tasks. You must break down the specific "Task Title" text into micro-topics, specific sub-steps, or concrete actionable parts across the estimated hours.

        The student's active tasks to process:
        {task_text}

        Create a practical and realistic study plan.

        Requirements:

        1. Prioritize tasks with earlier deadlines.
        2. Give higher priority tasks more attention.
        3. Avoid overloading a single day.
        4. Break large tasks into smaller study sessions and provide detailed breakdown of specific topics or milestones for each study slot based directly on the task details.
        5. Include short breaks between study sessions when appropriate.
        6. Maintain a healthy workload and avoid burnout.
        7. Encourage consistency rather than cramming.
        8. Distribute work across multiple days whenever possible.
        9. Use estimated hours intelligently to decide how much time to allocate.
        10. Help the student complete tasks before deadlines.
        11. If a deadline is very near, recommend focusing on that task first.
        12. Present the plan in a clean day-by-day format.

        Output Format:
        Do NOT use any markdown characters like '#', '##', '###', '*', '**', '_', or '__'. Use plain text only.
        
        Example of desired day-by-day structural format (Notice how the specific active task details are broken into specific sub-focus points):

        2026-06-10 Wednesday

        Session 2: [Insert Exact Task Title or Sub-component] (1.5 hours)
        Focus: [Next logical sub-step or topic block for this specific task]
        Break: 15 minutes

        Session 2: DS Viva Preparation (1.5 hours)
        Focus: Deep dive into the identified critical topics for the DS Viva. Practice explaining them clearly.
        Break: 15 minutes

        Session 3: Design Project Home Page (1.0 hour)
        Focus: Begin sketching or outlining the structure and key elements for the design project home page.

        Start the schedule from the current date.
        Use actual calendar dates instead of only weekday names.
        Keep formatting consistent.
        Return clean text suitable for direct display in the application.

        After the schedule, you MUST include the text "Study Summary" (case-insensitive) as a header exactly, followed by these details:

        Study Summary
        Total planned study hours: <value>
        Most urgent task: <value>
        Suggested daily workload: <value>

        Keep the tone friendly, encouraging, and concise.

        Important Instructions:

        - Return only the study plan.
        - Do not use markdown headers (like #, ##, ###) or bold tags (like **).
        - Do not ask follow-up questions.
        - Do not offer additional assistance.
        - Do not include conversational phrases.
        - Do not include introductions or conclusions.
        - Do not include phrases such as "Let me know...", "If you'd like...", "I can also...", "Feel free to...".
        - Do not mention that you are an AI.
        - The response should be ready to display directly inside the SmartDay application.
        - Ensure that total daily study time is realistic (2–5 hours per day unless deadlines require more).
        """
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("Gemini Error:", e)
        return "Unable to generate study plan at the moment. Please try again."



def generate_workload_analysis(tasks, stats, productivity_score):

    task_text = ""

    for task in tasks:
        deadline_str = task['deadline'].strftime("%Y-%m-%d") if task['deadline'] else "No deadline"
        task_text += (
            f"Task Title: {task['title']}\n"
            f"Task Category: {task['category']}\n"
            f"Task Priority: {task['priority']}\n"
            f"Task Deadline: {deadline_str}\n"
            f"Status: {task['status']}\n"
            f"Estimated Hours: {task['estimated_hours']}\n\n"
        )

    prompt = dedent(f"""
    You are SmartDay's AI workload analyzer. Your job is to provide a precise, data-driven synthesis of a student's performance based strictly on the metrics and specific tasks provided below. Do not use generic placeholders.


    Analyze the student's current workload and productivity.

    Dashboard Statistics:

    Total Tasks: {stats['total_tasks']}
    Pending Tasks: {stats['pending_tasks']} (active tasks that are not overdue)
    Completed Tasks: {stats['completed_tasks']}
    Expired Tasks: {stats['expired_tasks']}
    Productivity Score: {productivity_score}%

    Current Tasks:
    {task_text}

    Analysis Rules:

    1. Contextual Status: Classify the workload as Light, Moderate, or Heavy. You must explicitly calculate a percentage figure representing their workload volume or completion rate (e.g., using Pending vs Total Tasks).
    2. Strict Urgency: Identify actual tasks from the list above based on close deadlines or high priority. Do not invent filler task names.
    3. Risk Assessment: If Expired Tasks > 0, explicitly comment on the risk backlog. If 0, acknowledge their good management.
    4. Score Reflection: Directly mention the {productivity_score}% productivity score in your assessment text and offer a realistic, encouraging critique.
    5. Actionable Steps: Provide 3 concrete, specific recommendations using the Task Titles and Categories listed above (e.g., "Allocate time to complete [Task Title]" instead of "Work on your tasks").

    Output Format:
    Do NOT use any markdown characters like '#', '##', '###', '*', '**', '_', or '__'. Use plain text only. Use the exact text blocks below:

    Workload Status:
    [Your classification: light, moderate, or heavy, along with your computed percentage workload figure]

    Productivity Assessment:
    [A brief, clear paragraph directly referencing the {productivity_score}% score and the task backlog/completion ratio]

    Urgent Tasks:
    - [Insert exact Task Title 1 with its category/deadline]
    - [Insert exact Task Title 2 with its category/deadline]

    Recommendations:
    - [Specific actionable recommendation mentioning an active Task Title]
    - [Specific actionable recommendation targeting an active Task Category]
    - [A workload balancing or consistency recommendation tailored to their data]

    Important Instructions:

    - Return only the raw analysis text blocks.
    - Do not use markdown headers (like #, ##, ###) or bold tags (like **).
    - Do not ask questions.
    - Do not offer additional help.
    - Do not mention that you are an AI.
    - Do not include introductions, pleasantries or conclusions.
    - Keep the response concise, blunt yet encouraging, and ready to display directly in the SmartDay application.
    """
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception:
        return "Analysis could not be generated at the moment. Please try again later"
