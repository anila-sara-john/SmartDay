from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from db_config import create_task, create_user, delete_task, email_exists, get_active_tasks_for_plan, get_dashboard_stats, get_latest_study_plan, get_latest_workload_report, get_task_by_id, get_tasks_by_user, get_user_by_email, mark_task_completed, save_study_plan, save_workload_report, update_task
from gemini_helper import generate_study_plan, generate_workload_analysis
from config import SECRET_KEY

app = Flask(__name__)

# Secret key is required to securely sign session cookies
app.secret_key = SECRET_KEY


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    name = ''
    email = ''

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        exists = email_exists(email)

        if exists is None:
            error = 'Unable to connect to the database. Please try again later.'
        elif exists:
            error = 'An account with this email already exists.'
        else:
            hashed_password = generate_password_hash(password)
            if create_user(name, email, hashed_password):
                success = 'Registration successful! You can now log in.'
                name = ''
                email = ''
            else:
                error = 'Registration failed. Please try again.'

    return render_template('register.html', error=error, success=success, name=name, email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    email = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            # Store logged-in user info in the session
            session['user_id'] = user['id']
            session['user_name'] = user['name']

            # Redirect to dashboard after successful login
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid email or password.'

    return render_template('login.html', error=error, email=email)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Redirect to login if the user is not logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tasks = get_tasks_by_user(session['user_id'])
    stats = get_dashboard_stats(session['user_id'])

    total = stats['total_tasks']
    completion_rate = 0
    deadline_rate = 0
    productivity_score = 0

    if total > 0:
        completion_rate = round((stats['completed_tasks'] / total) * 100)
        deadline_rate = round(((total - stats['expired_tasks']) / total) * 100)

        # simple productivity formula
        productivity_score = round((completion_rate * 0.8) + (deadline_rate * 0.2))

        if productivity_score < 0:
            productivity_score = 0

    # Retrieve latest AI study plan and workload analysis for dashboard overview
    plan = get_latest_study_plan(session['user_id'])
    report = get_latest_workload_report(session['user_id'])
    parsed_report = None
    if report:
        parsed_report = parse_workload_report(report['report_text'])

    return render_template(
        'dashboard.html',
        user_name=session['user_name'],
        tasks=tasks,
        stats=stats,
        completion_rate=completion_rate,
        deadline_rate=deadline_rate,        
        productivity_score=productivity_score,
        plan=plan,
        report=report,
        parsed_report=parsed_report,
        now=datetime.now().date()
    )

@app.route('/tasks')
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tasks = get_tasks_by_user(session['user_id'])
    return render_template(
        'tasks.html',
        tasks=tasks,
        now=datetime.now().date()
    )

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    success = None

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        priority = request.form['priority']
        deadline = request.form['deadline'] or None
        estimated_hours = request.form['estimated_hours'] or None

        if create_task(session['user_id'], title, category, priority, deadline, estimated_hours):
            success = 'Task added successfully!'

    return render_template('add_task.html', success=success)


@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    error = None
    success = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = get_task_by_id(task_id)

    # Task doesn't exist
    if not task:
        error = 'Task not found.'
        return render_template('edit_task.html', task=None, error=error, success=None)

    # Security check: only owner can edit
    if task['user_id'] != session['user_id']:
        error = 'You are not authorized to edit this task.'

    if request.method == 'POST':

        title = request.form['title']
        category = request.form['category']
        priority = request.form['priority']
        deadline = request.form['deadline'] or None
        estimated_hours = request.form['estimated_hours'] or None
        status = request.form['status']

        if update_task(task_id, session['user_id'], title, category, priority, deadline, estimated_hours, status):
            success = 'Task updated successfully!'
        else:
            error = 'Failed to update task. Please try again.'

    return render_template('edit_task.html', task=task, error=error, success=success)


@app.route('/delete-task-route/<int:task_id>', methods=['POST'])
def delete_task_route(task_id):
    error = None
    success = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = get_task_by_id(task_id)

    if not task:
        error = 'Task not found.'
        tasks_list = get_tasks_by_user(session['user_id'])
        return render_template('tasks.html', tasks=tasks_list, now=datetime.now().date(), error=error)

    if task['user_id'] != session['user_id']:
        error = 'You are not authorized to delete this task.'
        tasks_list = get_tasks_by_user(session['user_id'])
        return render_template('tasks.html', tasks=tasks_list, now=datetime.now().date(), error=error)

    if delete_task(task_id):
        success = 'Task deleted successfully!'
    else:
        error = 'Failed to delete task. Please try again.'

    tasks_list = get_tasks_by_user(session['user_id'])
    return render_template('tasks.html', tasks=tasks_list, now=datetime.now().date(), error=error, success=success)


@app.route('/complete-task/<int:task_id>')
def complete_task(task_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = get_task_by_id(task_id)

    if not task:
        return redirect(url_for('tasks'))

    # Security check
    if task['user_id'] != session['user_id']:
        return redirect(url_for('tasks'))

    mark_task_completed(task_id)

    return redirect(url_for('tasks'))


def parse_study_plan(plan_text):
    if not plan_text:
        return None
    try:
        clean_lines = []
        for line in plan_text.strip().split('\n'):
            cleaned = line.strip()
            # Clean markdown bold/italic tags and header hashes
            cleaned = cleaned.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
            cleaned = cleaned.lstrip('#').strip()
            clean_lines.append(cleaned)
            
        days = []
        current_day = None
        current_session = None
        summary = {}
        in_summary = False
        
        for line in clean_lines:
            if not line:
                continue
                
            if "study summary" in line.lower():
                in_summary = True
                continue
                
            if in_summary:
                clean_line = line.lstrip('-*• ').strip()
                if ':' in clean_line:
                    key, val = clean_line.split(':', 1)
                    summary[key.strip()] = val.strip()
                else:
                    summary[clean_line] = ""
                continue
                
            is_date = False
            parts = line.split()
            if parts:
                first_word = parts[0]
                if '-' in first_word and first_word.replace('-', '').isdigit():
                    is_date = True
                elif first_word.isdigit() and len(first_word) == 4:
                    is_date = True
                    
            if is_date:
                current_day = {
                    'date': line,
                    'sessions': []
                }
                days.append(current_day)
                current_session = None
                continue
                
            if line.lower().startswith("session"):
                title = line
                duration = ""
                if '(' in line and ')' in line:
                    start = line.find('(')
                    end = line.find(')')
                    duration = line[start+1:end]
                    title = line[:start].strip()
                
                if ':' in title:
                    title = title.split(':', 1)[1].strip()
                    
                current_session = {
                    'title': title,
                    'duration': duration,
                    'focus': '',
                    'break': ''
                }
                if current_day is not None:
                    current_day['sessions'].append(current_session)
                continue
                
            if line.lower().startswith("focus:"):
                if current_session:
                    current_session['focus'] = line.split(':', 1)[1].strip()
                continue
            elif line.lower().startswith("break:"):
                if current_session:
                    current_session['break'] = line.split(':', 1)[1].strip()
                continue
                
            if current_session:
                if current_session['focus']:
                    current_session['focus'] += " " + line
                else:
                    current_session['focus'] = line
                    
        return {
            'days': days,
            'summary': summary
        }
    except Exception as e:
        print("Parsing Study Plan Error:", e)
        return None


def parse_workload_report(report_text):
    if not report_text:
        return None
    try:
        clean_lines = []
        for line in report_text.strip().split('\n'):
            cleaned = line.strip()
            # Clean markdown bold/italic tags and header hashes
            cleaned = cleaned.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
            cleaned = cleaned.lstrip('#').strip()
            clean_lines.append(cleaned)

        sections = {
            'status': '',
            'assessment': '',
            'urgent_tasks': [],
            'recommendations': []
        }
        current_section = None
        
        for line in clean_lines:
            if not line:
                continue
                
            lower_line = line.lower()
            if "workload status:" in lower_line or lower_line.startswith("workload status"):
                current_section = 'status'
                if ':' in line:
                    val = line.split(':', 1)[1].strip()
                    if val:
                        sections['status'] = val
                continue
            elif "productivity assessment:" in lower_line or lower_line.startswith("productivity assessment"):
                current_section = 'assessment'
                if ':' in line:
                    val = line.split(':', 1)[1].strip()
                    if val:
                        sections['assessment'] = val
                continue
            elif "urgent tasks:" in lower_line or lower_line.startswith("urgent tasks"):
                current_section = 'urgent_tasks'
                continue
            elif "recommendations:" in lower_line or lower_line.startswith("recommendations"):
                current_section = 'recommendations'
                continue
                
            if current_section == 'status':
                if sections['status']:
                    sections['status'] += " " + line
                else:
                    sections['status'] = line
            elif current_section == 'assessment':
                if sections['assessment']:
                    sections['assessment'] += " " + line
                else:
                    sections['assessment'] = line
            elif current_section == 'urgent_tasks':
                task = line.lstrip('-*• ').strip()
                sections['urgent_tasks'].append(task)
            elif current_section == 'recommendations':
                rec = line.lstrip('-*• ').strip()
                sections['recommendations'].append(rec)
                
        status_text = sections['status']
        level = 'Moderate'
        if 'heavy' in status_text.lower():
            level = 'Heavy'
        elif 'light' in status_text.lower():
            level = 'Light'
            
        sections['level'] = level
        return sections
    except Exception as e:
        print("Parsing Workload Report Error:", e)
        return None


@app.route('/study-plan')
def study_plan():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    plan = get_latest_study_plan(session['user_id'])
    parsed_plan = None
    if plan:
        parsed_plan = parse_study_plan(plan['plan_text'])
    
    return render_template('study_plan.html', plan=plan, parsed_plan=parsed_plan)


@app.route('/generate-plan')
def generate_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    active_tasks = get_active_tasks_for_plan(session['user_id'])

    generated_plan = generate_study_plan(active_tasks)

    if generated_plan == "Unable to generate study plan at the moment. Please try again.":
        return redirect(url_for('study_plan'))

    save_study_plan(session['user_id'], generated_plan)

    '''# Automatically generate workload analysis when study plan is updated
    tasks = get_tasks_by_user(session['user_id'])
    stats = get_dashboard_stats(session['user_id'])
    
    total = stats['total_tasks'] if stats else 0
    completion_rate = 0
    deadline_rate = 0
    productivity_score = 0

    if total > 0:
        completion_rate = round((stats['completed_tasks'] / total) * 100)
        deadline_rate = round(((total - stats['expired_tasks']) / total) * 100)
        productivity_score = round((completion_rate * 0.8) + (deadline_rate * 0.2))

    #analysis = generate_workload_analysis(tasks, stats, productivity_score)

    #if analysis != "Analysis could not be generated at the moment. Please try again later":
        #save_workload_report(session['user_id'], analysis)
    '''
    return redirect(url_for('study_plan'))


@app.route('/workload-analysis')
def workload_analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    report = get_latest_workload_report(session['user_id'])
    parsed_report = None
    if report:
        parsed_report = parse_workload_report(report['report_text'])

    return render_template('workload_analysis.html', report=report, parsed_report=parsed_report)

@app.route('/generate-analysis')
def generate_analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tasks = get_tasks_by_user(session['user_id'])
    stats = get_dashboard_stats(session['user_id'])
    
    total = stats['total_tasks'] if stats else 0
    completion_rate = 0
    deadline_rate = 0
    productivity_score = 0

    if total > 0:
        completion_rate = round((stats['completed_tasks'] / total) * 100)
        deadline_rate = round(((total - stats['expired_tasks']) / total) * 100)
        productivity_score = round((completion_rate * 0.8) + (deadline_rate * 0.2))

    analysis = generate_workload_analysis(tasks, stats, productivity_score)

    if analysis != "Analysis could not be generated at the moment. Please try again later":
        save_workload_report(session['user_id'], analysis)

    return redirect(url_for('workload_analysis'))

if __name__ == '__main__':
    app.run(debug=True)