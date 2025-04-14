#!/bin/bash

echo "🔄 Kodlar GitHub'dan çekiliyor..."
git pull origin main || { echo "❌ Git pull başarısız"; exit 1; }

echo "⚙️ Ortam dosyası hazırlanıyor..."
cp .env.example .env || { echo "❌ .env dosyası kopyalanamadı"; exit 1; }

echo "🐳 Docker imajı oluşturuluyor (cache'siz)..."
docker build --no-cache -t vwb . || { echo "❌ Docker build başarısız"; exit 1; }

echo "🛑 Eski container durduruluyor (varsa)..."
docker stop vwb || true

echo "🗑️ Eski container siliniyor (varsa)..."
docker rm vwb || true

echo "🚀 Yeni container başlatılıyor..."
docker run -d -p 10000:10000 -v ./log:/app/log --env-file .env --name vwb vwb || { echo "❌ Docker run başarısız"; exit 1; }

echo "✅ Başarıyla güncellendi ve çalışıyor!"
