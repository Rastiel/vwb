#!/bin/bash

echo "🔄 Kodlar GitHub'dan çekiliyor..."
git pull origin main || { echo "❌ Git pull başarısız"; exit 1; }

echo "⚙️ Ortam dosyası hazırlanıyor..."
cp .env.example .env || { echo "❌ .env dosyası kopyalanamadı"; exit 1; }

echo "🧨 Önceki Compose ortamı kapatılıyor (varsa)..."
docker compose down || true

echo "🔄 Yeni imaj build ediliyor ve container ayağa kaldırılıyor..."
docker compose up -d --build || { echo "❌ Compose başlatılamadı"; exit 1; }

echo "✅ Başarıyla güncellendi ve çalışıyor!"
