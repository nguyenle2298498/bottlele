from flask import Flask, request, render_template, session, redirect, url_for
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import StartBotRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
import os, re, time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Thông tin API Telegram
API_ID = 25437670  # Thay bằng API ID của bạn
API_HASH = "7a60d938df5a25122326f007055013b6"  # Thay bằng API Hash của bạn

# Hàm trích xuất thông tin bot
def extract_bot_info(bot_link):
    match = re.search(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', bot_link)
    return (match.group(1), match.group(2)) if match else (None, None)

# Hàm trích xuất mã mời nhóm
def extract_invite_hash(group_link):
    match = re.search(r't\.me/\+([a-zA-Z0-9_-]+)', group_link)
    return match.group(1) if match else None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['phone'] = request.form['phone']
        session['bot_link'] = request.form['bot_link']
        session['group_links'] = request.form['group_links'].split('\n')
        return redirect(url_for('verify_otp'))
    return render_template('index.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    session_file = f"session_{session['phone']}"
    client = TelegramClient(session_file, API_ID, API_HASH)
    
    client.connect()
    if not client.is_user_authorized():
        try:
            client.send_code_request(session['phone'])
        except Exception as e:
            return f"Lỗi gửi mã OTP: {e}"
        
        if request.method == 'POST':
            try:
                client.sign_in(session['phone'], request.form['otp'])
                return redirect(url_for('tasks'))
            except Exception as e:
                return f"Lỗi xác thực OTP: {e}"
        return render_template('otp.html')
    return redirect(url_for('tasks'))

@app.route('/tasks')
def tasks():
    session_file = f"session_{session['phone']}"
    client = TelegramClient(session_file, API_ID, API_HASH)
    
    client.connect()
    if not client.is_user_authorized():
        return "Lỗi: Tài khoản chưa được xác thực."
    
    bot_username, referral_code = extract_bot_info(session['bot_link'])
    if bot_username and referral_code:
        try:
            bot_entity = client.get_entity(bot_username)
            client(StartBotRequest(bot=bot_entity, peer=bot_entity, start_param=referral_code))
        except Exception as e:
            return f"Lỗi khi tham gia bot: {e}"
    
    for group_link in session['group_links']:
        invite_hash = extract_invite_hash(group_link)
        try:
            if invite_hash:
                client(ImportChatInviteRequest(invite_hash))
            else:
                username = group_link.split("/")[-1]
                client(JoinChannelRequest(username))
        except Exception as e:
            return f"Lỗi tham gia nhóm {group_link}: {e}"
    
    try:
        client.send_message(bot_username, "Tôi đã tham gia tất cả các nhóm!")
    except Exception as e:
        return f"Lỗi gửi tin nhắn: {e}"
    
    return "Hoàn thành nhiệm vụ!"

if __name__ == '__main__':
    import sys
    if 'input' in sys.modules:
        sys.modules['input'] = lambda: session.get('phone', '')
    app.run(debug=True, host='0.0.0.0', port=5000)
