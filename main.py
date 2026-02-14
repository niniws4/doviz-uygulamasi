import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time

class DovizUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Finans Dashboard v2.0")
        self.root.geometry("400x700")
        self.root.configure(bg="#121212")

        self.tum_kurlar = {}
        self.kur_isimleri = {}
        self.is_loading = False

        self.arayuz_kur_ayarla()
        
        self.verileri_baslat_thread()
        self.otomatik_guncelle_dongusu()

    def arayuz_kur_ayarla(self):
        header = tk.Frame(self.root, bg="#1e1e1e", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="GLOBAL PİYASA", font=("Segoe UI", 16, "bold"), fg="#00ff88", bg="#1e1e1e").pack()
        
        self.status_label = tk.Label(self.root, text="Veriler güncel", font=("Segoe UI", 8), fg="#555555", bg="#121212")
        self.status_label.pack(pady=2)

        self.sabit_frame = tk.Frame(self.root, bg="#121212")
        self.sabit_frame.pack(pady=10, fill="x")

        self.lbl_usd = self.kart_olustur(self.sabit_frame, "USD / TRY", "#4da6ff")
        self.lbl_eur = self.kart_olustur(self.sabit_frame, "EUR / TRY", "#ff4d4d")
        self.lbl_altin = self.kart_olustur(self.sabit_frame, "GRAM ALTIN (XAU)", "#ffcc00")

        search_frame = tk.Frame(self.root, bg="#121212", pady=10)
        search_frame.pack(fill="x", padx=25)
        
        tk.Label(search_frame, text="Para Birimi Ara:", fg="#aaaaaa", bg="#121212", font=("Segoe UI", 10)).pack(anchor="w")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.arama_yap)
        self.entry_arama = tk.Entry(search_frame, textvariable=self.search_var, bg="#2a2a2a", fg="white", 
                                    insertbackground="white", borderwidth=0, font=("Segoe UI", 12))
        self.entry_arama.pack(fill="x", ipady=8, pady=5)

        self.listbox = tk.Listbox(self.root, bg="#2a2a2a", fg="white", borderwidth=0, 
                                  highlightthickness=0, font=("Segoe UI", 10), height=5)
        self.listbox.pack(padx=25, fill="x")
        self.listbox.bind("<<ListboxSelect>>", self.kur_secildi)

        self.ozel_kur_frame = tk.Frame(self.root, bg="#121212")
        self.ozel_kur_frame.pack(pady=20, fill="x")
        self.lbl_ozel_deger = self.kart_olustur(self.ozel_kur_frame, "SEÇİLEN KUR", "#a29bfe")

    def kart_olustur(self, parent, baslik, renk):
        f = tk.Frame(parent, bg="#1e1e1e", pady=12)
        f.pack(pady=6, padx=25, fill="x")
        tk.Label(f, text=baslik, font=("Segoe UI", 9, "bold"), fg="#888888", bg="#1e1e1e").pack()
        lbl = tk.Label(f, text="Yükleniyor...", font=("Consolas", 20, "bold"), fg=renk, bg="#1e1e1e")
        lbl.pack()
        return lbl

    def verileri_baslat_thread(self):
        thread = threading.Thread(target=self.api_verilerini_cek, daemon=True)
        thread.start()

    def api_verilerini_cek(self):
        if self.is_loading: return
        self.is_loading = True
        self.status_label.config(text="Güncelleniyor...", fg="#ffcc00")

        try:
            if not self.kur_isimleri:
                isimler_url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json"
                self.kur_isimleri = requests.get(isimler_url, timeout=10).json()

            url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/try.json"
            response = requests.get(url, timeout=10)
            data = response.json()
            self.tum_kurlar = data['try']

            self.root.after(0, self.arayuz_verilerini_yansit)

        except requests.exceptions.RequestException as e:
            print(f"Hata oluştu: {e}")
            self.root.after(0, lambda: self.status_label.config(text="Bağlantı Hatası!", fg="#ff4d4d"))
        finally:
            self.is_loading = False

    def arayuz_verilerini_yansit(self):
        try:
            usd_tl = 1 / self.tum_kurlar['usd']
            eur_tl = 1 / self.tum_kurlar['eur']
            altin_gram = (1 / self.tum_kurlar['xau']) / 31.1035

            self.lbl_usd.config(text=f"₺{usd_tl:.2f}")
            self.lbl_eur.config(text=f"₺{eur_tl:.2f}")
            self.lbl_altin.config(text=f"₺{altin_gram:.2f}")
            
            self.status_label.config(text=f"Son Güncelleme: {time.strftime('%H:%M:%S')}", fg="#555555")
        except Exception as e:
            print(f"Yansıtma hatası: {e}")

    def arama_yap(self, *args):
        ara = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        
        if len(ara) < 1: return

        sonuclar = [f"{kod.upper()} - {isim}" for kod, isim in self.kur_isimleri.items() 
                    if ara in kod or ara in isim.lower()]
        
        for s in sonuclar[:15]:
            self.listbox.insert(tk.END, s)

    def kur_secildi(self, event):
        if not self.listbox.curselection(): return
        
        try:
            secim = self.listbox.get(self.listbox.curselection())
            kod = secim.split(" - ")[0].lower()
            isim = secim.split(" - ")[1]
            
            fiyat = 1 / self.tum_kurlar[kod]
            
            self.lbl_ozel_deger.master.winfo_children()[0].config(text=f"{kod.upper()} ({isim})")
            self.lbl_ozel_deger.config(text=f"₺{fiyat:.4f}")
            
            self.search_var.set("")
            self.listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Hata", "Kur verisi hesaplanamadı.")

    def otomatik_guncelle_dongusu(self):
        self.verileri_baslat_thread()
        self.root.after(60000, self.otomatik_guncelle_dongusu)

if __name__ == "__main__":
    root = tk.Tk()
    app = DovizUygulamasi(root)
    root.mainloop()