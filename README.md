# last_watched

Windows'ta bir klasör ağacındaki video dosyalarını tarar ve en güncel
`LastAccessTime` değerine sahip dosya ya da dosyaları gösterir.

## Kurulum

Bu depo içindeyken:

```powershell
python -m pip install -e .
```

Araç bağımlılık gerektirmez. Kurulumdan sonra herhangi bir klasörden
çalıştırılabilir:

```powershell
last-watched "C:\Users\<username>\Desktop\P_S_M"
last-watched "C:\Users\<username>\Desktop\P_S_M\Shows"
```

Kurulum yapmadan, depo klasöründeyken de şu şekilde çalışır:

```powershell
python -m last_watched "C:\Users\<username>\Desktop\P_S_M"
```

## Davranış

- `.mkv`, `.mp4`, `.avi`, `.mov`, `.m4v`, `.wmv` ve `.webm` dosyalarını
  özyinelemeli olarak tarar.
- Altyazı, afiş ve diğer video olmayan dosyaları yok sayar.
- Dosya içeriğini açmadan yalnızca metadata okur; bu nedenle tarama erişim
  zamanını değiştirmez.
- Birden çok dosyanın erişim zamanı tamamen eşitse hepsini listeler. Windows
  `LastAccessTime` bilgisini gecikmeli veya toplu güncelleyebildiğinden gerçek
  izleme sırası bu durumda kesin olarak belirlenemez.
- Erişilemeyen alt klasörleri uyarıyla atlar; geçersiz klasörler ve videosuz
  klasörler için Türkçe hata ve başarısız çıkış kodu verir.

## Testler

```powershell
python -m unittest discover -s tests -v
```
