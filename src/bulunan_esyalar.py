import sys
import os
import sqlite3
from PyQt5 import QtWidgets, QtGui, uic


current_dir = os.path.dirname(os.path.abspath(__file__)) 
base_dir = os.path.dirname(current_dir) 
ui_path = os.path.join(base_dir, 'ui', 'bulunan_esyalar.ui') 
db_path = os.path.join(base_dir, 'database', 'lost_found.db')

class BulunanEsyalar(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        
        
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"HATA: Bulunan Esyalar UI dosyası bulunamadı! Yol: {ui_path}\n{e}")

        self.veritabani_baglantisi()
        self.bulunanlara_aktar()
        self.verileri_getir()

        
        self.lineEditArama.textChanged.connect(self.ara)
        self.tableWidgetBulunanEsyalar.itemSelectionChanged.connect(self.detay_goster)

    
        self.tableWidgetBulunanEsyalar.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.tableWidgetBulunanEsyalar.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.tableWidgetBulunanEsyalar.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def veritabani_baglantisi(self):
        
        self.baglanti = sqlite3.connect(db_path)
        self.cursor = self.baglanti.cursor()

    def verileri_getir(self, filtre=""):
        
        sorgu = """
            SELECT id, esya_adi, aciklama, kayip_yer, kayip_tarih, durum, telefon, email
            FROM kayip_esyalar
            WHERE LOWER(durum) = 'bulundu'
        """
        if filtre:
            sorgu += " AND LOWER(esya_adi) LIKE ?"
            self.cursor.execute(sorgu, (f'%{filtre.lower()}%',))
        else:
            self.cursor.execute(sorgu)
            
        veriler = self.cursor.fetchall()
        self.tableWidgetBulunanEsyalar.setRowCount(0)

        for satir_index, satir in enumerate(veriler):
            self.tableWidgetBulunanEsyalar.insertRow(satir_index)
            for sutun_index, veri in enumerate(satir):
                item = QtWidgets.QTableWidgetItem(str(veri))
                self.tableWidgetBulunanEsyalar.setItem(satir_index, sutun_index, item)

        if veriler:
            self.tableWidgetBulunanEsyalar.selectRow(0)
            self.detay_goster()

    def detay_goster(self):
        secili_satir = self.tableWidgetBulunanEsyalar.currentRow()
        if secili_satir == -1:
            return

        try:
            esya_id = self.tableWidgetBulunanEsyalar.item(secili_satir, 0).text()
            esya_adi = self.tableWidgetBulunanEsyalar.item(secili_satir, 1).text()
            aciklama = self.tableWidgetBulunanEsyalar.item(secili_satir, 2).text()
            yer = self.tableWidgetBulunanEsyalar.item(secili_satir, 3).text()
            tarih = self.tableWidgetBulunanEsyalar.item(secili_satir, 4).text()
            telefon = self.tableWidgetBulunanEsyalar.item(secili_satir, 6).text()
            email = self.tableWidgetBulunanEsyalar.item(secili_satir, 7).text()
        except AttributeError:
            return

        detay = f"""📦 Eşya Adı: {esya_adi}
📝 Açıklama: {aciklama}
📍 Bulunduğu Yer: {yer}
📅 Tarih: {tarih}
📞 Telefon: {telefon}
✉️ Email: {email}"""

        self.textBrowser_bulunan.setPlainText(detay)

    
        self.cursor.execute("SELECT foto FROM kayip_esyalar WHERE id = ?", (esya_id,))
        sonuc = self.cursor.fetchone()
        if sonuc and sonuc[0] and os.path.exists(sonuc[0]):
            self.labelFoto.setPixmap(QtGui.QPixmap(sonuc[0]).scaled(150, 150, aspectRatioMode=1))
        else:
            self.labelFoto.clear()
            self.labelFoto.setText("Fotoğraf Yok")

    def ara(self):
        kelime = self.lineEditArama.text()
        self.verileri_getir(kelime)

    def bulunanlara_aktar(self):
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bulunan_esyalar (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                esya_adi TEXT,
                aciklama TEXT,
                bulunma_tarihi TEXT,
                bulunan_yer TEXT,
                telefon TEXT,
                email TEXT,
                foto TEXT
            )
        """)
        
        self.cursor.execute("""
            SELECT id, user_id, esya_adi, aciklama, kayip_tarih, kayip_yer,
                   telefon, email, foto
            FROM kayip_esyalar
            WHERE LOWER(durum) = 'bulundu'
              AND id NOT IN (SELECT id FROM bulunan_esyalar)
        """)
        bulunanlar = self.cursor.fetchall()

        for kayit in bulunanlar:
            self.cursor.execute("""
                INSERT INTO bulunan_esyalar (
                    id, user_id, esya_adi, aciklama, bulunma_tarihi,
                    bulunan_yer, telefon, email, foto
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, kayit)

        self.baglanti.commit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pencere = BulunanEsyalar()
    pencere.show()
    sys.exit(app.exec_())