from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

# ✅ Complete CORS Configuration - This should fix the issue
CORS(app, 
     origins=[
         "https://demobookvaultui.vercel.app",
         "https://demobookvault.vercel.app", 
         "http://localhost:3000",
         "http://localhost:5173"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     supports_credentials=True
)

# ✅ Additional CORS headers for all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in [
        'https://demobookvaultui.vercel.app',
        'https://demobookvault.vercel.app',
        'http://localhost:3000',
        'http://localhost:5173'
    ]:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# ✅ Handle preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'message': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# 🗃️ SQLite connection
conn = sqlite3.connect('bookvault.db', check_same_thread=False)
cursor = conn.cursor()

# 🔗 Import Blueprints
from app.routes.issue_book import issue_book_bp
from app.routes.return_book import return_book_bp
from app.routes.transactions import transactions_bp
from app.routes.admin_login import admin_bp
from app.routes.book_routes import book_bp
from app.routes.member_routes import member_bp
from app.routes.analytics import analytics_bp

# 📦 Register Blueprints
app.register_blueprint(issue_book_bp)
app.register_blueprint(return_book_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(book_bp)
app.register_blueprint(member_bp)
app.register_blueprint(analytics_bp)

# ✅ Health check
@app.route('/ping')
def ping():
    return jsonify({"status": "ok"}), 200

# 🏠 Root
@app.route('/')
def home():
    return "📚 BookVault Backend is Running ✅"

# 🖼️ Cover update
@app.route("/api/update-cover", methods=["POST"])
def update_cover():
    data = request.get_json()
    title = data.get("title")
    cover_url = data.get("cover_url")
    
    try:
        cursor.execute("""
            UPDATE books
            SET cover_url = ?
            WHERE LOWER(title) LIKE LOWER(?)
        """, (cover_url, f"%{title}%"))
        conn.commit()
        return jsonify({"message": "Cover updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🏁 Start server
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
