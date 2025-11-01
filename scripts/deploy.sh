#!/bin/bash
set -e  # Выход при ошибке

APP_DIR="/opt/nutrition-bot"
SERVICE_NAME="nutrition-bot"

echo "🚀 Starting deployment..."

# Создаем директории если их нет
echo "📁 Creating directories..."
sudo mkdir -p $APP_DIR/{bot,data,logs}
sudo chown -R nutrition-bot:nutrition-bot $APP_DIR

# Копируем код из текущей директории (уже обновленной через git pull)
echo "📝 Copying bot files..."
sudo -u nutrition-bot cp -r $APP_DIR/bot/* $APP_DIR/bot/ 2>/dev/null || true

# Устанавливаем зависимости
echo "📦 Installing dependencies..."
cd $APP_DIR
sudo -u nutrition-bot python3 -m pip install -r requirements.txt

# Настраиваем systemd service
echo "⚙️ Setting up service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Nutrition Bot
After=network.target

[Service]
Type=simple
User=nutrition-bot
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

# Перезапускаем сервис
echo "🔄 Restarting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "🔄 Restarting running service..."
    sudo systemctl restart $SERVICE_NAME
else
    echo "▶️ Starting service..."
    sudo systemctl start $SERVICE_NAME
fi

# Проверяем статус
echo "📊 Checking status..."
sleep 5
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "🎉 Bot deployed successfully!"
    echo "📋 Check status: sudo systemctl status $SERVICE_NAME"
    echo "📝 Check logs: sudo journalctl -u $SERVICE_NAME -f"
else
    echo "❌ Deployment failed!"
    echo "🔍 Checking service status:"
    sudo systemctl status $SERVICE_NAME
    echo "📋 Recent logs:"
    sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi