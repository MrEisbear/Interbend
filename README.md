# Interbend API

Interbend is a Flask-based web application that provides a backend API for managing user balances and transactions. It features a robust authentication system using JWT and includes a separate set of administrative endpoints for system management. The application is designed to be extensible and can be used as a foundation for a variety of financial applications.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/interbend.git
    cd interbend
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install Flask python-dotenv mysql-connector-python PyJWT
    ```

4.  **Set up the environment variables:**
    Create a `.env` file in the root directory of the project and add the following variables:
    ```
    JWT_KEY=your_secret_jwt_key
    JWT_EXPIRATION=30
    DB_HOST=your_database_host
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_NAME=your_database_name
    ADMIN_KEY=your_secret_admin_key
    COLLECT_COOLDOWN=30
    ```

## Usage

To start the application, run the following command in the root directory of the project:
```bash
python run.py
```
The application will start in debug mode on `http://127.0.0.1:5000`.

## API Endpoints

### Authentication

-   **`POST /register`**: Creates a new user account.
    -   **Request Body**: `{ "username": "testuser", "email": "test@example.com", "password": "password123" }`
    -   **Response**: Sets a JWT token in an HTTP-only cookie and returns a success message.

-   **`POST /login`**: Logs in a user.
    -   **Request Body**: `{ "bid": "your_user_bid", "password": "password123" }`
    -   **Response**: Sets a JWT token in an HTTP-only cookie and returns a success message.

### Transactions

-   **`GET /balance?bid=<user_bid>`**: Retrieves the balance of a user.
    -   **Response**: `{ "balance": 100.00 }`

-   **`POST /collect`**: Collects the salary for the authenticated user.
    -   **Authentication**: JWT token required.
    -   **Response**: A success message and the new balance.

-   **`POST /transfer`**: Transfers a specified amount from the authenticated user to another user.
    -   **Authentication**: JWT token required.
    -   **Request Body**: `{ "to": "recipient_bid", "amount": 50.00, "note": "Payment for services" }`
    -   **Response**: A success message.

### Admin

All admin endpoints require an admin key in the request body.

-   **`POST /admin/set-job`**: Sets the job for a user.
    -   **Request Body**: `{ "bid": "user_bid", "job": 1, "key": "your_admin_key" }`
    -   **Response**: A success message.

-   **`POST /admin/add-money`**: Adds money to a user's account.
    -   **Request Body**: `{ "bid": "user_bid", "amount": 100.00, "key": "your_admin_key" }`
    -   **Response**: A success message.

-   **`POST /admin/change-password`**: Changes the password for a user.
    -   **Request Body**: `{ "bid": "user_bid", "password": "new_password", "key": "your_admin_key" }`
    -   **Response**: A success message.
