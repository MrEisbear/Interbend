# Project To-Do and Feature Ideas

This file tracks potential new features and improvements for the Interbend banking system.

## Feature Suggestions

1.  **Automated Payroll System**
    * **Description:** Instead of requiring users to manually call the `/collect` endpoint, a scheduled script could run periodically to automatically distribute salaries to all eligible users.
    * **Benefits:** Improves user experience, ensures consistent pay, and reduces repeated API calls to the server.
    * **Status:** Under Review
    * **Note:** Due to system concept, needs to be modified to only pay active users.
    * **Alternative:** Implement system to verify host is online; add admin route to control server availability.

2.  **User Transaction History**
    * **Description:** Create API endpoint for retrieving paginated transaction history.
    * **Benefits:** Provides transparency and financial tracking for users.
    * **Status:** COMPLETED
    * **Note:** Needs verification testing.

3.  **Changeable Tax Rate**
    * **Description:** Add system for dynamic tax rate adjustment through admin interface.
    * **Benefits:** Allows economic control and flexibility for different transaction types.
    * **Status:** In Progress
    * **Implementation:** Store in database for persistence, add admin routes for modification.

4.  **User Roles System**
    * **Description:** Implement comprehensive role-based access control (RBAC).
    * **Benefits:** Enables different permissions for police, government, admin, and regular users.
    * **Status:** Not Started
    * **Required Features:**
        - Role assignment and management
        - Permission hierarchy
        - Role-specific interfaces
        - Audit logging for role changes

5.  **Frontend Development**
    * **Description:** Create user interface for the banking system.
    * **Benefits:** Provides intuitive access to banking features.
    * **Status:** Not Started
    * **Components Needed:**
        - User dashboard
        - Transaction interface
        - Admin control panel
        - Role-specific views