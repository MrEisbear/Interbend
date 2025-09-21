# Project To-Do and Feature Ideas

This file tracks potential new features and improvements for the Interbend banking system.

## Feature Suggestions

1.  **Automated Payroll System:**
    *   **Description:** Instead of requiring users to manually call the `/collect` endpoint, a scheduled script could run periodically (e.g., every 24 hours) to automatically distribute salaries to all eligible users.
    *   **Benefits:** Improves user experience, ensures consistent pay, and reduces repeated API calls to the server.
    * **Important:** Due to the concept of this whole system it needs to be considered to only pay users who are attend. Bad Idea.
    * **Alternative:** Implement system to make sure you can only collect if the host is online. Make admin route to open server (set global bool)

2.  **User Transaction History:**
    *   **Description:** Create a new API endpoint (e.g., `GET /transactions`) that allows an authenticated user to retrieve a paginated list of their own transaction history.
    *   **Benefits:** Provides users with transparency and a way to track their finances, which is a core feature of any banking application.

    * FINISHED: PLEASE CHECK IF WORKING!