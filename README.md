# Car Dealership Inventory System

## 1. Project Overview

The Car Dealership Inventory System is a web application developed using Python, FastAPI, SQLite, HTML, CSS, and JavaScript.

It allows users to view available vehicles, search the inventory, register and log in, and purchase vehicles. Administrators can manage vehicle records, delete vehicles, and restock inventory.

## 2. Objectives

- Develop a REST API for managing vehicle inventory.
- Store vehicle and user data persistently in SQLite.
- Implement registration and token-based authentication.
- Apply role-based authorization for administrative operations.
- Allow users to search vehicles by relevant criteria.
- Prevent purchases when a vehicle is out of stock.
- Apply Test-Driven Development (TDD) and automated testing.

## 3. Technologies Used

- **Python:** Backend programming language.
- **FastAPI:** REST API framework.
- **SQLite:** Persistent database.
- **HTML, CSS, JavaScript:** Frontend interface.
- **pytest:** Automated testing.
- **Git:** Version control.

## 4. Main Features

### Authentication
- User registration and login.
- Password hashing.
- Signed authentication tokens.
- Admin and regular-user roles.

### Vehicle Inventory
- Add, view, search, update, and delete vehicles.
- Search by make, model, category, and price range.
- Purchase vehicles and reduce available quantity.
- Restock vehicles using administrator access.
- Reject purchases when stock reaches zero.

### Authorization
- Adding and updating vehicles require administrator access.
- Deleting and restocking vehicles require administrator access.
- Purchasing requires authentication.

## 5. Project Structure

```text
car-dealership/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── auth.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── frontend/
│   └── index.html
├── create_admin.py
├── requirements.txt
├── README.md
├── PROMPTS.md
└── .gitignore
```

## 6. Setup and Installation

### Prerequisites
- Python installed.
- pip available through Python.
- Git installed for version control.

### Install dependencies

Open a terminal in the project directory and create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Configure the application

Set a secret for local development in Windows Command Prompt:

```cmd
set JWT_SECRET=replace-with-a-long-random-secret
```

Use a strong, private secret in actual deployments. Do not commit secrets to Git.

### Create an administrator account

```bash
python create_admin.py
```

Follow the prompts to create an administrator username and password.

### Start the application

```bash
python -m uvicorn app.main:app --reload
```

Open the frontend at:

http://127.0.0.1:8000/

The interactive API documentation is available at:

http://127.0.0.1:8000/docs

## 7. Running Tests

Run the automated test suite:

```bash
python -m pytest -v
```

**Current test status:** 11 tests passed.

The tests cover vehicle listing, creation, searching, updating, deletion, purchasing, stock validation, authentication, and administrator restocking.

Update this report if the test results change before submission.

## 8. Test-Driven Development

The project uses automated tests to verify API behaviour. Development follows the Red-Green-Refactor approach:

1. **Red:** Write a test that fails for the expected reason.
2. **Green:** Implement the simplest code that makes the test pass.
3. **Refactor:** Improve code structure while keeping tests passing.

The Git commit history should be used to demonstrate the actual development process. Do not claim that every feature followed this cycle unless the commit history supports it.

## 9. Screenshots

Add screenshots of the following before submission:

- Inventory dashboard.
- Registration or login screen.
- Search results.
- Administrator inventory controls.
- Successful test execution.

Save the screenshots in a project folder such as `screenshots/` and embed them here using Markdown image links.

## 10. Security Notes

Passwords are hashed before being stored. Authentication tokens are signed and have an expiration time. Administrative operations are protected by role checks.

The current implementation uses a custom HMAC-signed token format rather than a standards-compliant JWT library. Tokens are signed, not encrypted. A production deployment should use a well-reviewed authentication implementation, HTTPS, secure secret management, and additional security controls.

## 11. My AI Usage

AI assistance was used during development to help understand FastAPI, authentication, database operations, frontend integration, automated testing, debugging, and project documentation.

AI suggestions were reviewed and applied during implementation. The project was tested locally, and the test suite currently reports 11 passing tests.

The developer remains responsible for understanding the code, verifying correctness, and ensuring that the final submission reflects the actual work completed.

The tools used, the specific assistance received, the changes made after reviewing suggestions, and personal reflections should be documented accurately in `PROMPTS.md` and this section before submission.

## 12. Future Improvements

- Add further automated tests for validation and authorization failures.
- Improve the frontend with more detailed forms and feedback.
- Use a standard JWT implementation and strengthen production security.
- Add deployment configuration and monitoring.

## 13. Author

Add the project author's name and any required course or internship details here.
