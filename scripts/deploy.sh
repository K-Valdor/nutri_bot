#!/bin/bash
set -e  # Выход при ошибке

APP_DIR="/opt/nutrition-bot"
SERVICE_NAME="nutrition-bot"

echo "🚀 Starting quick deployment..."

# Создаем директории
sudo mkdir -p $APP_DIR/{bot,data,logs}
sudo chown -R nutrition-bot:nutrition-bot $APP_DIR

# Копируем код
cd $APP_DIR
sudo -u nutrition-bot cp -r /tmp/nutrition-bot-deploy/bot/* $APP_DIR/bot/
sudo -u nutrition-bot cp /tmp/nutrition-bot-deploy/requirements.txt $APP_DIR/

# Устанавливаем зависимости
cd $APP_DIR
sudo -u nutrition-bot python3 -m pip install -r requirements.txt

# Systemd service (минимальный)
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Nutrition Bot
After=network.target

[Service]
Type=simple
User=nutrition-bot
WorkingDirectory=$APP_DIR/bot
Environment=TELEGRAM_BOT_TOKEN=$BOT_TOKEN
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Перезапускаем сервис
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

if systemctl is-active --quiet $SERVICE_NAME; then
    sudo systemctl restart $SERVICE_NAME
else
    sudo systemctl start $SERVICE_NAME
fi

echo "✅ Bot deployed!"
echo "📊 Check: sudo systemctl status $SERVICE_NAME"
