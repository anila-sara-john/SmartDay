# SmartDay — AI-Powered Student Planner & Academic Productivity Assistant

SmartDay is a full-stack AI-powered web application designed to help university students manage academic workload, plan study schedules intelligently, and improve productivity using real-time data and generative AI.

It combines traditional task management with Google Gemini AI to automatically generate personalized study plans and workload insights based on a student’s deadlines, priorities, and estimated effort.

Built with Flask, MySQL, and Bootstrap, SmartDay transforms scattered academic tasks into a structured, AI-driven daily plan that helps students avoid procrastination, balance workload, and stay consistent.

## **✨ Features**

### User Management
- User registration and secure login authentication  
- Session-based authentication using Flask  
- Password hashing using Werkzeug security utilities  

### Task Management System
- Create, edit, and delete academic tasks  
- Assign category, priority, deadline, and estimated hours  
- Track task status (Pending, In Progress, Completed)  
- Automatic overdue detection based on deadlines  
- Task ownership validation for security  

### Productivity Dashboard
- Real-time task statistics (Total, Pending, Completed, Overdue)  
- Completion Rate calculation  
- Deadline Success Rate tracking  
- Composite Productivity Score  
- Animated visual progress indicators  

### AI-Powered Study Planning
- Generates personalized day-by-day study schedules  
- Uses Google Gemini (`gemini-2.5-flash`) for intelligent planning  
- Breaks large tasks into manageable study sessions  
- Prioritizes tasks based on deadline and importance  
- Automatically balances workload across days  

### AI Workload Analysis
- Analyzes student workload using AI  
- Classifies workload as Light / Moderate / Heavy  
- Identifies urgent and overdue tasks  
- Provides actionable study recommendations  
- Helps prevent academic burnout  

### Smart Scheduling System
- Deadline-aware task prioritization  
- Estimated study hour integration  
- Dynamic redistribution of workload  
- AI-driven planning instead of manual scheduling  

### Insights & Analytics
- Productivity scoring system  
- Task completion tracking over time  
- Workload visualization  
- AI-generated academic performance insights  

### Security Features
- Password hashing (no plaintext storage)  
- SQL injection prevention using parameterized queries  
- User-based data isolation  
- Secure session handling using Flask secret key  

## **🛠️ Technology Stack**

### Backend
- **Flask (Python)** – Core web framework for routing, session management, and backend logic  
- **MySQL** – Relational database used for storing users, tasks, study plans, and workload reports  
- **mysql-connector-python** – Python connector for secure database communication  

### Artificial Intelligence
- **Google Gemini API (`gemini-2.5-flash`)** – Powers AI-generated study plans and workload analysis  
- **google-genai SDK** – Official Python SDK used to interact with Gemini models  

### Frontend
- **HTML5** – Structure of the web application  
- **CSS3 + Bootstrap 5.3** – Responsive and modern UI design  
- **Jinja2 Templates** – Dynamic server-side rendering in Flask  

### Security & Authentication
- **Werkzeug Security** – Password hashing and verification  
- **Flask Sessions** – User authentication and session management  
- **Environment Variables (.env)** – Secure storage of API keys and database credentials  

### Development Tools
- **Visual Studio Code** – Primary development environment  
- **MySQL Workbench** – Database design and management  
- **Git & GitHub** – Version control and project hosting  

### Deployment
- **Render** – Cloud deployment platform for hosting Flask web application  
- **Gunicorn** – Production-grade WSGI server for running Flask app  
- **TiDB Cloud / MySQL Cloud Database** – Cloud database hosting for production use  

## **⚙️ How the System Works**

SmartDay follows a structured workflow that connects user input, database operations, and AI-driven processing to generate intelligent study plans and workload insights.



### 1. User Authentication Flow
1. User registers with name, email, and password  
2. Password is securely hashed using Werkzeug  
3. Credentials are stored in MySQL database  
4. During login, password is verified and a session is created  
5. Session maintains user state across the application  

### 2. Task Management Flow
1. User creates a task with:
   - Title  
   - Category  
   - Priority  
   - Deadline  
   - Estimated hours  
2. Task is stored in MySQL under the logged-in user  
3. Tasks are retrieved and displayed in sorted order (by deadline)  
4. Users can update, delete, or mark tasks as completed  
5. Task status updates automatically reflect in dashboard analytics  

### 3. Productivity Calculation Flow
1. System fetches all user tasks from database  
2. Tasks are categorized into:
   - Completed  
   - Pending  
   - Overdue  
3. Metrics are calculated:
   - Completion Rate  
   - Deadline Success Rate  
   - Productivity Score  
4. Results are displayed using dashboard progress indicators  

### 4. AI Study Plan Generation Flow
1. User clicks “Generate Study Plan”  
2. System collects all active (non-completed) tasks  
3. Task data is formatted into a structured AI prompt  
4. Prompt is sent to **Google Gemini (gemini-2.5-flash)**  
5. AI returns a structured day-by-day study schedule  
6. Plan is stored in MySQL (study_plans table)  
7. Plan is parsed and displayed in a readable format  

### 5. AI Workload Analysis Flow
1. System gathers:
   - All tasks  
   - Productivity statistics  
   - Completion metrics  
2. Data is sent to Gemini AI for analysis  
3. AI classifies workload as:
   - Light  
   - Moderate  
   - Heavy  
4. AI returns:
   - Workload status  
   - Productivity assessment  
   - Urgent tasks  
   - Recommendations  
5. Report is stored and displayed in dashboard  

### 6. Overall Architecture Flow
User → Flask Routes → MySQL Database → AI (Gemini API) → Processed Output → UI (Dashboard / Pages)

## **🚀 Installation & Setup**

Follow these steps to run SmartDay locally on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/anila-sara-john/SmartDay
cd SmartDay
```
### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
```
Activate the environment:

- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Create a `.env` file in the root directory and add the following:
```bash
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_flask_secret_key

DB_HOST=your_database_host
DB_PORT=4000
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=smartday_db
```
### 5. Setup MySQL Database
- Create a database named `smartday_db`
- Import database schema from `database/schema.sql`
- Run it in MySQL Workbench or TiDB SQL editor to create required tables.
- Ensure database credentials match `.env` file

### 6. Run the Application
```bash
python app.py
```
### 7. Open in Browser
```bash
http://127.0.0.1:5000
```
Your application should now be running successfully!

## **📌 Credits**

This project, **SmartDay – AI-Powered Student Planner and Academic Productivity Assistant**, was developed as a full-stack academic project to demonstrate the integration of web development, database management, and artificial intelligence.

### AI & APIs Used
- **Google Gemini API (gemini-2.5-flash)** – Used for generating AI-powered study plans and workload analysis  
- **Google GenAI SDK** – Python SDK for interacting with Gemini models  

### Tools & Technologies
- Flask – Backend web framework  
- MySQL – Database management system  
- HTML, CSS, Bootstrap – Frontend design  
- Jinja2 – Template rendering engine  
- Gunicorn – Production WSGI server  
- Render – Cloud deployment platform  

### Learning Resources
- Flask Documentation – https://flask.palletsprojects.com/  
- MySQL Documentation – https://dev.mysql.com/doc/  
- Google Gemini API Docs – https://ai.google.dev/  

### Acknowledgements
Special thanks to all open-source communities and tutorials that helped in understanding full-stack development, AI integration, and deployment workflows.