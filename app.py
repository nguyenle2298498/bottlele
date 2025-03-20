from flask import Flask, request, render_template, session, redirect, url_for
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import StartBotRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
import os, re, time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
        session['api_id'] = request.form['api_id']
        session['api_hash'] = request.form['api_hash']
        session['phone'] = request.form['phone']
        session['bot_link'] = request.form['bot_link']
        session['group_links'] = request.form['group_links'].split('\n')
        return redirect(url_for('run_bot'))
    return render_template('index.html')

@app.route('/run_bot')
def run_bot():
    session_file = f"session_{session['phone']}"
    client = TelegramClient(session_file, int(session['api_id']), session['api_hash'])
    
    with client:
        if not client.is_user_authorized():
            client.send_code_request(session['phone'])
            return render_template('otp.html')
    
    return redirect(url_for('tasks'))

@app.route('/otp', methods=['POST'])
def otp():
    session_file = f"session_{session['phone']}"
    client = TelegramClient(session_file, int(session['api_id']), session['api_hash'])
    
    with client:
        client.sign_in(session['phone'], request.form['otp'])
    
    return redirect(url_for('tasks'))

@app.route('/tasks')
def tasks():
    session_file = f"session_{session['phone']}"
    client = TelegramClient(session_file, int(session['api_id']), session['api_hash'])
    
    with client:
        bot_username, referral_code = extract_bot_info(session['bot_link'])
        if bot_username and referral_code:
            bot_entity = client.get_entity(bot_username)
            client(StartBotRequest(bot=bot_entity, peer=bot_entity, start_param=referral_code))
        
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
        
        client.send_message(bot_username, "Tôi đã tham gia tất cả các nhóm!")
    
    return "Hoàn thành nhiệm vụ!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
