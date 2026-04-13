import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from PyQt5 import uic  


current_dir = os.path.dirname(os.path.abspath(__file__)) 
base_dir = os.path.dirname(current_dir) 
ui_path = os.path.join(base_dir, 'ui', 'kayip_bildir.ui') 
db_path = os.path.join(base_dir, 'database', 'lost_found.db') 

class KayipBildirDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"HATA: UI dosyası bulunamadı! Yol: {ui_path}\n{e}")

        self.secilen_dosya_yolu = None

                
        self.pushButton.clicked.connect(self.resim_sec)      
        self.button_bildir.clicked.connect(self.bildir)      

    def resim_sec(self):
        dosya_adi, _ = QFileDialog.getOpenFileName(
            self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)"
        )
        if dosya_adi:
            self.secilen_dosya_yolu = dosya_adi
            self.label_resim_path.setText(dosya_adi)
        else:
            self.label_resim_path.setText("Henüz dosya seçilmedi.")

    def bildir(self):
        
        esya_adi = self.lineEdit_esya_adi.text().strip()
        kayip_yer = self.lineEdit_yer.text().strip()
        aciklama = self.textEdit_aciklama.toPlainText().strip()
        kayip_tarih = self.dateEdit_tarih.date().toString("yyyy-MM-dd")
        foto = self.secilen_dosya_yolu if self.secilen_dosya_yolu else ""

        eksik_alanlar = []
        if len(esya_adi) == 0:
            eksik_alanlar.append("eşya adı")
        if len(kayip_yer) == 0:
            eksik_alanlar.append("kaybolduğu yer")

        if eksik_alanlar:
            mesaj = f"Lütfen { ' ve '.join(eksik_alanlar) } doldurun."
            QMessageBox.warning(self, "Eksik Bilgi", mesaj)
            return

        
        user_id = 1
        durum = "Kayıp"
        telefon = "05001234567"
        email = "ornek@mail.com"

        basarili = self.kaydet_veritabani(
            user_id, esya_adi, aciklama, kayip_tarih, kayip_yer, foto, durum, telefon, email
        )

        if basarili:
            QMessageBox.information(self, "Kayıt Başarılı", "Kayıp eşya bildiriminiz kaydedildi.")
            self.temizle_form()
        else:
            QMessageBox.critical(self, "Hata", "Veritabanına kayıt yapılamadı!")

    def kaydet_veritabani(self, user_id, esya_adi, aciklama, kayip_tarih, kayip_yer, foto, durum, telefon, email):
        try:
            
            conn = sqlite3.connect(db_path)  
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kayip_esyalar (     
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    esya_adi TEXT,
                    aciklama TEXT,
                    kayip_tarih TEXT,
                    kayip_yer TEXT,
                    foto TEXT,
                    durum TEXT,
                    telefon TEXT,
                    email TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO kayip_esyalar (
                    user_id, esya_adi, aciklama, kayip_tarih, kayip_yer, foto, durum, telefon, email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, esya_adi, aciklama, kayip_tarih, kayip_yer, foto, durum, telefon, email))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("Veritabanı Hatası:", e)
            return False

    def temizle_form(self):
        self.lineEdit_esya_adi.clear()
        self.textEdit_aciklama.clear()
        self.lineEdit_yer.clear()
        self.label_resim_path.setText("Henüz dosya seçilmedi.")
        self.secilen_dosya_yolu = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = KayipBildirDialog()
    pencere.setWindowTitle("Kayıp Eşya Bildirimi")
    pencere.show()
    sys.exit(app.exec_())