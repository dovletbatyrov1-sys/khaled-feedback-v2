# app.py - KHALED VIP Feedback Server (Dual Channel Support)
import os
import base64
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔑 1. Bot Bilgileri (v2 Kanalı - SHADOW ve KHALED 1. Feedback)
BOT_TOKEN_V2 = "8199864222:AAF5nWh9tCl-tcn5I_N6PntBVk5V_tPV3vM"
CHAT_ID_V2 = "-1004355323124"

# 🔑 2. Bot Bilgileri (v3 Kanalı - KHALED 2. Feedback)
BOT_TOKEN_V3 = "8888189556:AAHdv1K-eVw6EoZSxMug_ExR5_K89mLuy9k" 
CHAT_ID_V3 = "-1003709911230"

@app.route('/')
def home():
    return jsonify({
        "status": True, 
        "message": "KHALED VIP Feedback Server ONLINE (Dual Channel)",
        "version": "3.1"
    })

# Hem /api/feedback hem de /api/feedback/v3 isteklerini karşılar
@app.route('/api/feedback', methods=['POST'])
@app.route('/api/feedback/v3', methods=['POST'])
def feedback():
    try:
        # İsteğin nereden geldiğini kontrol et (v3 mü, v2 mi?)
        is_v3 = request.path.endswith('/v3')
        
        # JSON veya Form-Data formatını otomatik algıla
        if request.content_type and 'application/json' in request.content_type:
            data = request.json or {}
            base64_image = data.get('base64_image', '')
            caption = data.get('caption', '')
        else:
            base64_image = request.form.get('base64_image', '')
            caption = request.form.get('caption', '')
        
        if not base64_image:
            return jsonify({"status": False, "error": "No image provided"}), 400
        
        # Base64 URL decode ve decode işlemi
        try:
            base64_image = base64_image.replace('%2B', '+').replace('%2F', '/').replace('%3D', '=')
            image_bytes = base64.b64decode(base64_image)
        except Exception as e:
            return jsonify({"status": False, "error": f"Base64 decode failed: {e}"}), 400
        
        # Hedef Botu ve Chat ID'yi seç
        target_token = BOT_TOKEN_V3 if is_v3 else BOT_TOKEN_V2
        target_chat = CHAT_ID_V3 if is_v3 else CHAT_ID_V2

        # Telegram API'sine gönder
        url = f"https://api.telegram.org/bot{target_token}/sendPhoto"
        files = {'photo': ('screenshot.png', image_bytes, 'image/png')}
        payload = {
            'chat_id': target_chat,
            'caption': caption[:1024], # Telegram caption limiti
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=payload, files=files, timeout=60)
        
        if response.status_code == 200:
            return jsonify({"status": True, "message": f"Sent to Telegram (Channel: {'v3' if is_v3 else 'v2'})"})
        else:
            return jsonify({"status": False, "error": response.text}), 500
            
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)