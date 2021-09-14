# Bachelor_opc_ua
Dieses repository enthält die Python-Module zur geschriebenen Bachelorarbeit an der Technischen Hochschule Georg Agricola in Bochum mit dem Thema "Fernzugriff auf Sensoren und Aktoren des Raspberry Pi eines Kokerei-Miniaturmodells über OPC UA".


# Verwendete Hardware
1. Selbst modelliertes und 3D-gedrucktes Kokerei-Modell
2. Raspberry Pi Model 4 B
3. Expander Board [RB-Explorer700](https://joy-it.net/de/products/RB-Explorer700)
4. LED-Lichtstreifen WS2812B
5. Drehpotentiometer B10K
6. [Windradmodellbausatz](https://www.sol-expert-group.de/Solar-Produkte/Windanlagenmodelle/Solar-Modelle/Windanlagenmodell-SOL-WIND-Bausatz::857.html?MODsid=b7su72u36u9i4lmapqquudkst7) mit DC-Motor und Solarzelle 
7. L298N Motortreiberboard mit integrierter Schutzbeschaltung [MotoDriver2](https://joy-it.net/de/products/SBC-Motodriver2)


# Beschaltung
Nachfolgend ist die Beschaltung für dieses Projekt gezeigt. Zu beachten ist, dass der A/D-Wandler über den I2C Bus an der Adresse 0x48 angeschlossen ist.<br><br>
![Gesamtschaltung](https://user-images.githubusercontent.com/81588173/133212266-e198e94a-7edf-4d12-9953-ee7393504849.jpg)


# Starten des Programms und Server
1. Auf Zeile 99 in opcua_srv.py IP-Adresse eingeben
2. Wenn nötig Zeilen 21 bis 24 in Main.py umkonfigurieren
3. Bauteile entsprechend am Raspberry Pi anschließen und mit Strom versorgen
4. Main.py mit dem Befehl <br>```sudo python3 Main.py```<br>starten

