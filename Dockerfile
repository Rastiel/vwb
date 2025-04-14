# Hafif Python imajı
FROM python:3.11-slim

# Uygulama klasörüne geç
WORKDIR /app

# Gerekli dosyaları kopyala
COPY . .

# Gereken Python kütüphanelerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Ortam portunu tanımla
ENV PORT=10000

# Container başladığında çalışacak komut
CMD ["python", "app.py"]
