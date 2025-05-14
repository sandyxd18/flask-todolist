from app import create_app, db, create_admin_user
from dotenv import load_dotenv

load_dotenv()

app = create_app()

with app.app_context():
    from app.models import User, Task
    db.create_all()
    create_admin_user()

if __name__ == '__main__':
    app.run(debug=True)
