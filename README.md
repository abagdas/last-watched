# last_watched

Windows'ta bir klasor agacindaki video dosyalarini tarar ve en guncel
`LastAccessTime` degerine sahip dosya ya da dosyalari gosterir.

## Kurulum

Bu depo icindeyken:

```powershell
python -m pip install -e .
```

Arac bagimlilik gerektirmez. Kurulumdan sonra herhangi bir klasorden
calistirilabilir:

```powershell
last-watched "C:\Users\<username>\Desktop\P_S_M"
last-watched "C:\Users\<username>\Desktop\P_S_M\Shows"
```

Kurulum yapmadan, depo klasorundeyken de su sekilde calisir:

```powershell
python -m last_watched "C:\Users\<username>\Desktop\P_S_M"
```

## Davranis

- `.mkv`, `.mp4`, `.avi`, `.mov`, `.m4v`, `.wmv` ve `.webm` dosyalarini
  ozyinelemeli olarak tarar.
- Altyazi, afis ve diger video olmayan dosyalari yok sayar.
- Dosya icerigini acmadan yalnizca metadata okur; bu nedenle tarama erisim
  zamanini degistirmez.
- Birden cok dosyanin erisim zamani tamamen esitse hepsini listeler. Windows
  `LastAccessTime` bilgisini gecikmeli veya toplu guncelleyebildiginden gercek
  izleme sirasi bu durumda kesin olarak belirlenemez.
- Erisilemeyen alt klasorleri uyariyla atlar; gecersiz klasorler ve videosuz
  klasorler icin Turkce hata ve basarisiz cikis kodu verir.

## Testler

```powershell
python -m unittest discover -s tests -v
```
