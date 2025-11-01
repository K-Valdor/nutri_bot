#!/bin/bash
set -e

APP_DIR="/opt/nutrition-bot"
SERVICE_NAME="nutrition-bot"

echo "🚀 Starting deployment..."

# Создаем директории (это может делать сам пользователь в своей домашней директории)
echo "📁 Creating directories..."
mkdir -p $APP_DIR/{bot,data,logs}

# Копируем код
echo "📝 Copying bot files..."
cp -r bot/* $APP_DIR/bot/ 2>/dev/null || true
cp requirements.txt $APP_DIR/

# Устанавливаем зависимости
echo "📦 Installing dependencies..."
cd $APP_DIR
python3 -m pip install --user -r requirements.txt

# Systemd service setup (только конкретные команды с sudo)
echo "⚙️ Setting up service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

cat << EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=Nutrition Bot
After=network.target

[Service]
Type=simple
User=nutrition-bot
Group=nutrition-bot
WorkingDirectory=$APP_DIR/bot
EnvironmentFile=$APP_DIR/.env
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5
StandardOutput=file:$APP_DIR/logs/bot.log
StandardError=file:$APP_DIR/logs/bot-error.log

[Install]
WantedBy=multi-user.target
EOF

# Systemd commands with limited sudo
echo "🔄 Configuring service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo "▶️ Starting bot..."
sudo systemctl start $SERVICE_NAME

# Check status
echo "📊 Checking status..."
sleep 3
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "🎉 Bot deployed successfully!"
    echo "📋 Service status:"
    sudo systemctl status $SERVICE_NAME --no-pager -l
else
    echo "❌ Deployment failed!"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    exit 1
fi