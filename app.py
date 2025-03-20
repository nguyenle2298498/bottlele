from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from telethon import TelegramClient

# Config Flask
app = Flask(__name__)
app.secret_key = "super_secret_key"

# Config Telegram
API_ID = 25437670  
API_HASH = "7a60d938df5a25122326f007055013b6"
client = TelegramClient("session", API_ID, API_HASH)

# Khởi tạo database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")

# Đăng ký
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Đăng ký thành công! Hãy đăng nhập.", "success")
        except:
            flash("Tài khoản đã tồn tại!", "danger")
        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# Đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            if username == "khachwen" and password == "Hehe12341":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "danger")

    return render_template("login.html")

# Dashboard user
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return f"Chào mừng {session['username']}! <a href='/logout'>Đăng xuất</a>"

# Trang admin
@app.route("/admin")
def admin():
    if "username" not in session or session["username"] != "khachwen":
        return "Bạn không có quyền truy cập!"
    return render_template("admin.html")

# Chức năng gửi tin nhắn Telegram
@app.route("/send_message", methods=["POST"])
def send_message():
    if "username" not in session or session["username"] != "khachwen":
        return "Bạn không có quyền!"

    message = request.form["message"]
    
    with client:
        client.loop.run_until_complete(client.send_message("me", message))
    
    flash("Đã gửi tin nhắn thành công!", "success")
    return redirect(url_for("admin"))

# Đăng xuất
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
