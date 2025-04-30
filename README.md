# ProjX

# ProjX – Student Project Collaboration Platform

ProjX is a mini web-based platform that allows students to **create, join, and manage academic project groups** easily. It provides a centralized system for project discovery, collaboration, and team role management.

---

## 🚀 Features

- 🔐 User registration & login
- 📋 Create and post new projects
- 🔍 Search/filter projects by status, keywords, roles
- 👥 Join projects and view team members
- 🧑‍💼 Assign and manage project roles (e.g., Developer, Designer)
- 👨‍🏫 Project leader and co-leader assignment
- 📝 View project details including members, roles, and updates
- ⚙️ Simple user profile editing
- 📌 Status tags for Ongoing/Completed projects

---

## 📚 Tech Stack

- **Frontend:** HTML, CSS, Bootstrap, Jinja2
- **Backend:** Python (Flask), SQLAlchemy
- **Database:** MySQL
- **Tools:** VS Code, Git, MySQL Workbench

---

## 🗂️ Project Structure

projx/ │ ├── app.py # Main Flask app ├── templates/ # HTML templates (Jinja2) │ ├── login.html │ ├── signup.html │ ├── dashboard.html │ ├── project_details.html │ └── ... ├── static/ # CSS, JS, images │ └── styles.css ├── models.py # SQLAlchemy models ├── db_config.py # Database connection ├── README.md # You're here! └── requirements.txt # Dependencies

---

## 🧑‍💻 Database Schema (Simplified)

- **Users:** `user_id`, `name`, `email`, `username`, `password`, ...
- **Projects:** `project_id`, `project_name`, `description`, `status`, ...
- **Roles:** `role_id`, `role_name`
- **ProjectMembership:** composite PK (`project_id`, `user_id`), `role_id`, `is_leader`, `joined_at`
- **ProjectUpdates:** `update_id`, `project_id`, `content`, `timestamp`

---

## ✅ Sample Queries

```sql
-- Show all ongoing projects
SELECT * FROM projects WHERE status = 'Ongoing';

-- List members of a specific project
SELECT u.name, r.role_name FROM project_members pm
JOIN users u ON pm.user_id = u.user_id
JOIN roles r ON pm.role_id = r.role_id
WHERE pm.project_id = 1;
