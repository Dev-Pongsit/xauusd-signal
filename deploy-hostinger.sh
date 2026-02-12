# ============================
# 🚀 HOSTINGER VPS DEPLOYMENT GUIDE
# ============================
# สำหรับ deploy XAUUSD AI Signal บน Hostinger VPS
# ค่าใช้จ่าย: ~$5/เดือน (KVM1 plan)

# ========================================
# STEP 1: ซื้อ Hostinger VPS
# ========================================
# 1. ไปที่ hostinger.com/vps-hosting
# 2. เลือก KVM 1 plan ($4.99/mo) — เพียงพอแล้ว
#    - 1 vCPU, 4GB RAM, 50GB NVMe
# 3. เลือก OS: Ubuntu 22.04
# 4. เลือก Server Location: Singapore (ใกล้ไทยสุด)
# 5. จ่ายเงิน → จะได้ IP + root password

# ========================================
# STEP 2: เชื่อมต่อ VPS
# ========================================
# เปิด Terminal (Mac/Linux) หรือ PowerShell (Windows)
ssh root@YOUR_VPS_IP

# ========================================
# STEP 3: ติดตั้ง dependencies
# ========================================
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git -y

# ========================================
# STEP 4: Upload โปรเจกต์
# ========================================
# วิธีที่ 1: Git (แนะนำ)
cd /opt
git clone https://github.com/YOUR_USER/xauusd-ai-signal.git
cd xauusd-ai-signal

# วิธีที่ 2: SCP upload จากเครื่องตัวเอง
# scp -r ./xauusd-ai-signal root@YOUR_VPS_IP:/opt/

# ========================================
# STEP 5: Setup Python environment
# ========================================
cd /opt/xauusd-ai-signal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ========================================
# STEP 6: Config
# ========================================
cp .env.example .env
nano .env
# ใส่ ANTHROPIC_API_KEY
# ใส่ TELEGRAM_BOT_TOKEN + CHAT_ID (ถ้าต้องการ)
# ตั้ง SECRET_KEY เป็น string สุ่ม

# ========================================
# STEP 7: ทดสอบ
# ========================================
python server.py
# เปิด browser → http://YOUR_VPS_IP:5000

# ========================================
# STEP 8: รันถาวร (systemd service)
# ========================================
cat > /etc/systemd/system/xauusd-signal.service << 'EOF'
[Unit]
Description=XAUUSD AI Signal System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/xauusd-ai-signal
Environment=PATH=/opt/xauusd-ai-signal/venv/bin:/usr/bin
ExecStart=/opt/xauusd-ai-signal/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 120 \
    server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable xauusd-signal
systemctl start xauusd-signal

# เช็คสถานะ
systemctl status xauusd-signal

# ========================================
# STEP 9: (Optional) Setup domain + HTTPS
# ========================================
# ถ้ามี domain name:
apt install nginx certbot python3-certbot-nginx -y

cat > /etc/nginx/sites-available/xauusd << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/xauusd /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# HTTPS
certbot --nginx -d your-domain.com

# ========================================
# USEFUL COMMANDS
# ========================================
# ดู logs
journalctl -u xauusd-signal -f

# Restart service
systemctl restart xauusd-signal

# Manual scan
cd /opt/xauusd-ai-signal
source venv/bin/activate
python -c "from app.runner import run_scan; run_scan()"
