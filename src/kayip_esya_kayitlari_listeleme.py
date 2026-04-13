import sys
import os
import sqlite3
from PyQt5 import QtWidgets, uic


current_dir = os.path.dirname(os.path.abspath(__file__)) # src
base_dir = os.path.dirname(current_dir) # Ana dizin
ui_path = os.path.join(base_dir, 'ui', 'kayip_esya_kayitlari_listeleme.ui')
db_path = os.path.join(base_dir, 'database', 'lost_found.db')

class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        
        
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"HATA: Liste UI dosyası bulunamadı! Yol: {ui_path}\n{e}")

        self.baglanti_olustur()
        self.tabloyu_doldur()

        
        self.tableWidget_tablo.itemSelectionChanged.connect(self.detaylari_goster)
        self.pushButton_guncelle.clicked.connect(self.guncelle)
        self.pushButton_sil.clicked.connect(self.sil)
        self.pushButtonAra.clicked.connect(self.ara)
        self.lineEditArama.returnPressed.connect(self.ara)

    def baglanti_olustur(self):
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def tabloyu_doldur(self):
        self.tableWidget_tablo.setRowCount(0)
        self.cursor.execute("""
            SELECT id, telefon, email, esya_adi, aciklama, kayip_yer, kayip_tarih, durum, foto
            FROM kayip_esyalar
        """)
        for row_index, row_data in enumerate(self.cursor.fetchall()):
            self.tableWidget_tablo.insertRow(row_index)
            for column_index, cell_data in enumerate(row_data):
                self.tableWidget_tablo.setItem(
                    row_index, column_index, QtWidgets.QTableWidgetItem(str(cell_data))
                )

    def detaylari_goster(self):
        selected_items = self.tableWidget_tablo.selectedItems()
        if not selected_items:
            return

        self.secilen_id = int(selected_items[0].text())

        
        self.lineEdit_telefon.setText(selected_items[1].text())
        self.lineEdit_email.setText(selected_items[2].text())
        self.lineEdit_aciklama.setText(selected_items[4].text())
        self.comboBox_sec.setCurrentText(selected_items[7].text())

        detay_text = f"""\
Id: {selected_items[0].text()}
Telefon: {selected_items[1].text()}
Email: {selected_items[2].text()}
Eşya Adı: {selected_items[3].text()}
Açıklama: {selected_items[4].text()}
Kayıp Yer: {selected_items[5].text()}
Kayıp Tarih: {selected_items[6].text()}
Durum: {selected_items[7].text()}
Fotoğraf: {selected_items[8].text()}
"""
        self.textBrowser_detay.setText(detay_text.strip())

    def guncelle(self):
        if not hasattr(self, 'secilen_id'):
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen güncellenecek bir satır seçin.")
            return

        yeni_telefon = self.lineEdit_telefon.text()
        yeni_email = self.lineEdit_email.text()
        yeni_aciklama = self.lineEdit_aciklama.text()
        yeni_durum = self.comboBox_sec.currentText()

        self.cursor.execute("""
            UPDATE kayip_esyalar
            SET telefon=?, email=?, aciklama=?, durum=?
            WHERE id=?
        """, (yeni_telefon, yeni_email, yeni_aciklama, yeni_durum, self.secilen_id))
        self.conn.commit()
        self.tabloyu_doldur()
        QtWidgets.QMessageBox.information(self, "Başarılı", "Kayıt güncellendi.")

    def sil(self):
        if not hasattr(self, 'secilen_id'):
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen silinecek bir satır seçin.")
            return

        self.cursor.execute("DELETE FROM kayip_esyalar WHERE id=?", (self.secilen_id,))
        self.conn.commit()
        self.tabloyu_doldur()
        
        
        self.textBrowser_detay.clear()
        self.lineEdit_telefon.clear()
        self.lineEdit_email.clear()
        self.lineEdit_aciklama.clear()
        self.comboBox_sec.setCurrentIndex(0)
        QtWidgets.QMessageBox.information(self, "Başarılı", "Kayıt silindi.")

    def ara(self):
        aranan = self.lineEditArama.text().strip()
        self.tableWidget_tablo.setRowCount(0)

        self.cursor.execute("""
            SELECT id, telefon, email, esya_adi, aciklama, kayip_yer, kayip_tarih, durum, foto
            FROM kayip_esyalar
            WHERE esya_adi LIKE ? 
        """, (f'%{aranan}%',))

        for row_index, row_data in enumerate(self.cursor.fetchall()):
            self.tableWidget_tablo.insertRow(row_index)
            for column_index, cell_data in enumerate(row_data):
                self.tableWidget_tablo.setItem(
                    row_index, column_index, QtWidgets.QTableWidgetItem(str(cell_data))
                )

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pencere = MainWindow()
    pencere.show()
    sys.exit(app.exec_())