# 🧠 SmartArrange Pro 2.0

**Dosyalarınızı tek tıkla analiz eder, kategorilere ayırır, düzenler.**

SmartArrange Pro 2.0, klasör karmaşasına son vermek isteyen kullanıcılar için tasarlanmış sade ve güçlü bir masaüstü uygulamasıdır. Hedef klasörünüzdeki tüm dosyaları analiz eder, türlerine göre gruplar ve düzenli bir yapıya kavuşturur.

---

## ⚡️ Hızlı Bakış

- 🔍 Dosya analiz ve kategori algılama
- 🗂️ Otomatik klasörleme (belgeler, medya, arşivler vb.)
- ✨ Modern ve kompakt kullanıcı arayüzü (Tkinter tabanlı)
- 📁 Alt klasör düzleştirme (flattening)
- 🧼 Gereksiz dosya temizliği
- 🧠 Akıllı yeniden adlandırma sistemi
- 🌗 Karanlık ve aydınlık tema desteği

---

## 🔧 Kurulum

### Sistem Gereksinimleri

- Python 3.8+
- `tkinter` (Python ile birlikte gelir)
- `Pillow` (`pip install pillow` ile kurulabilir)

### Başlatmak için:

```bash
git clone https://github.com/FreshYoshio/SmartArrangePro.git
cd SmartArrangePro
pip install -r requirements.txt
python SmartArrangePro.py
```

---

## 🖥️ Uygulama Özeti

| Modül               | Açıklama                                                                 |
|---------------------|--------------------------------------------------------------------------|
| 📂 Klasör Seçici     | Hedef klasörü seçerek düzenlemeye başlanır                              |
| 🔄 Dönüştürme Modülü | Alt klasörlerden dosya çıkarma ve yeniden yerleştirme işlemleri         |
| 🧠 Sınıflandırıcı    | Dosya türlerine göre kategorik ayırma ve taşıma                         |
| ⚙️ Ayarlar Menüsü    | Dosya boyutu filtreleme, özel uzantılar, tema ve daha fazlası           |
| 🧹 Temizlik Aracı    | Gereksiz ve geçici dosyaların hızlı silinmesi                           |

---

## ✨ Kullanıcı Deneyimi

- Başlangıç ekranı: sade, yönlendirici ve buton tabanlı
- Kategorilere göre ikonlar ve renkli etiketleme
- Gerçek zamanlı bilgi kutuları (kaç dosya, ne türde, ne kadar yer kazanıldı?)
- Hata mesajları ve onay kutuları ile kullanıcı dostu yaklaşım

---

## 📁 Kategori Desteği

SmartArrange Pro aşağıdaki kategorilere göre dosyaları gruplandırır:

```
📄 Belgeler: .pdf, .docx, .txt, .xlsx  
🎵 Müzik: .mp3, .wav  
🎞️ Video: .mp4, .avi, .mov  
🖼️ Görseller: .jpg, .png, .gif, .webp  
🗜️ Arşivler: .zip, .rar, .7z  
🧩 Yazılım: .py, .exe, .msi, .js  
📊 Veri: .csv, .json, .xml
```

---

## 💬 Sık Sorulanlar

**Q:** Uygulama hangi işletim sisteminde çalışır?  
**A:** Windows için optimize edilmiştir. Ancak Python kurulu olduğu sürece diğer platformlarda da çalışabilir.

**Q:** Dosyalarım silinir mi?  
**A:** Hayır. Uygulama sadece taşıma, yeniden adlandırma ve düzenleme işlemleri yapar. Her işlem kullanıcı onayına bağlıdır.

**Q:** Tema nasıl değiştirilir?  
**A:** Ayarlar panelinden açık veya koyu tema seçebilirsiniz.

---

## 🛠️ Geliştirici Notları

- Proje dili: Python
- Arayüz: Tkinter + Pillow
- Sürüm: 2.0 (Yeniden tasarlanmış UI + Gelişmiş özellikler)

---

## 📌 Yol Haritası

- [x] Dosya analizi ve sınıflandırma
- [x] Arayüz temaları
- [x] Sağ tık menüsü
- [ ] Klasörler arası eşitleme
- [ ] Sürükle bırak desteği
- [ ] Otomatik yedekleme sistemi

---

## 📄 Lisans

Bu proje MIT lisansı ile korunmaktadır.  
Detaylar için `LICENSE` dosyasını inceleyin.

---

## 🙋 Destek & İletişim

GitHub üzerinden [issue](https://github.com/FreshYoshio/SmartArrangePro/issues) açarak geri bildirimde bulunabilir ya da proje sayfasından katkı sunabilirsin.
