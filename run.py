from interbend import create_app
from interbend.db import init_db

# Initialize the database (creates tables if they don't exist)
init_db()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)