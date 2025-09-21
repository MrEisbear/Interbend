# Project To-Do and Feature Ideas

This file tracks potential new features and improvements for the Interbend banking system.

## Feature Suggestions

1.  **Automated Payroll System:**
    *   **Description:** Instead of requiring users to manually call the `/collect` endpoint, a scheduled script could run periodically (e.g., every 24 hours) to automatically distribute salaries to all eligible users.
    *   **Benefits:** Improves user experience, ensures consistent pay, and reduces repeated API calls to the server.

2.  **User Transaction History:**
    *   **Description:** Create a new API endpoint (e.g., `GET /transactions`) that allows an authenticated user to retrieve a paginated list of their own transaction history.
    *   **Benefits:** Provides users with transparency and a way to track their finances, which is a core feature of any banking application.

3.  **Comprehensive Admin Panel:**
    *   **Description:** Develop a simple web-based dashboard for administrators. This would be more user-friendly than using API endpoints for administrative tasks.
    *   **Features:**
        *   View and manage all users (e.g., edit balance, change job, view profile).
        *   Manage jobs and their corresponding salaries.
        *   View system-wide transaction logs and financial statistics.
        *   A secure login system for administrators.
    *   **Benefits:** Greatly simplifies the management of the roleplay economy and provides better oversight.
