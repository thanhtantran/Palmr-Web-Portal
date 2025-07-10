import os
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')  # ← important!
)

app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    # Serve static file if it exists
    requested_file = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(requested_file):
        return send_from_directory(static_folder_path, path)

    # Otherwise render index.html from templates
    return render_template("index.html", time=int(datetime.utcnow().timestamp()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
