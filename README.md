# BiztProtHW2
Biztonsági Protokollok 2. házi feladat

## Eltérések a design dokumentumhoz képest
+ 1 új byte a headerben - a kliens címe a szimulált networkben (elég ez, a szerver mindig a Z címen van)
+ Handshake üzeneteknél nincs szükség MAC ellenőrzésre, ha sérült az üzenet, a random string kódolás és dekódolás után nem lesz ugyanaz, így tudjuk, hogy nem sikerült.
