import os
from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host=os.environ.get('APP_HOST', '0.0.0.0'), port=int(os.environ.get('APP_PORT', 8000)))