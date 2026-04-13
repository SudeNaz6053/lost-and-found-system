import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5 import uic  


current_dir = os.path.dirname(os.path.abspath(__file__)) 
base_dir = os.path.dirname(current_dir) 
ui_path = os.path.join(base_dir, 'ui', 'panel.ui')


try:
    from kayip_bildir import KayipBildirDialog
    from kayip_esya_kayitlari_listeleme import MainWindow as KayipEsyaKayitlariDialog
    from bulunan_esyalar import BulunanEsyalar
except ImportError as e:
    print(f"Hata: Bazı modüller yüklenemedi, dosyaların src içinde olduğundan emin ol: {e}")

class PanelDialog(QDialog):
    def __init__(self, user_name="Kullanıcı", parent=None):
        super().__init__(parent)
        
        
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"HATA: Panel UI dosyası bulunamadı! Yol: {ui_path}\n{e}")

        self.setWindowTitle("Kayıp Eşya Takip Paneli")
        
        
        self.hosgeldinizlabel.setText(f"HOŞ GELDİNİZ, {user_name.upper()}!")

        
        self.btnkypesya.clicked.connect(self.open_kayip_esya_bildir)
        self.btnkyp.clicked.connect(self.open_kayip_kayitlari)
        self.btnbulesya.clicked.connect(self.open_bulunan_esyalar)
        self.cksbtn.clicked.connect(self.cikis_yap)

    def open_kayip_esya_bildir(self):
        self.hide()
        dialog = KayipBildirDialog()
        dialog.exec_()
        self.show()

    def open_kayip_kayitlari(self):
        self.hide()
        dialog = KayipEsyaKayitlariDialog()
        dialog.exec_()
        self.show()

    def open_bulunan_esyalar(self):
        self.hide()
        dialog = BulunanEsyalar()
        dialog.exec_()
        self.show()

    def cikis_yap(self):
        reply = QMessageBox.question(
            self,
            "Çıkış Onayı",
            "Uygulamadan çıkmak istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
            QApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel_window = PanelDialog(user_name="Misafir")
    panel_window.show()
    sys.exit(app.exec_())