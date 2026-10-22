# app.py - KHALED VIP Feedback Server v2 & v3
import os
import base64
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔑 1. Bot Bilgileri (v2 için)
BOT_TOKEN_V2 = "8199864222:AAF5nWh9tCl-tcn5I_N6PntBVk5V_tPV3vM"
CHAT_ID_V2 = "-1004355323124"

# 🔑 2. Bot Bilgileri (v3 için - BURAYI DEĞİŞTİR!)
# Eğer 2. kanal için farklı bir bot açtıysan tokeni ve chat_id'yi buraya yaz. 
# Şimdilik aynı yere atması için aynı bıraktım, değiştirebilirsin.
BOT_TOKEN_V3 = "8199864222:AAF5nWh9tCl-tcn5I_N6PntBVk5V_tPV3vM" 
CHAT_ID_V3 = "-1004355323124"

@app.route('/')
def home():
    return jsonify({
        "status": True, 
        "message": "KHALED VIP Feedback Server (v2 & v3) ONLINE",
        "version": "3.0"
    })

@app.route('/api/feedback', methods=['POST'])
@app.route('/api/feedback/v3', methods=['POST']) # Lua'daki v3 isteğini burada yakalıyoruz
def feedback():
    try:
        # Hangi endpoint'e geldiğini kontrol et
        is_v3 = request.path.endswith('/v3')
        
        # JSON veya Form-Data al
        if request.content_type and 'application/json' in request.content_type:
            data = request.json or {}
            base64_image = data.get('base64_image', '')
            caption = data.get('caption', '')
        else:
            base64_image = request.form.get('base64_image', '')
            caption = request.form.get('caption', '')
        
        if not base64_image:
            return jsonify({"status": False, "error": "No image provided"}), 400
        
        # Base64 decode
        try:
            base64_image = base64_image.replace('%2B', '+').replace('%2F', '/').replace('%3D', '=')
            image_bytes = base64.b64decode(base64_image)
        except Exception as e:
            return jsonify({"status": False, "error": f"Base64 decode failed: {e}"}), 400
        
        # Hedef Botu ve Chat ID'yi seç
        target_token = BOT_TOKEN_V3 if is_v3 else BOT_TOKEN_V2
        target_chat = CHAT_ID_V3 if is_v3 else CHAT_ID_V2

        # Telegram'a gönder
        url = f"https://api.telegram.org/bot{target_token}/sendPhoto"
        files = {'photo': ('screenshot.png', image_bytes, 'image/png')}
        payload = {
            'chat_id': target_chat,
            'caption': caption[:1024],
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=payload, files=files, timeout=60)
        
        if response.status_code == 200:
            return jsonify({"status": True, "message": f"Sent to Telegram (v3: {is_v3})"})
        else:
            return jsonify({"status": False, "error": response.text}), 500
            
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)