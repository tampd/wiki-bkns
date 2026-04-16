#!/bin/bash
# BKNS Wiki Portal — Deployment Script
# Run with: sudo bash deploy-nginx.sh
set -euo pipefail

DOMAIN="wiki.bkns.vn"
CONF_SRC="/wiki/web/nginx-wiki.bkns.vn.conf"
CONF_DST="/etc/nginx/sites-available/${DOMAIN}"
CONF_LINK="/etc/nginx/sites-enabled/${DOMAIN}"
EMAIL="duytam@bkns.vn"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " BKNS Wiki Portal — Deploy Nginx"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Get SSL cert first (with HTTP-only temp config)
echo ""
echo "📋 Step 1: Obtaining SSL certificate..."

# Create temp HTTP-only config for certbot
cat > /tmp/upload-http.conf << 'HTTPEOF'
server {
    listen 80;
    listen [::]:80;
    server_name wiki.bkns.vn;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
HTTPEOF

cp /tmp/upload-http.conf "$CONF_DST"
ln -sf "$CONF_DST" "$CONF_LINK"
nginx -t && systemctl reload nginx

# Get cert
if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  certbot certonly --webroot -w /var/www/html -d "$DOMAIN" \
    --non-interactive --agree-tos --email "$EMAIL" \
    --cert-name "$DOMAIN"
  echo "✅ SSL certificate obtained"
else
  echo "✅ SSL certificate already exists"
fi

# Step 2: Deploy full SSL config
echo ""
echo "📋 Step 2: Deploying SSL Nginx config..."
cp "$CONF_SRC" "$CONF_DST"

# Test and reload
if nginx -t; then
  systemctl reload nginx
  echo "✅ Nginx reloaded with SSL config"
else
  echo "❌ Nginx config test failed!"
  exit 1
fi

# Step 3: Setup auto-renewal cron
echo ""
echo "📋 Step 3: Checking certbot auto-renewal timer..."
if systemctl is-enabled certbot.timer &>/dev/null; then
  echo "✅ Certbot auto-renewal is enabled"
else
  systemctl enable certbot.timer
  systemctl start certbot.timer
  echo "✅ Certbot auto-renewal enabled"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✅ Deploy complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🌐 https://${DOMAIN}"
echo " 🔐 SSL: Let's Encrypt"
echo " 📡 Backend: http://127.0.0.1:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
