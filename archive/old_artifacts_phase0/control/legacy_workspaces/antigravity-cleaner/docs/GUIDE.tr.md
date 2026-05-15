# Antigravity Kullanım Kılavuzu

## 📚 Tam Modül Rehberi

### 📂 Profil Yedekleme ve Geri Yükleme (Session Manager)
Antigravity'nin çekirdek modülü, tarayıcı kimliklerinizi yönetmenizi sağlar.

#### Nasıl Yedek Alınır?
1. Ana menüden **[2]** (Session Manager) seçeneğini seçin.
2. **[1]** (Backup Browser Profile) seçeneğine tıklayın.
3. Listeden bir profil seçin. Araç, Chrome, Edge ve diğer tarayıcı profillerini ve bağlı e-postaları otomatik olarak algılar.
4. Yedekleme Modunu Seçin:
    *   **[1] Light Mode:** Sadece temel verileri yedekler (Çerezler, Giriş Bilgileri). Hız: Anlık. Boyut: ~20MB. Hızlı geçişler için ideal.
    *   **[2] Full Mode:** Her şeyi yedekler (Uzantılar, Geçmiş, Önbellek vb.). Hız: Yavaş. Boyut: 500MB+. Tam taşıma için ideal.

#### Nasıl Geri Yüklenir?
1. Session Manager içinde **[3]** (Restore Profile) seçeneğini seçin.
2. Listeden bir yedek seçin.
3. Program tarayıcıyı otomatik olarak kapatır ve dosyaları enjekte eder.
    *   *Uyarı:* Geri yükleme işlemi, o profilin mevcut verilerinin üzerine yazar.

---

### 🌍 Google Bölge Değişikliği (Region Inspector)
Google Play / YouTube Premium bölgenizi kontrol etmenize ve değiştirmenize yardımcı olur.

**Adımlar:**
1. Ana menüden **[5]** (Region Inspector) seçeneğini seçin.
2. **KRİTİK:** Önce **Pre-Check** (Ön Kontrol) yapın. Bu, şunları kontrol etmek için bir site açar:
    *   **IP Sızıntısı:** Gerçek IP adresiniz görünüyor mu?
    *   **DNS Sızıntısı:** İSS DNS'ini mi kullanıyorsunuz?
    *   **WebRTC:** Yerel IP adresiniz ifşa oluyor mu?
3. Güvenli olduğundan eminseniz, gizli Google `Country Association` sayfasını açmak için bir profil seçin.

---

### 🚀 Ağ Optimize Edici (Network Optimizer)
Genellikle sansür veya bozuk proxy ayarlarından kaynaklanan bağlantı sorunlarını giderir.

*   **Flush DNS:** Bozuk DNS önbelleğini temizler.
*   **Reset Winsock:** Windows soket kataloğunuzu sıfırlar.
*   **Reset TCP/IP:** TCP/IP protokol yığınını yeniden yükler.
*   *Not:* Yönetici (Administrator) yetkileri gerektirir.

---

### 🧹 Sistem Temizleyici (System Cleaner)
Hesapları birbirine bağlayabilecek veya konum geçmişinizi ifşa edebilecek izleri temizler.
*   **Temp Dosyaları:** Standart Windows geçici dosyaları.
*   **IDE Önbelleği:** Genellikle büyük miktarda meta veri depolayan JetBrains/VSCode önbelleklerini temizler.
