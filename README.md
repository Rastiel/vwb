# VWB – Varacron WhatsApp Bot

Meta WhatsApp Cloud API ile geliştirilmiş, Docker üzerinde çalışan, otomatik mesaj yanıtlayan bir webhook botudur.

## 🚀 Özellikler

- Flask tabanlı webhook sunucusu
- Meta WhatsApp Cloud API ile tam entegre
- Her gelen mesaja otomatik cevap verir
- Docker ile container ortamında çalışır
- `redeploy.sh` ile tek komutla güncellenebilir
- `docker-compose` desteği ile kolay yönetim
- Log klasörü host sistemine bağlanabilir

## 🛠️ Kurulum

### 1. GitHub'dan projeyi klonla
```bash
git clone https://github.com/Rastiel/vwb.git
cd vwb
