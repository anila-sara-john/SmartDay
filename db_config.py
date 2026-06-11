import os
import mysql.connector
from mysql.connector import Error
from datetime import date
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")


def get_connection():
    """Return a MySQL connection to smartday_db, or None on failure."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def email_exists(email):
    """Return True if email exists, False if not, None on connection failure."""
    connection = get_connection()
    if not connection:
        return None

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1 FROM users WHERE email = %s LIMIT 1", (email,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        connection.close()


def get_user_by_email(email):
    """Return the user record as a dictionary if found, otherwise None."""
    connection = get_connection()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def create_user(name, email, hashed_password):
    """Insert a new user into the users table. Return True on success, False on failure."""
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password),
        )
        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        print(f"User creation error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def create_task(user_id, title, category, priority, deadline, estimated_hours):
    """Insert a new task into the tasks table. Return True on success, False on failure."""
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute(
            """INSERT INTO tasks (user_id, title, category, priority, deadline, estimated_hours, status)
               VALUES (%s, %s, %s, %s, %s, %s, 'pending')""",
            (user_id, title, category, priority, deadline, estimated_hours),
        )
        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        print(f"Task creation error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_task_by_id(task_id):
    """Return the task record as a dictionary if found, otherwise None."""
    connection = get_connection()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tasks WHERE id = %s LIMIT 1", (task_id,))

        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def update_task(task_id, user_id, title, category, priority, deadline, estimated_hours, status):
    """Update a task in the tasks table. Return True on success, False on failure."""
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute(
            """UPDATE tasks
               SET title = %s, category = %s, priority = %s, deadline = %s, estimated_hours = %s, status = %s
               WHERE id = %s AND user_id = %s""",
            (title, category, priority, deadline, estimated_hours, status, task_id, user_id),
        )
        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        print(f"Task update error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def delete_task(task_id):
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s",
            (task_id,)
        )

        connection.commit()
        return True

    except Exception:
        return False

    finally:
        cursor.close()
        connection.close()


def mark_task_completed(task_id):
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE tasks SET status = 'completed' WHERE id = %s",
            (task_id,)
        )
        connection.commit()
        return True

    except Exception:
        return False

    finally:
        cursor.close()
        connection.close()


def get_tasks_by_user(user_id):
    """Return all tasks for a user as a list of dictionaries, ordered by nearest deadline first."""
    connection = get_connection()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT * FROM tasks
               WHERE user_id = %s
               ORDER BY deadline ASC""",
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_dashboard_stats(user_id):
    connection = get_connection()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        today = date.today()

        # Total tasks
        cursor.execute(
            "SELECT COUNT(*) AS count FROM tasks WHERE user_id = %s",
            (user_id,)
        )
        total_tasks = cursor.fetchone()['count']

        # Pending tasks (non-completed tasks that have not expired, including those with no deadline)
        cursor.execute(
            """SELECT COUNT(*) AS count FROM tasks 
               WHERE user_id = %s 
               AND status != 'completed' 
               AND (deadline IS NULL OR deadline >= %s)""",
            (user_id, today)
        )
        pending_tasks = cursor.fetchone()['count']

        # Completed tasks
        cursor.execute(
            "SELECT COUNT(*) AS count FROM tasks WHERE user_id = %s AND status = 'completed'",
            (user_id,)
        )
        completed_tasks = cursor.fetchone()['count']

        # Expired tasks
        cursor.execute(
            """SELECT COUNT(*) AS count FROM tasks 
            WHERE user_id = %s 
            AND deadline IS NOT NULL
            AND deadline < %s
            AND status != 'completed' """,
            (user_id, today,)
        )
        expired_tasks = cursor.fetchone()['count']

        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'expired_tasks': expired_tasks
        }
    finally:
        cursor.close()
        connection.close()




                                    #   AI STUDY PLAN GENERATION

def get_active_tasks_for_plan(user_id):
    connection = get_connection()
    if not connection:
        return []
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT * FROM tasks where user_id = %s AND status != 'completed'
            ORDER BY deadline ASC
            """,
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def save_study_plan(user_id, plan_text):
    connection = get_connection()
    if not connection:
        return False
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM study_plans
            WHERE user_id = %s
            """,
            (user_id,)
        )
        cursor.execute(
            """
            INSERT INTO study_plans (user_id, plan_text)
            VALUES (%s, %s)
            """,
            (user_id, plan_text)
        )
        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()


def get_latest_study_plan(user_id):
    connection = get_connection()
    if not connection:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT *
            FROM study_plans
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def save_workload_report(user_id, report_text):
    connection = get_connection()
    if not connection:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO workload_reports (user_id, report_text)
            VALUES (%s, %s)
            """,
            (user_id, report_text)
        )

        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()


def get_latest_workload_report(user_id):
    connection = get_connection()
    if not connection:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM workload_reports
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )

        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


        
   