import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5 import uic 


current_dir = os.path.dirname(os.path.abspath(__file__)) 
base_dir = os.path.dirname(current_dir) 
ui_path = os.path.join(base_dir, 'ui', 'login.ui') 


db_path = os.path.join(base_dir, 'database', 'lost_found.db') 

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"HATA: UI dosyası bulunamadı! Yol: {ui_path}")

        self.btngiris.clicked.connect(self.giris_yap)
        self.btnuye_ol.clicked.connect(self.uye_ol)

        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect_db()

    def connect_db(self):
        try:
            # Veritabanı bağlantısı
            self.conn = sqlite3.connect(self.db_path, timeout=5)
            self.cursor = self.conn.cursor()
            print(f"Bağlantı başarılı: {self.db_path}")
            self.create_table_if_not_exists()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Bağlanılamadı: {e}")
            sys.exit(1)

    def create_table_if_not_exists(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS kullanicilar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Tablo oluşturma hatası: {e}")

    def giris_yap(self):
        kullanici_adi = self.lekullanici_adi.text().strip().lower()
        sifre = self.lesifre.text()

        if not kullanici_adi or not sifre:
            QMessageBox.warning(self, "Uyarı", "Lütfen kullanıcı adı ve şifre girin.")
            return

        try:
            self.cursor.execute("SELECT * FROM kullanicilar WHERE username=? AND password=?", (kullanici_adi, sifre))
            user = self.cursor.fetchone()
            if user:
                QMessageBox.information(self, "Başarılı", f"Hoşgeldiniz {user[3]}!")
                try:
                    from panel import PanelDialog 
                    self.hide()
                    self.panel_window = PanelDialog(user_name=user[3])
                    self.panel_window.show()
                except ImportError:
                    print("Hata: panel.py dosyası src içinde bulunamadı!")
            else:
                QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış.")
        except sqlite3.Error as e:
            print(f"Sorgu hatası: {e}")

    def uye_ol(self):
        kullanici_adi = self.lekulladiuye.text().strip().lower()
        email = self.leposta.text().strip().lower()
        sifre = self.lesifre_2.text()
        sifre_tekrar = self.lesifre_tekrar.text()
        isim = kullanici_adi

        if not kullanici_adi or not email or not sifre or not sifre_tekrar:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
            return

        if sifre != sifre_tekrar:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor.")
            return

        try:
            self.cursor.execute("INSERT INTO kullanicilar (username, email, password, name) VALUES (?, ?, ?, ?)",
                                 (kullanici_adi, email, sifre, isim))
            self.conn.commit()
            QMessageBox.information(self, "Başarılı", "Kayıt başarılı!")
            
            self.lekulladiuye.clear()
            self.leposta.clear()
            self.lesifre_2.clear()
            self.lesifre_tekrar.clear()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Bu kullanıcı adı veya e-posta zaten kullanımda olabilir.\nDetay: {e}")

    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = LoginDialog()
    pencere.show()
    sys.exit(app.exec_())