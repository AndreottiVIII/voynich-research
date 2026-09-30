# Esperimento 14: un tentativo di decifrazione

Sostituzione omofonica (più segni possono valere la stessa lettera), spazi = spazi fra parole. Per ogni lingua: chiave cercata con un modello a trigrammi di lettere della Bibbia in quella lingua.

- **parole vere**: quota delle parole decifrate che sono parole della lingua; **lunghe**: lo stesso per le parole di almeno 4 lettere.
- **coppie**: quota delle coppie di parole vicine (entrambe vere) che la lingua usa davvero; fra parentesi lo stesso con le parole rimescolate nella riga. Se il testo ha senso, la prima è molto più alta.
- **zodiaco**: pagine (su 12) in cui compare il nome del mese o del segno giusto; nomi di altri mesi o segni comparsi per sbaglio.

- **diverse**: quante parole vere diverse escono; **prime 3**: quanta parte delle parole vere coprono le tre più frequenti. Una chiave degenere schiaccia tutto su poche parole ripetute.

| lingua | testo | parole vere | diverse | prime 3 | lunghe | coppie (mescolate) | zodiaco |
|---|---|---|---|---|---|---|---|
| latino | controllo positivo | 90.6% | 4266 | 15% | 86.6% | 54.4% (30.4%) | – |
| latino | controllo negativo | 22.9% | 43 | 58% | 2.6% | 4.4% (7.1%) | – |
| latino | Voynich, glifi | 15.8% | 63 | 58% | 6.9% | 17.3% (16.4%) | 0 giuste, 2 fuori posto |
| latino | Voynich, glifi e serie di i | 14.0% | 69 | 62% | 3.7% | 23.2% (27.0%) | 1 giuste, 10 fuori posto |
| italiano | controllo positivo | 90.6% | 2799 | 12% | 84.0% | 71.5% (31.5%) | – |
| italiano | controllo negativo | 22.9% | 39 | 64% | 2.8% | 12.8% (5.8%) | – |
| italiano | Voynich, glifi | 21.9% | 93 | 31% | 8.8% | 20.1% (20.8%) | 0 giuste, 0 fuori posto |
| italiano | Voynich, glifi e serie di i | 26.6% | 48 | 60% | 2.2% | 10.7% (14.2%) | 0 giuste, 0 fuori posto |
| tedesco | controllo positivo | 93.9% | 2359 | 13% | 90.0% | 71.3% (42.7%) | – |
| tedesco | controllo negativo | 12.9% | 42 | 36% | 7.0% | 39.6% (33.0%) | – |
| tedesco | Voynich, glifi | 11.4% | 52 | 41% | 8.0% | 24.2% (22.8%) | 0 giuste, 0 fuori posto |
| tedesco | Voynich, glifi e serie di i | 9.8% | 38 | 70% | 7.8% | 39.3% (25.8%) | 2 giuste, 9 fuori posto |
| inglese | controllo positivo | 97.8% | 1433 | 23% | 95.9% | 82.0% (43.7%) | – |
| inglese | controllo negativo | 2.3% | 4 | 100% | 0.0% | 0.0% (0.0%) | – |
| inglese | Voynich, glifi | 12.6% | 46 | 52% | 6.5% | 13.3% (11.5%) | 0 giuste, 1 fuori posto |
| inglese | Voynich, glifi e serie di i | 19.7% | 64 | 42% | 6.6% | 13.2% (13.8%) | 0 giuste, 0 fuori posto |
| francese | controllo positivo | 95.8% | 1864 | 12% | 91.8% | 76.3% (33.8%) | – |
| francese | controllo negativo | 19.7% | 64 | 62% | 1.1% | 34.0% (28.8%) | – |
| francese | Voynich, glifi | 14.5% | 55 | 41% | 6.3% | 18.8% (19.9%) | 0 giuste, 0 fuori posto |
| francese | Voynich, glifi e serie di i | 28.3% | 52 | 55% | 14.7% | 2.7% (3.7%) | 0 giuste, 0 fuori posto |
| spagnolo | controllo positivo | 82.0% | 1880 | 19% | 68.3% | 76.8% (38.8%) | – |
| spagnolo | controllo negativo | 23.1% | 43 | 69% | 6.6% | 11.3% (6.9%) | – |
| spagnolo | Voynich, glifi | 19.6% | 30 | 53% | 8.1% | 7.9% (8.6%) | 0 giuste, 0 fuori posto |
| spagnolo | Voynich, glifi e serie di i | 27.5% | 43 | 60% | 1.5% | 13.0% (15.0%) | 0 giuste, 0 fuori posto |
| ceco | controllo positivo | 91.1% | 3986 | 11% | 86.8% | 58.2% (28.2%) | – |
| ceco | controllo negativo | 5.1% | 18 | 47% | 2.1% | 7.3% (10.1%) | – |
| ceco | Voynich, glifi | 6.2% | 29 | 65% | 1.1% | 22.1% (21.9%) | – |
| ceco | Voynich, glifi e serie di i | 6.0% | 28 | 66% | 1.0% | 20.6% (25.0%) | – |
| ungherese | controllo positivo | 85.8% | 4112 | 24% | 78.0% | 64.0% (37.3%) | – |
| ungherese | controllo negativo | 20.4% | 19 | 87% | 3.6% | 23.8% (54.1%) | – |
| ungherese | Voynich, glifi | 17.4% | 28 | 49% | 3.3% | 13.4% (12.7%) | – |
| ungherese | Voynich, glifi e serie di i | 27.9% | 54 | 34% | 12.7% | 0.9% (1.2%) | – |
| greco | controllo positivo | 92.1% | 2672 | 13% | 86.6% | 76.7% (35.0%) | – |
| greco | controllo negativo | 21.7% | 21 | 74% | 0.7% | 16.3% (16.9%) | – |
| greco | Voynich, glifi | 15.7% | 58 | 39% | 3.2% | 6.6% (7.4%) | – |
| greco | Voynich, glifi e serie di i | 22.7% | 43 | 58% | 3.8% | 11.9% (14.3%) | – |
| ebraico | controllo positivo | 89.2% | 5188 | 7% | 83.6% | 49.3% (20.5%) | – |
| ebraico | controllo negativo | 12.5% | 18 | 53% | 5.1% | 15.6% (8.8%) | – |
| ebraico | Voynich, glifi | 12.9% | 45 | 47% | 8.3% | 0.8% (2.2%) | – |
| ebraico | Voynich, glifi e serie di i | 31.1% | 56 | 47% | 11.4% | 6.1% (6.8%) | – |
| arabo | controllo positivo | 86.6% | 5445 | 7% | 81.3% | 53.5% (19.6%) | – |
| arabo | controllo negativo | 20.9% | 86 | 62% | 4.9% | 7.6% (32.0%) | – |
| arabo | Voynich, glifi | 32.5% | 71 | 25% | 17.1% | 6.7% (6.3%) | – |
| arabo | Voynich, glifi e serie di i | 35.6% | 76 | 39% | 12.6% | 5.0% (5.7%) | – |
| turco | controllo positivo | 86.4% | 5669 | 5% | 84.2% | 37.4% (13.1%) | – |
| turco | controllo negativo | 26.8% | 54 | 59% | 7.5% | 0.1% (0.0%) | – |
| turco | Voynich, glifi | 27.9% | 68 | 41% | 9.4% | 4.8% (4.0%) | – |
| turco | Voynich, glifi e serie di i | 27.3% | 38 | 68% | 6.5% | 4.9% (3.9%) | – |
| malgascio | controllo positivo | 69.4% | 629 | 31% | 48.3% | 72.2% (54.2%) | – |
| malgascio | controllo negativo | 24.8% | 26 | 66% | 7.5% | 18.1% (26.4%) | – |
| malgascio | Voynich, glifi | 25.6% | 88 | 26% | 12.9% | 9.6% (9.6%) | – |
| malgascio | Voynich, glifi e serie di i | 25.1% | 52 | 53% | 6.2% | 19.5% (15.9%) | – |
| chinanteco | controllo positivo | 97.7% | 2241 | 19% | 96.7% | 86.0% (51.7%) | – |
| chinanteco | controllo negativo | 19.6% | 8 | 75% | 2.2% | 0.1% (0.4%) | – |
| chinanteco | Voynich, glifi | 21.2% | 7 | 89% | 10.5% | 1.5% (1.3%) | – |
| chinanteco | Voynich, glifi e serie di i | 21.4% | 7 | 90% | 4.3% | 1.3% (2.1%) | – |

## Come "legge" il Voynich la chiave migliore, per alcune lingue

**latino**:

```
iesaa aret et eressi set seta ttia a ret setta
aeta tet et a rest sressi set eai tet tet tei
aaesst sira et aressi set teeta tia tetessi aa
aessi eriia eriea tetera tset tessi eressi et erei
```

**italiano**:

```
nusil inuo uo unutto dio dioi doal i nio dioti
lioi tuo io i nuto snutto duo ula duo duo tuo
liutto dani io inutto dit diuoi dal tuoutto li
litto inaai inail oioini dtuo tutto inutto io inuo
```

**tedesco**:

```
heees eher en eherrn eer eene dnrs e hen eerte
sene ten en e hern eherrn een esr den den ten
seerrn erhe en eherrn eet deene drs tenerrn se
serrn ehrre ehres nerehe dren terrn eherrn en ehen
```

