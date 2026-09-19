# 📝 Blog Platform with Comments

A full-stack blogging platform built using **Flask, MySQL, HTML, CSS and RESTful APIs**.

Users can create an account, securely log in, publish blog posts, edit or delete their own posts, and interact with posts through comments.

## 🚀 Features

* User registration and login
* Password hashing and authentication
* Create blog posts
* View all blog posts
* View individual blog posts
* Edit own blog posts
* Delete own blog posts
* Add comments to blog posts
* MySQL database integration
* RESTful API for posts and comments
* Responsive and professional UI
* Environment variables for sensitive configuration

## 🛠️ Technologies Used

### Backend

* Python
* Flask
* Flask-Login
* Flask-SQLAlchemy
* PyMySQL

### Frontend

* HTML5
* CSS3
* Jinja2 Templates

### Database

* MySQL

### API

* RESTful APIs
* JSON

### Tools

* Git
* GitHub
* VS Code

## 📂 Project Structure

```text
blog-platform/
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── posts.html
│   ├── create_post.html
│   ├── post.html
│   └── edit_post.html
│
└── static/
    └── style.css
```

## 🗄️ Database

The application uses a MySQL database named:

```text
blog_platform
```

### Tables

* `users`
* `posts`
* `comments`

Relationships:

```text
User
 │
 ├── Posts
 │
 └── Comments

Post
 │
 └── Comments
```

## 🔗 REST API Endpoints

### Posts

| Method | Endpoint          | Description       |
| ------ | ----------------- | ----------------- |
| GET    | `/api/posts`      | Get all posts     |
| GET    | `/api/posts/<id>` | Get a single post |
| POST   | `/api/posts`      | Create a post     |
| PUT    | `/api/posts/<id>` | Update a post     |
| DELETE | `/api/posts/<id>` | Delete a post     |

### Comments

| Method | Endpoint                   | Description      |
| ------ | -------------------------- | ---------------- |
| GET    | `/api/posts/<id>/comments` | Get comments     |
| POST   | `/api/posts/<id>/comments` | Create a comment |

## ⚙️ How to Run

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd blog-platform
```

### 2. Create a virtual environment

Using Conda:

```bash
conda create -n blogenv python=3.12
conda activate blogenv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```text
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_DATABASE=blog_platform
SECRET_KEY=your_secret_key
```

### 5. Create the MySQL database

```sql
CREATE DATABASE blog_platform;
```

Create the required `users`, `posts`, and `comments` tables using the project database schema.

### 6. Run the Flask application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 🔐 Security

Sensitive configuration such as the MySQL password and Flask secret key is stored in `.env`.

The `.env` file is excluded from Git using `.gitignore`.

Passwords are stored using Werkzeug password hashing instead of plain text.

## 🎯 Learning Outcomes

This project demonstrates practical experience with:

* Flask web application development
* MVC-style application structure
* User authentication
* Password hashing
* CRUD operations
* MySQL database integration
* SQLAlchemy ORM
* REST API development
* JSON request/response handling
* HTML/CSS frontend development
* Git and GitHub version control

## 👩‍💻 Author

**Savi Kavi**

B.E. Electronics and Communication Engineering

Interested in:

* Full Stack Development
* Python Development
* Data Analytics
* Data Science
