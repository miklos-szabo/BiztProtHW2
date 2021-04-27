# BiztProtHW2
Biztonsági Protokollok 2. házi feladat

## Eltérések a design dokumentumhoz képest
+ 1 új byte a headerben - a kliens címe a szimulált networkben (elég ez, a szerver mindig a Z címen van)
+ Handshake üzeneteknél nincs szükség MAC ellenőrzésre, ha sérült az üzenet, a random string kódolás és dekódolás után nem lesz ugyanaz, így tudjuk, hogy nem sikerült.
+ Kliens publikus kulcsa átküldve 4 üzenetbe fér bele 2 helyett

##### Egyéb módosítások
+ Netsim-ben késleltetéshez alap time.sleep helyett eventlet.sleep, hogy működjön a saját, eventlet-es timeout-tal

## Szükséges könyvtárak:
+ pycryptodome
+ eventlet

```
pip install -r requirements.txt
```

##Használat
Fő mappából beírva: (netsim/files mappa meglétét feltételezve) <br/>
Windows operációs rendszer szükséges, feltételezzük, hogy a könyvtárak telepítve vannak
+ Network: py -m netsim.network -p "netsim/files" -a "AZ" --clean
+ Szerver: py -m server.server
+ Kliens: py -m client.client -a A
