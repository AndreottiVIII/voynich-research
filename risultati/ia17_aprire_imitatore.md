# IA17 (ia17) — Aprire l'imitatore

Preregistrazione: `preregistrazioni/ia17.md`.

- **Modo: imitatore valido (ia16).**
- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.
- Taglia (scelta da ia16): **P**. Pieghe lette: P2 [0, 1, 2, 3, 4], P1 [0, 1, 2, 3, 4].

## Condizione d'ingresso (varianti di ia16 che hanno superato i loro controlli)

- P2: valida.
- P1: valida.
- R: valida.

## Controlli

- **Positivo, eco piantata a 2 righe:** attenzione: sollevamento a 2 righe 2,07 (1,93; 2,19) (soglia ≥ 3,0, limite basso ≥ 2,0), altre distanze al massimo 1,29 → NO. Maschere: k1 meno k2 0,150 bit per parola, caduta per eco 0,093 (0,069; 0,115) (soglia ≥ 0,30) → NO. Libri: righe copiate a 2 righe 0,000 con memoria piena, 0,000 con k1 (altre distanze al massimo 0,000) → NO.
- **Positivo, regole di eco:** la migliore regola di eco (eco: classe piu' vicina e posto nella riga) spiega il risparmio di bit della memoria con R² 0,052 (0,020; 0,079) (soglia ≥ 0,30, limite basso ≥ 0,20); albero a 16 foglie con le sole regole di eco 0,096 (0,045; 0,150) → NO.
- **Negativo, senza eco:** sollevamenti tutti nella banda 0,70–1,43: sì; caduta per eco 0,011 (0,004; 0,018) (soglia ≤ 0,05); k0 meno pieno 0,123 (descrittivo: effetto di un contesto mai visto, base delle letture dei bit); righe copiate al massimo 0,000; R² delle regole di eco al massimo 0,260 (soglia ≤ 0,03) → NO.
- **Strumento sulle pagine vere (parola da scrivere sbagliata):** stessa riga 1,01 (1,00; 1,01) → sì; 1-3 righe sopra 0,99 (0,99; 1,00) → sì; vicina (stessa riga e 1-3 sopra) 1,00 (1,00; 1,01) → sì; lontana (4 o piu' righe sopra) 1,00 (1,00; 1,01) → sì; pagina precedente 1,00 (0,99; 1,01) → sì.
- **Coerenza scrittura/maschera:** massima differenza 0,000010 bit (soglia ≤ 0,0010) → sì.
- **Riproduzione di ia16:** libro P2 numero 1 riscritto senza maschera: uguale a quello di ia16 → sì.
- Validità. Specificità (lo strumento non vede ciò che non c'è; serve a leggere un sì): attenzione sì, maschere sì, regole NO. Sensibilità (vede l'eco piantata; serve a leggere un no): attenzione NO, maschere NO, regole NO. Libri (coerenza e riproduzione di ia16): sì; con l'eco piantata nei libri NO.

## Riferimento: bit per segno dei modelli di ia16 (validazione / fuori piega)

P1 P: 1,956 / 1,939; P2 P: 1,965 / 1,954; P2 S: 1,966 / 1,958; R P: 2,000 / 1,995. Per confronto: le letture sopra con "solo la riga" (k0) sono lo stesso modello P2 con la memoria tolta in lettura, non un modello addestrato senza memoria (R).

*P2: stato in ia16 = valida.*

## P2: dove guarda (strati globali; sollevamento = attenzione osservata / attesa su parole non-eco alla stessa distanza)

| distanza in righe | sollevamento sull'eco | con la parola da scrivere sbagliata (controllo) | celle | lettura |
|---|---|---|---|---|
| stessa riga | 1,09 (1,07; 1,10) | 1,01 (1,00; 1,01) | 31475 | come il caso |
| 1 | 1,14 (1,12; 1,15) | 0,99 (0,99; 1,00) | 62891 | come il caso |
| 2 | 1,16 (1,14; 1,18) | 0,99 (0,98; 1,00) | 56053 | come il caso |
| 3 | 1,18 (1,15; 1,20) | 1,00 (0,99; 1,00) | 51979 | come il caso |
| 4-5 | 1,17 (1,15; 1,20) | 1,00 (0,99; 1,01) | 77293 | come il caso |
| 6-9 | 1,18 (1,15; 1,21) | 1,00 (0,99; 1,01) | 99185 | come il caso |
| 10-19 | 1,18 (1,15; 1,21) | 1,00 (1,00; 1,01) | 105966 | come il caso |
| 20+ | 1,18 (1,14; 1,23) | 1,02 (1,00; 1,04) | 66771 | come il caso |
| pagina precedente | 1,21 (1,19; 1,24) | 1,00 (0,99; 1,01) | 162083 | come il caso |

Per gruppo di distanze: stessa riga 1,09 (1,07; 1,10) (come il caso); 1-3 righe sopra 1,15 (1,13; 1,16) (come il caso); vicina (stessa riga e 1-3 sopra) 1,12 (1,11; 1,13) (come il caso); lontana (4 o piu' righe sopra) 1,17 (1,15; 1,20) (come il caso); pagina precedente 1,21 (1,19; 1,24) (come il caso).
Per testa (distanze vicine): 1,01, 1,15, 1,16.

Per tipo di eco: uguale, segno allineato: stessa riga 1,73 (1,67; 1,80), 1-3 righe sopra 2,19 (2,11; 2,27), vicina (stessa riga e 1-3 sopra) 1,99 (1,93; 2,06), lontana (4 o piu' righe sopra) 2,06 (1,96; 2,20), pagina precedente 2,37 (2,19; 2,57); uguale, altri segni: stessa riga 0,99 (0,97; 1,01), 1-3 righe sopra 0,99 (0,97; 1,01), vicina (stessa riga e 1-3 sopra) 0,99 (0,97; 1,01), lontana (4 o piu' righe sopra) 1,06 (1,03; 1,09), pagina precedente 1,12 (1,08; 1,17); a una modifica: stessa riga 1,08 (1,07; 1,09), 1-3 righe sopra 1,13 (1,12; 1,14), vicina (stessa riga e 1-3 sopra) 1,11 (1,10; 1,12), lontana (4 o piu' righe sopra) 1,16 (1,13; 1,18), pagina precedente 1,18 (1,16; 1,20).

**Quando indovina: inizio parola (si indovina il primo glifo)** (34863 segni che guardano)

| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |
|---|---|---|---|---|
| coda pagina precedente | 0,083 (0,074; 0,093) | 0,447 (0,418; 0,480) | 0,19 (0,18; 0,20) | meno del caso |
| testa di pagina | 0,002 (0,002; 0,002) | 0,004 (0,004; 0,005) | 0,52 (0,48; 0,56) | meno del caso |
| testa di riga | 0,055 (0,053; 0,057) | 0,032 (0,031; 0,033) | 1,70 (1,62; 1,80) | piu' del caso |
| stessa riga: parola da scrivere (segni gia' scritti) | 0,000 (0,000; 0,000) | 0,000 (0,000; 0,000) | — | zona grigia |
| stessa riga: parola prima | 0,214 (0,211; 0,216) | 0,005 (0,005; 0,005) | 42,33 (39,21; 45,03) | piu' del caso |
| stessa riga: seconda prima | 0,095 (0,094; 0,096) | 0,004 (0,004; 0,005) | 21,93 (20,44; 23,20) | piu' del caso |
| stessa riga: altre | 0,114 (0,109; 0,118) | 0,014 (0,014; 0,015) | 7,95 (7,48; 8,38) | piu' del caso |
| 1 riga sopra | 0,221 (0,219; 0,222) | 0,046 (0,045; 0,049) | 4,75 (4,51; 4,96) | piu' del caso |
| 2 righe sopra | 0,074 (0,074; 0,075) | 0,041 (0,040; 0,042) | 1,82 (1,74; 1,89) | piu' del caso |
| 3 righe sopra | 0,041 (0,040; 0,041) | 0,037 (0,036; 0,038) | 1,11 (1,07; 1,15) | come il caso |
| 4-5 righe sopra | 0,045 (0,044; 0,046) | 0,062 (0,061; 0,064) | 0,72 (0,70; 0,75) | zona grigia |
| 6-9 righe sopra | 0,038 (0,036; 0,040) | 0,092 (0,088; 0,096) | 0,41 (0,40; 0,43) | meno del caso |
| 10-19 righe sopra | 0,017 (0,016; 0,019) | 0,127 (0,111; 0,141) | 0,14 (0,13; 0,15) | meno del caso |
| 20+ righe sopra | 0,001 (0,001; 0,002) | 0,087 (0,071; 0,100) | 0,01 (0,01; 0,02) | meno del caso |
| prime due righe della pagina (da riga 4) | 0,021 (0,018; 0,024) | 0,083 (0,078; 0,088) | 0,25 (0,23; 0,27) | meno del caso |

**Quando indovina: dentro la parola** (120652 segni che guardano)

| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |
|---|---|---|---|---|
| coda pagina precedente | 0,078 (0,070; 0,088) | 0,438 (0,410; 0,470) | 0,18 (0,17; 0,19) | meno del caso |
| testa di pagina | 0,005 (0,004; 0,006) | 0,004 (0,004; 0,004) | 1,26 (1,18; 1,34) | zona grigia |
| testa di riga | 0,053 (0,051; 0,054) | 0,032 (0,031; 0,033) | 1,64 (1,57; 1,72) | piu' del caso |
| stessa riga: parola da scrivere (segni gia' scritti) | 0,131 (0,130; 0,132) | 0,003 (0,003; 0,003) | 48,35 (44,89; 51,31) | piu' del caso |
| stessa riga: parola prima | 0,155 (0,154; 0,157) | 0,005 (0,005; 0,005) | 31,51 (29,45; 33,22) | piu' del caso |
| stessa riga: seconda prima | 0,074 (0,073; 0,074) | 0,004 (0,004; 0,004) | 17,50 (16,44; 18,38) | piu' del caso |
| stessa riga: altre | 0,099 (0,094; 0,103) | 0,014 (0,013; 0,014) | 7,30 (6,87; 7,68) | piu' del caso |
| 1 riga sopra | 0,196 (0,195; 0,197) | 0,045 (0,044; 0,048) | 4,31 (4,11; 4,49) | piu' del caso |
| 2 righe sopra | 0,071 (0,071; 0,072) | 0,041 (0,039; 0,042) | 1,76 (1,69; 1,82) | piu' del caso |
| 3 righe sopra | 0,039 (0,038; 0,040) | 0,037 (0,036; 0,038) | 1,07 (1,03; 1,11) | come il caso |
| 4-5 righe sopra | 0,044 (0,043; 0,045) | 0,063 (0,061; 0,064) | 0,70 (0,68; 0,72) | zona grigia |
| 6-9 righe sopra | 0,037 (0,035; 0,039) | 0,093 (0,089; 0,097) | 0,40 (0,39; 0,41) | meno del caso |
| 10-19 righe sopra | 0,017 (0,015; 0,018) | 0,131 (0,116; 0,145) | 0,13 (0,12; 0,14) | meno del caso |
| 20+ righe sopra | 0,001 (0,001; 0,001) | 0,091 (0,075; 0,104) | 0,01 (0,01; 0,02) | meno del caso |
| prime due righe della pagina (da riga 4) | 0,019 (0,017; 0,022) | 0,081 (0,077; 0,087) | 0,24 (0,22; 0,26) | meno del caso |

**Quando indovina: fine parola (spazio o a capo)** (34863 segni che guardano)

| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |
|---|---|---|---|---|
| coda pagina precedente | 0,079 (0,070; 0,088) | 0,445 (0,415; 0,477) | 0,18 (0,17; 0,19) | meno del caso |
| testa di pagina | 0,004 (0,003; 0,004) | 0,004 (0,004; 0,004) | 0,91 (0,84; 0,97) | come il caso |
| testa di riga | 0,064 (0,062; 0,066) | 0,032 (0,031; 0,033) | 2,00 (1,90; 2,11) | piu' del caso |
| stessa riga: parola da scrivere (segni gia' scritti) | 0,205 (0,203; 0,206) | 0,005 (0,004; 0,005) | 43,80 (40,70; 46,54) | piu' del caso |
| stessa riga: parola prima | 0,122 (0,121; 0,123) | 0,005 (0,005; 0,005) | 24,21 (22,59; 25,63) | piu' del caso |
| stessa riga: seconda prima | 0,059 (0,058; 0,060) | 0,004 (0,004; 0,005) | 13,62 (12,74; 14,40) | piu' del caso |
| stessa riga: altre | 0,080 (0,076; 0,084) | 0,014 (0,013; 0,015) | 5,63 (5,29; 5,95) | piu' del caso |
| 1 riga sopra | 0,185 (0,183; 0,186) | 0,046 (0,044; 0,048) | 4,00 (3,80; 4,18) | piu' del caso |
| 2 righe sopra | 0,069 (0,068; 0,069) | 0,041 (0,039; 0,042) | 1,69 (1,62; 1,76) | piu' del caso |
| 3 righe sopra | 0,038 (0,037; 0,039) | 0,036 (0,036; 0,037) | 1,04 (1,01; 1,08) | come il caso |
| 4-5 righe sopra | 0,043 (0,042; 0,044) | 0,062 (0,061; 0,064) | 0,69 (0,67; 0,71) | zona grigia |
| 6-9 righe sopra | 0,036 (0,034; 0,038) | 0,092 (0,087; 0,096) | 0,40 (0,38; 0,41) | meno del caso |
| 10-19 righe sopra | 0,016 (0,015; 0,018) | 0,127 (0,111; 0,141) | 0,13 (0,12; 0,14) | meno del caso |
| 20+ righe sopra | 0,001 (0,001; 0,001) | 0,087 (0,071; 0,100) | 0,01 (0,01; 0,02) | meno del caso |
| prime due righe della pagina (da riga 4) | 0,020 (0,018; 0,023) | 0,082 (0,078; 0,088) | 0,25 (0,23; 0,27) | meno del caso |

## P2: che cosa succede ai bit se si toglie la memoria (pagine tenute fuori)

| condizione | bit per segno | bit in piu' per parola | base (controllo senza eco) | in piu' per segno | solo primo glifo | parole con eco | lettura |
|---|---|---|---|---|---|---|---|
| senza la pagina precedente | 1,947 (1,915; 1,984) | 0,002 (-0,002; 0,005) | 0,000 | 0,000 (-0,000; 0,001) | 0,001 (-0,000; 0,003) | 0,005 (0,003; 0,009) | non dipende |
| solo la riga | 2,179 (2,144; 2,222) | 1,265 (1,199; 1,339) | 0,123 | 0,232 (0,219; 0,247) | 0,297 (0,276; 0,318) | 1,218 (1,155; 1,290) | dipende |
| riga e 1 sopra | 1,954 (1,922; 1,991) | 0,040 (0,031; 0,050) | -0,021 | 0,007 (0,006; 0,009) | 0,015 (0,012; 0,018) | 0,050 (0,041; 0,059) | dipende |
| riga e 2 sopra | 1,949 (1,918; 1,985) | 0,013 (0,007; 0,019) | -0,008 | 0,002 (0,001; 0,003) | 0,005 (0,004; 0,008) | 0,018 (0,012; 0,024) | non dipende |
| riga e 4 sopra | 1,947 (1,916; 1,984) | 0,003 (-0,001; 0,008) | 0,000 | 0,001 (-0,000; 0,001) | 0,002 (0,001; 0,004) | 0,008 (0,003; 0,012) | non dipende |
| riga e 8 sopra | 1,947 (1,915; 1,984) | 0,001 (-0,002; 0,005) | 0,000 | 0,000 (-0,000; 0,001) | 0,001 (-0,000; 0,003) | 0,005 (0,002; 0,009) | non dipende |
| senza le parole eco (uguali o a una modifica) | 1,982 (1,953; 2,017) | 0,192 (0,174; 0,210) | 0,020 | 0,035 (0,032; 0,038) | 0,081 (0,071; 0,091) | 0,246 (0,226; 0,267) | conta |
| senza altrettante parole non-eco | 1,958 (1,927; 1,993) | 0,058 (0,051; 0,065) | 0,009 | 0,011 (0,009; 0,012) | 0,038 (0,034; 0,044) | 0,077 (0,069; 0,086) | conta |
| senza le parole uguali | 1,955 (1,924; 1,991) | 0,044 (0,038; 0,051) | 0,000 | 0,008 (0,007; 0,009) | 0,020 (0,016; 0,023) | 0,057 (0,049; 0,064) | conta |
| senza altrettante parole non uguali | 1,950 (1,918; 1,986) | 0,017 (0,014; 0,021) | 0,000 | 0,003 (0,003; 0,004) | 0,011 (0,009; 0,014) | 0,023 (0,019; 0,028) | non conta |

Memoria piena: 1,947 (1,915; 1,983) bit per segno. Quota di parole con un'eco già scritta (nella pagina o nella coda): 0,801.
- caduta per eco: 0,134 (0,117; 0,151) bit per parola (togliere le parole eco meno togliere altrettante non-eco) → conta.
- caduta per eco uguale: 0,027 (0,021; 0,033) bit per parola (togliere le parole eco meno togliere altrettante non-eco) → zona grigia.
- Quota del risparmio di "solo la riga" che si perde con k righe: k1 0,03, k2 0,01, k4 0,00, k8 0,00; la memoria utile sta entro 1 righe.

Bordi della riga letti dall'imitatore (bit in più per parola quando le parole di ogni riga sono rimescolate, solo glifi, appaiati per posto; ia13, GRU sul vero: prima 1,142, ultima -0,581, R_prima 1,28, R_ultima -0,47): prima parola 1,27 (1,07; 1,48); seconda parola 1,78 (1,61; 1,94); dal terzo posto al penultimo 1,20 (1,13; 1,28); ultima parola -0,67 (-0,90; -0,44); R_prima 1,06 (0,87; 1,27); R_ultima -0,56 (-0,74; -0,38).

Bit in più per parola con "solo la riga", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,915 (0,838; 0,995), glifi interni 4,347 (4,190; 4,520), ultimo glifo 0,065 (0,021; 0,110), spazio o a capo -0,096 (-0,137; -0,058); interne: primo glifo 0,240 (0,220; 0,261), glifi interni 0,406 (0,378; 0,437), ultimo glifo -0,030 (-0,042; -0,017), spazio o a capo 0,252 (0,229; 0,278); ultima parola: primo glifo 0,046 (0,026; 0,067), glifi interni 0,156 (0,121; 0,197), ultimo glifo -0,061 (-0,080; -0,043), spazio o a capo -0,290 (-0,365; -0,203).
Bit in più per parola con "senza la pagina precedente", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,006 (0,003; 0,010), glifi interni 0,009 (-0,000; 0,017), ultimo glifo 0,001 (-0,005; 0,006), spazio o a capo 0,003 (0,001; 0,006); interne: primo glifo 0,001 (-0,001; 0,003), glifi interni 0,002 (-0,001; 0,005), ultimo glifo -0,000 (-0,004; 0,003), spazio o a capo 0,006 (0,004; 0,008); ultima parola: primo glifo -0,000 (-0,003; 0,003), glifi interni -0,002 (-0,006; 0,002), ultimo glifo -0,003 (-0,008; 0,001), spazio o a capo -0,052 (-0,074; -0,033).
Bit in più per parola con "senza le parole eco (uguali o a una modifica)", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,010 (0,006; 0,013), glifi interni 0,045 (0,038; 0,052), ultimo glifo 0,016 (0,013; 0,019), spazio o a capo 0,002 (0,000; 0,004); interne: primo glifo 0,095 (0,083; 0,109), glifi interni 0,107 (0,097; 0,117), ultimo glifo 0,003 (-0,000; 0,007), spazio o a capo -0,005 (-0,007; -0,004); ultima parola: primo glifo 0,059 (0,047; 0,070), glifi interni 0,061 (0,049; 0,075), ultimo glifo 0,015 (0,009; 0,021), spazio o a capo 0,123 (0,108; 0,139).
Bit in più per parola con "senza altrettante parole non-eco", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,002 (-0,001; 0,006), glifi interni -0,003 (-0,007; 0,001), ultimo glifo 0,004 (0,001; 0,007), spazio o a capo -0,000 (-0,002; 0,002); interne: primo glifo 0,044 (0,038; 0,051), glifi interni 0,026 (0,021; 0,030), ultimo glifo -0,014 (-0,017; -0,011), spazio o a capo -0,009 (-0,010; -0,007); ultima parola: primo glifo 0,038 (0,028; 0,049), glifi interni 0,004 (-0,003; 0,011), ultimo glifo 0,008 (0,002; 0,013), spazio o a capo 0,135 (0,120; 0,150).


*P1: stato in ia16 = valida.*

## P1: dove guarda (strati globali; sollevamento = attenzione osservata / attesa su parole non-eco alla stessa distanza)

| distanza in righe | sollevamento sull'eco | con la parola da scrivere sbagliata (controllo) | celle | lettura |
|---|---|---|---|---|
| stessa riga | 1,04 (1,03; 1,05) | 1,00 (0,99; 1,01) | 31475 | come il caso |
| 1 | 1,07 (1,06; 1,08) | 0,99 (0,98; 1,00) | 62891 | come il caso |
| 2 | 1,11 (1,10; 1,13) | 0,99 (0,98; 1,00) | 56053 | come il caso |
| 3 | 1,15 (1,13; 1,17) | 0,99 (0,98; 1,00) | 51979 | come il caso |
| 4-5 | 1,16 (1,14; 1,19) | 1,00 (0,99; 1,01) | 77293 | come il caso |
| 6-9 | 1,18 (1,16; 1,21) | 1,00 (0,99; 1,01) | 99185 | come il caso |
| 10-19 | 1,20 (1,17; 1,23) | 1,00 (0,99; 1,01) | 105966 | come il caso |
| 20+ | 1,19 (1,16; 1,23) | 1,02 (1,00; 1,03) | 66771 | come il caso |
| pagina precedente | — | — | 0 | zona grigia |

Per gruppo di distanze: stessa riga 1,04 (1,03; 1,05) (come il caso); 1-3 righe sopra 1,09 (1,08; 1,10) (come il caso); vicina (stessa riga e 1-3 sopra) 1,07 (1,06; 1,08) (come il caso); lontana (4 o piu' righe sopra) 1,18 (1,15; 1,20) (come il caso); pagina precedente — (zona grigia).
Per testa (distanze vicine): 1,00, 1,02, 1,17.

Per tipo di eco: uguale, segno allineato: stessa riga 1,50 (1,45; 1,55), 1-3 righe sopra 1,87 (1,81; 1,95), vicina (stessa riga e 1-3 sopra) 1,71 (1,67; 1,77), lontana (4 o piu' righe sopra) 2,08 (1,98; 2,20), pagina precedente —; uguale, altri segni: stessa riga 0,96 (0,95; 0,98), 1-3 righe sopra 0,97 (0,95; 0,99), vicina (stessa riga e 1-3 sopra) 0,96 (0,95; 0,98), lontana (4 o piu' righe sopra) 1,05 (1,02; 1,08), pagina precedente —; a una modifica: stessa riga 1,03 (1,03; 1,04), 1-3 righe sopra 1,08 (1,07; 1,09), vicina (stessa riga e 1-3 sopra) 1,06 (1,05; 1,07), lontana (4 o piu' righe sopra) 1,16 (1,14; 1,19), pagina precedente —.

**Quando indovina: inizio parola (si indovina il primo glifo)** (34863 segni che guardano)

| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |
|---|---|---|---|---|
| coda pagina precedente | 0,000 (0,000; 0,000) | 0,000 (0,000; 0,000) | — | zona grigia |
| testa di pagina | 0,005 (0,005; 0,006) | 0,021 (0,019; 0,023) | 0,26 (0,25; 0,27) | meno del caso |
| testa di riga | 0,072 (0,068; 0,076) | 0,066 (0,064; 0,069) | 1,08 (1,05; 1,12) | come il caso |
| stessa riga: parola da scrivere (segni gia' scritti) | 0,000 (0,000; 0,000) | 0,000 (0,000; 0,000) | — | zona grigia |
| stessa riga: parola prima | 0,221 (0,219; 0,222) | 0,022 (0,020; 0,024) | 10,02 (9,06; 11,00) | piu' del caso |
| stessa riga: seconda prima | 0,100 (0,099; 0,101) | 0,018 (0,016; 0,019) | 5,71 (5,19; 6,22) | piu' del caso |
| stessa riga: altre | 0,126 (0,122; 0,130) | 0,050 (0,046; 0,054) | 2,54 (2,34; 2,75) | piu' del caso |
| 1 riga sopra | 0,237 (0,235; 0,239) | 0,128 (0,120; 0,138) | 1,84 (1,73; 1,96) | piu' del caso |
| 2 righe sopra | 0,083 (0,082; 0,084) | 0,094 (0,089; 0,100) | 0,88 (0,83; 0,92) | come il caso |
| 3 righe sopra | 0,046 (0,045; 0,046) | 0,076 (0,072; 0,079) | 0,60 (0,58; 0,63) | meno del caso |
| 4-5 righe sopra | 0,050 (0,049; 0,051) | 0,116 (0,112; 0,120) | 0,43 (0,42; 0,45) | meno del caso |
| 6-9 righe sopra | 0,041 (0,039; 0,043) | 0,148 (0,144; 0,151) | 0,28 (0,27; 0,29) | meno del caso |
| 10-19 righe sopra | 0,018 (0,016; 0,019) | 0,166 (0,149; 0,182) | 0,11 (0,10; 0,12) | meno del caso |
| 20+ righe sopra | 0,001 (0,001; 0,002) | 0,096 (0,079; 0,109) | 0,01 (0,01; 0,02) | meno del caso |
| prime due righe della pagina (da riga 4) | 0,027 (0,024; 0,032) | 0,163 (0,152; 0,177) | 0,17 (0,16; 0,18) | meno del caso |

**Quando indovina: dentro la parola** (120652 segni che guardano)

| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |
|---|---|---|---|---|
| coda pagina precedente | 0,000 (0,000; 0,000) | 0,000 (0,000; 0,000) | — | zona grigia |
| testa di pagina | 0,011 (0,010; 0,013) | 0,019 (0,018; 0,022) | 0,59 (0,58; 0,61) | meno del caso |
| testa di riga | 0,070 (0,067; 0,074) | 0,064 (0,062; 0,067) | 1,09 (1,05; 1,14) | come il caso |
| stessa riga: parola da scrivere (segni gia' scritti) | 0,134 (0,132; 0,135) | 0,013 (0,012; 0,014) | 10,43 (9,40; 11,49) | piu' del caso |
| stessa riga: parola prima | 0,160 (0,159; 0,161) | 0,021 (0,019; 0,023) | 7,75 (7,05; 8,48) | piu' del caso |
| stessa riga: seconda prima | 0,077 (0,076; 0,078) | 0,016 (0,015; 0,018) | 4,67 (4,27; 5,08) | piu' del caso |
| stessa riga: altre | 0,106 (0,102; 0,110) | 0,046 (0,042; 0,050) | 2,32 (2,14; 2,51) | piu' del caso |
| 1 riga sopra | 0,211 (0,210; 0,213) | 0,122 (0,115; 0,132) | 1,73 (1,62; 1,83) | piu' del caso |
| 2 righe sopra | 0,079 (0,078; 0,080) | 0,091 (0,087; 0,097) | 0,87 (0,82; 0,91) | come il caso |
| 3 righe sopra | 0,044 (0,043; 0,044) | 0,074 (0,071; 0,078) | 0,59 (0,56; 0,62) | meno del caso |
| 4-5 righe sopra | 0,048 (0,048; 0,049) | 0,114 (0,111; 0,118) | 0,42 (0,41; 0,44) | meno del caso |
| 6-9 righe sopra | 0,040 (0,038; 0,041) | 0,148 (0,144; 0,151) | 0,27 (0,26; 0,28) | meno del caso |
| 10-19 righe sopra | 0,018 (0,016; 0,019) | 0,171 (0,154; 0,186) | 0,10 (0,10; 0,11) | meno del caso |
| 20+ righe sopra | 0,001 (0,001; 0,001) | 0,099 (0,083; 0,113) | 0,01 (0,01; 0,02) | meno del caso |
| prime due righe della pagina (da riga 4) | 0,025 (0,022; 0,029) | 0,159 (0,148; 0,172) | 0,16 (0,15; 0,17) | meno del caso |

**Quando indovina: fine parola (spazio o a capo)** (34863 segni che guardano)

| bersaglio | quota di attenzione | quota di segni | sollevamento | lettura |
|---|---|---|---|---|
| coda pagina precedente | 0,000 (0,000; 0,000) | 0,000 (0,000; 0,000) | — | zona grigia |
| testa di pagina | 0,008 (0,007; 0,009) | 0,018 (0,016; 0,020) | 0,45 (0,44; 0,47) | meno del caso |
| testa di riga | 0,081 (0,078; 0,085) | 0,063 (0,061; 0,066) | 1,28 (1,24; 1,32) | zona grigia |
| stessa riga: parola da scrivere (segni gia' scritti) | 0,209 (0,208; 0,211) | 0,020 (0,018; 0,022) | 10,37 (9,41; 11,38) | piu' del caso |
| stessa riga: parola prima | 0,128 (0,127; 0,129) | 0,020 (0,018; 0,022) | 6,36 (5,80; 6,94) | piu' del caso |
| stessa riga: seconda prima | 0,063 (0,063; 0,064) | 0,016 (0,015; 0,018) | 3,89 (3,56; 4,23) | piu' del caso |
| stessa riga: altre | 0,091 (0,087; 0,094) | 0,047 (0,044; 0,051) | 1,93 (1,77; 2,08) | piu' del caso |
| 1 riga sopra | 0,199 (0,197; 0,200) | 0,125 (0,117; 0,134) | 1,59 (1,49; 1,69) | piu' del caso |
| 2 righe sopra | 0,076 (0,075; 0,077) | 0,093 (0,088; 0,098) | 0,82 (0,78; 0,86) | zona grigia |
| 3 righe sopra | 0,042 (0,042; 0,043) | 0,075 (0,072; 0,078) | 0,56 (0,54; 0,59) | meno del caso |
| 4-5 righe sopra | 0,047 (0,046; 0,048) | 0,115 (0,111; 0,119) | 0,41 (0,39; 0,42) | meno del caso |
| 6-9 righe sopra | 0,038 (0,036; 0,039) | 0,147 (0,143; 0,150) | 0,26 (0,25; 0,27) | meno del caso |
| 10-19 righe sopra | 0,016 (0,015; 0,018) | 0,166 (0,148; 0,181) | 0,10 (0,09; 0,11) | meno del caso |
| 20+ righe sopra | 0,001 (0,001; 0,001) | 0,096 (0,079; 0,109) | 0,01 (0,01; 0,01) | meno del caso |
| prime due righe della pagina (da riga 4) | 0,025 (0,022; 0,029) | 0,161 (0,151; 0,175) | 0,16 (0,15; 0,17) | meno del caso |

## P1: che cosa succede ai bit se si toglie la memoria (pagine tenute fuori)

| condizione | bit per segno | bit in piu' per parola | base (controllo senza eco) | in piu' per segno | solo primo glifo | parole con eco | lettura |
|---|---|---|---|---|---|---|---|
| solo la riga | 2,093 (2,060; 2,133) | 0,877 (0,823; 0,938) | 0,123 | 0,161 (0,150; 0,172) | 0,217 (0,199; 0,236) | 0,849 (0,801; 0,904) | dipende |
| riga e 1 sopra | 1,939 (1,905; 1,977) | 0,037 (0,028; 0,045) | -0,021 | 0,007 (0,005; 0,008) | 0,015 (0,013; 0,018) | 0,050 (0,041; 0,059) | dipende |
| riga e 2 sopra | 1,934 (1,900; 1,973) | 0,009 (0,003; 0,014) | -0,008 | 0,002 (0,001; 0,003) | 0,004 (0,003; 0,005) | 0,016 (0,009; 0,022) | non dipende |
| riga e 4 sopra | 1,932 (1,899; 1,970) | -0,000 (-0,004; 0,003) | 0,000 | -0,000 (-0,001; 0,001) | 0,001 (0,000; 0,002) | 0,002 (-0,003; 0,006) | non dipende |
| riga e 8 sopra | 1,932 (1,899; 1,970) | -0,001 (-0,003; 0,001) | 0,000 | -0,000 (-0,001; 0,000) | 0,000 (-0,000; 0,000) | -0,000 (-0,003; 0,001) | non dipende |
| senza le parole eco (uguali o a una modifica) | 1,968 (1,937; 2,005) | 0,197 (0,181; 0,215) | 0,020 | 0,036 (0,033; 0,039) | 0,081 (0,071; 0,091) | 0,295 (0,272; 0,320) | conta |
| senza altrettante parole non-eco | 1,943 (1,910; 1,981) | 0,060 (0,053; 0,067) | 0,009 | 0,011 (0,010; 0,012) | 0,038 (0,033; 0,043) | 0,092 (0,083; 0,102) | conta |
| senza le parole uguali | 1,941 (1,908; 1,978) | 0,046 (0,040; 0,052) | 0,000 | 0,008 (0,007; 0,009) | 0,020 (0,017; 0,024) | 0,068 (0,060; 0,077) | conta |
| senza altrettante parole non uguali | 1,935 (1,902; 1,973) | 0,017 (0,014; 0,021) | 0,000 | 0,003 (0,003; 0,004) | 0,012 (0,009; 0,014) | 0,026 (0,021; 0,031) | non conta |

Memoria piena: 1,932 (1,899; 1,971) bit per segno. Quota di parole con un'eco già scritta (nella pagina o nella coda): 0,690.
- caduta per eco: 0,138 (0,121; 0,154) bit per parola (togliere le parole eco meno togliere altrettante non-eco) → conta.
- caduta per eco uguale: 0,029 (0,023; 0,034) bit per parola (togliere le parole eco meno togliere altrettante non-eco) → zona grigia.
- Quota del risparmio di "solo la riga" che si perde con k righe: k1 0,04, k2 0,01, k4 -0,00, k8 -0,00; la memoria utile sta entro 1 righe.

Bordi della riga letti dall'imitatore (bit in più per parola quando le parole di ogni riga sono rimescolate, solo glifi, appaiati per posto; ia13, GRU sul vero: prima 1,142, ultima -0,581, R_prima 1,28, R_ultima -0,47): prima parola 1,31 (1,09; 1,52); seconda parola 1,82 (1,65; 1,99); dal terzo posto al penultimo 1,24 (1,17; 1,32); ultima parola -0,54 (-0,77; -0,30); R_prima 1,05 (0,86; 1,25); R_ultima -0,43 (-0,61; -0,26).

Bit in più per parola con "solo la riga", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,655 (0,559; 0,753), glifi interni 3,134 (2,958; 3,302), ultimo glifo 0,057 (0,007; 0,109), spazio o a capo -0,157 (-0,195; -0,121); interne: primo glifo 0,173 (0,158; 0,189), glifi interni 0,315 (0,287; 0,343), ultimo glifo -0,042 (-0,053; -0,030), spazio o a capo 0,182 (0,164; 0,202); ultima parola: primo glifo 0,057 (0,040; 0,074), glifi interni 0,144 (0,114; 0,180), ultimo glifo -0,038 (-0,057; -0,019), spazio o a capo -0,507 (-0,580; -0,439).
Bit in più per parola con "senza le parole eco (uguali o a una modifica)", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,011 (0,008; 0,015), glifi interni 0,048 (0,041; 0,055), ultimo glifo 0,012 (0,010; 0,015), spazio o a capo 0,001 (-0,002; 0,003); interne: primo glifo 0,095 (0,083; 0,108), glifi interni 0,114 (0,103; 0,124), ultimo glifo 0,002 (-0,001; 0,006), spazio o a capo -0,007 (-0,009; -0,005); ultima parola: primo glifo 0,059 (0,048; 0,070), glifi interni 0,066 (0,053; 0,081), ultimo glifo 0,017 (0,011; 0,023), spazio o a capo 0,139 (0,122; 0,157).
Bit in più per parola con "senza altrettante parole non-eco", per posto nella riga e pezzo della parola: prima parola: primo glifo 0,004 (0,001; 0,008), glifi interni -0,001 (-0,004; 0,003), ultimo glifo 0,002 (-0,001; 0,005), spazio o a capo -0,001 (-0,003; 0,000); interne: primo glifo 0,044 (0,038; 0,051), glifi interni 0,027 (0,023; 0,031), ultimo glifo -0,015 (-0,018; -0,012), spazio o a capo -0,008 (-0,010; -0,007); ultima parola: primo glifo 0,030 (0,020; 0,041), glifi interni 0,005 (-0,003; 0,012), ultimo glifo 0,006 (-0,001; 0,012), spazio o a capo 0,148 (0,132; 0,163).

## Libri scritti con la memoria ridotta (stessi modelli e stessi semi di P2)

| testo | n | copia netta | quota locale Λ | D | contatto | inizio_primo | inizio_ultimo | inizio_lung | fine_primo | fine_ultimo | fine_lung |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vero | — | 0,114 | 0,207 | 0,144 | 0,188 | 0,201 | 0,015 | 0,022 | 0,049 | 0,088 | 0,006 |
| P2 | 5 | 0,087 ± 0,002 | 0,109 ± 0,021 | 0,127 ± 0,002 | 0,135 ± 0,002 | 0,220 ± 0,002 | 0,012 ± 0,001 | 0,019 ± 0,001 | 0,073 ± 0,002 | 0,095 ± 0,003 | 0,019 ± 0,001 |
| SP | 5 | 0,085 ± 0,003 | 0,088 ± 0,006 | 0,125 ± 0,003 | 0,133 ± 0,001 | 0,230 ± 0,002 | 0,012 ± 0,000 | 0,019 ± 0,001 | 0,067 ± 0,003 | 0,091 ± 0,001 | 0,017 ± 0,001 |
| K0 | 5 | 0,067 ± 0,004 | 0,261 ± 0,042 | 0,067 ± 0,002 | 0,077 ± 0,002 | 0,147 ± 0,002 | 0,035 ± 0,002 | 0,055 ± 0,002 | 0,034 ± 0,001 | 0,057 ± 0,001 | 0,013 ± 0,001 |
| K1 | 5 | 0,075 ± 0,003 | 0,186 ± 0,044 | 0,120 ± 0,001 | 0,129 ± 0,002 | 0,221 ± 0,004 | 0,013 ± 0,001 | 0,016 ± 0,001 | 0,062 ± 0,001 | 0,090 ± 0,002 | 0,018 ± 0,001 |
| K3 | 5 | 0,089 ± 0,004 | 0,110 ± 0,022 | 0,121 ± 0,001 | 0,131 ± 0,001 | 0,224 ± 0,002 | 0,013 ± 0,001 | 0,019 ± 0,001 | 0,069 ± 0,002 | 0,088 ± 0,002 | 0,016 ± 0,001 |

- P2 ha un'eco da perdere? copia netta di P2 0,087 contro 0,114 del vero (soglia: metà del vero) → sì.
- SP contro P2: copia_netta uguale entro l'errore; lam uguale entro l'errore; D uguale entro l'errore; contatto uguale entro l'errore; bordi_distanza_dal_vero: imitatore_ablato 0.011244528226955002, P2 0.011532996430666931.
- K0 contro P2: copia_netta cala; lam cresce; D cala; contatto cala; bordi_distanza_dal_vero: imitatore_ablato 0.0267194748452942, P2 0.011532996430666931.
- K1 contro P2: copia_netta cala; lam uguale entro l'errore; D cala; contatto cala; bordi_distanza_dal_vero: imitatore_ablato 0.009375790609711956, P2 0.011532996430666931.
- K3 contro P2: copia_netta uguale entro l'errore; lam uguale entro l'errore; D cala; contatto cala; bordi_distanza_dal_vero: imitatore_ablato 0.009738795196761936, P2 0.011532996430666931.
- **Lettura K0: l'eco cala ma resta.**
- **Lettura K1: l'eco cala ma resta.**
- **Lettura K3: l'eco non cambia.**
- **Lettura SP: l'eco non cambia.**

## Regole distillate (R² fuori campione, intervallo col bootstrap sulle pagine; ia13: albero a 16 foglie 0,193, migliore tabella 0,268, soffitto 0,674)

**P2, ordine** (30733 parole): variazione media 0,880, soffitto 0,852.
- alberi: pezzi: 4 foglie 0,098 (0,087; 0,109), 8 foglie 0,127 (0,112; 0,140), 16 foglie 0,170 (0,155; 0,183), 32 foglie 0,223 (0,207; 0,236); eco: 4 foglie 0,045 (0,037; 0,052), 8 foglie 0,049 (0,041; 0,058), 16 foglie 0,052 (0,043; 0,060), 32 foglie 0,051 (0,042; 0,061); pezzi+eco: 4 foglie 0,098 (0,087; 0,109), 8 foglie 0,127 (0,112; 0,140), 16 foglie 0,170 (0,155; 0,183), 32 foglie 0,223 (0,207; 0,236).
- migliore tabella di pezzi: ultimo(prec) -> primi2 (0,175 (0,162; 0,185)); migliore regola di eco: eco: classe piu' vicina e posto nella riga (0,004 (0,002; 0,006)).
- letture: albero16_pezzi: zona grigia; albero16_pezzi_contro_ia13: come ia13 (entro 0,05); albero16_eco: poco; albero16_pezzi_e_eco: zona grigia; migliore_tabella_pezzi: zona grigia; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P2, mem_k0** (30733 parole): variazione media 0,732, soffitto 0,841.
- alberi: pezzi: 4 foglie 0,115 (0,102; 0,127), 8 foglie 0,163 (0,147; 0,176), 16 foglie 0,185 (0,167; 0,199), 32 foglie 0,209 (0,191; 0,224); eco: 4 foglie 0,118 (0,104; 0,129), 8 foglie 0,127 (0,113; 0,138), 16 foglie 0,132 (0,117; 0,143), 32 foglie 0,132 (0,118; 0,144); pezzi+eco: 4 foglie 0,115 (0,102; 0,127), 8 foglie 0,163 (0,147; 0,176), 16 foglie 0,184 (0,166; 0,199), 32 foglie 0,208 (0,190; 0,223).
- migliore tabella di pezzi: posto nella riga + primo (0,192 (0,177; 0,204)); migliore regola di eco: eco: classe piu' vicina e posto nella riga (0,105 (0,091; 0,116)).
- letture: albero16_pezzi: zona grigia; albero16_pezzi_contro_ia13: come ia13 (entro 0,05); albero16_eco: zona grigia; albero16_pezzi_e_eco: zona grigia; migliore_tabella_pezzi: zona grigia; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: zona grigia.

**P2, mem_k1** (30733 parole): variazione media 0,034, soffitto 0,798.
- alberi: pezzi: 4 foglie 0,023 (0,012; 0,035), 8 foglie 0,036 (0,025; 0,044), 16 foglie 0,041 (0,030; 0,051), 32 foglie 0,044 (0,032; 0,054); eco: 4 foglie 0,025 (0,016; 0,034), 8 foglie 0,036 (0,025; 0,045), 16 foglie 0,039 (0,027; 0,049), 32 foglie 0,038 (0,025; 0,050); pezzi+eco: 4 foglie 0,025 (0,016; 0,034), 8 foglie 0,037 (0,027; 0,046), 16 foglie 0,040 (0,028; 0,052), 32 foglie 0,043 (0,030; 0,054).
- migliore tabella di pezzi: posto nella riga + primo (0,036 (0,030; 0,043)); migliore regola di eco: eco: classe di distanza (uguale, a una modifica) (0,018 (0,014; 0,021)).
- letture: albero16_pezzi: poco; albero16_pezzi_contro_ia13: meno spiegabile di ia13; albero16_eco: poco; albero16_pezzi_e_eco: poco; migliore_tabella_pezzi: poco; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P2, mem_k2** (30733 parole): variazione media 0,011, soffitto 0,759.
- alberi: pezzi: 4 foglie 0,014 (0,007; 0,021), 8 foglie 0,015 (0,007; 0,024), 16 foglie 0,015 (0,006; 0,024), 32 foglie 0,016 (0,006; 0,026); eco: 4 foglie 0,018 (0,011; 0,025), 8 foglie 0,018 (0,010; 0,027), 16 foglie 0,021 (0,011; 0,031), 32 foglie 0,020 (0,009; 0,031); pezzi+eco: 4 foglie 0,018 (0,011; 0,025), 8 foglie 0,014 (0,007; 0,022), 16 foglie 0,016 (0,007; 0,025), 32 foglie 0,019 (0,008; 0,029).
- migliore tabella di pezzi: posto nella riga + primo (0,015 (0,009; 0,022)); migliore regola di eco: eco: classe di distanza (uguale, a una modifica) (0,013 (0,009; 0,016)).
- letture: albero16_pezzi: poco; albero16_pezzi_contro_ia13: meno spiegabile di ia13; albero16_eco: poco; albero16_pezzi_e_eco: poco; migliore_tabella_pezzi: poco; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P2, mem_senza_prec** (30733 parole): variazione media -0,001, soffitto 0,723.
- alberi: pezzi: 4 foglie 0,009 (0,002; 0,016), 8 foglie 0,013 (0,005; 0,021), 16 foglie 0,012 (0,002; 0,022), 32 foglie 0,007 (-0,003; 0,018); eco: 4 foglie 0,017 (0,009; 0,025), 8 foglie 0,025 (0,015; 0,034), 16 foglie 0,025 (0,014; 0,036), 32 foglie 0,024 (0,013; 0,036); pezzi+eco: 4 foglie 0,017 (0,009; 0,025), 8 foglie 0,019 (0,009; 0,029), 16 foglie 0,024 (0,013; 0,035), 32 foglie 0,022 (0,009; 0,034).
- migliore tabella di pezzi: posto nella riga + primo (0,009 (0,001; 0,017)); migliore regola di eco: eco: classe di distanza (uguale, a una modifica) (0,014 (0,009; 0,019)).
- letture: albero16_pezzi: poco; albero16_pezzi_contro_ia13: meno spiegabile di ia13; albero16_eco: poco; albero16_pezzi_e_eco: poco; migliore_tabella_pezzi: poco; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P1, ordine** (30733 parole): variazione media 0,920, soffitto 0,672.
- alberi: pezzi: 4 foglie 0,090 (0,078; 0,101), 8 foglie 0,125 (0,110; 0,138), 16 foglie 0,182 (0,166; 0,195), 32 foglie 0,216 (0,201; 0,230); eco: 4 foglie 0,043 (0,035; 0,050), 8 foglie 0,047 (0,038; 0,054), 16 foglie 0,049 (0,040; 0,057), 32 foglie 0,049 (0,039; 0,057); pezzi+eco: 4 foglie 0,090 (0,078; 0,101), 8 foglie 0,125 (0,110; 0,138), 16 foglie 0,182 (0,166; 0,195), 32 foglie 0,216 (0,201; 0,230).
- migliore tabella di pezzi: ultimo(prec) -> primi2 (0,173 (0,160; 0,183)); migliore regola di eco: eco: classe piu' vicina e posto nella riga (0,003 (0,001; 0,005)).
- letture: albero16_pezzi: zona grigia; albero16_pezzi_contro_ia13: come ia13 (entro 0,05); albero16_eco: poco; albero16_pezzi_e_eco: zona grigia; migliore_tabella_pezzi: zona grigia; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P1, mem_k0** (30733 parole): variazione media 0,499, soffitto nan.
- alberi: pezzi: 4 foglie 0,093 (0,082; 0,105), 8 foglie 0,110 (0,097; 0,123), 16 foglie 0,114 (0,099; 0,128), 32 foglie 0,124 (0,109; 0,140); eco: 4 foglie 0,079 (0,071; 0,089), 8 foglie 0,088 (0,079; 0,097), 16 foglie 0,097 (0,087; 0,106), 32 foglie 0,100 (0,089; 0,109); pezzi+eco: 4 foglie 0,093 (0,082; 0,105), 8 foglie 0,110 (0,097; 0,123), 16 foglie 0,112 (0,098; 0,126), 32 foglie 0,126 (0,110; 0,140).
- migliore tabella di pezzi: posto nella riga + primo (0,095 (0,084; 0,104)); migliore regola di eco: eco: classe piu' vicina e posto nella riga (0,073 (0,063; 0,083)).
- letture: albero16_pezzi: zona grigia; albero16_pezzi_contro_ia13: meno spiegabile di ia13; albero16_eco: zona grigia; albero16_pezzi_e_eco: zona grigia; migliore_tabella_pezzi: zona grigia; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P1, mem_k1** (30733 parole): variazione media 0,035, soffitto nan.
- alberi: pezzi: 4 foglie 0,018 (0,009; 0,027), 8 foglie 0,018 (0,008; 0,027), 16 foglie 0,017 (0,006; 0,026), 32 foglie 0,015 (0,004; 0,025); eco: 4 foglie 0,017 (0,008; 0,025), 8 foglie 0,025 (0,016; 0,034), 16 foglie 0,031 (0,020; 0,040), 32 foglie 0,030 (0,019; 0,041); pezzi+eco: 4 foglie 0,017 (0,008; 0,025), 8 foglie 0,028 (0,018; 0,037), 16 foglie 0,024 (0,014; 0,034), 32 foglie 0,025 (0,013; 0,035).
- migliore tabella di pezzi: posto nella riga + primo (0,013 (0,006; 0,019)); migliore regola di eco: eco: classe di distanza (uguale, a una modifica) (0,017 (0,014; 0,020)).
- letture: albero16_pezzi: poco; albero16_pezzi_contro_ia13: meno spiegabile di ia13; albero16_eco: poco; albero16_pezzi_e_eco: poco; migliore_tabella_pezzi: poco; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

**P1, mem_k2** (30733 parole): variazione media 0,010, soffitto nan.
- alberi: pezzi: 4 foglie 0,005 (-0,002; 0,011), 8 foglie 0,002 (-0,005; 0,009), 16 foglie -0,001 (-0,009; 0,007), 32 foglie -0,006 (-0,015; 0,002); eco: 4 foglie 0,008 (0,000; 0,014), 8 foglie 0,014 (0,005; 0,022), 16 foglie 0,011 (0,001; 0,020), 32 foglie 0,010 (-0,000; 0,020); pezzi+eco: 4 foglie 0,007 (-0,000; 0,013), 8 foglie 0,009 (0,001; 0,016), 16 foglie -0,001 (-0,011; 0,008), 32 foglie -0,003 (-0,015; 0,008).
- migliore tabella di pezzi: la parola da sola: primo, ultimo, lunghezza (0,005 (0,001; 0,008)); migliore regola di eco: eco: classe di distanza (uguale, a una modifica) (0,012 (0,009; 0,016)).
- letture: albero16_pezzi: poco; albero16_pezzi_contro_ia13: meno spiegabile di ia13; albero16_eco: poco; albero16_pezzi_e_eco: poco; migliore_tabella_pezzi: poco; migliore_tabella_pezzi_contro_ia13: meno spiegabile di ia13; migliore_tabella_eco: poco.

## Letture preregistrate

- **A_dove_guarda_eco:** {"stessa riga": "come il caso (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "1-3 righe sopra": "come il caso (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "vicina (stessa riga e 1-3 sopra)": "come il caso (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "lontana (4 o piu' righe sopra)": "come il caso (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "pagina precedente": "come il caso (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}
- **A_mappa:** {"inizio parola (si indovina il primo glifo)": {"coda pagina precedente": "meno del caso", "testa di pagina": "meno del caso", "testa di riga": "piu' del caso", "stessa riga: parola da scrivere (segni gia' scritti)": "zona grigia", "stessa riga: parola prima": "piu' del caso", "stessa riga: seconda prima": "piu' del caso", "stessa riga: altre": "piu' del caso", "1 riga sopra": "piu' del caso", "2 righe sopra": "piu' del caso", "3 righe sopra": "come il caso", "4-5 righe sopra": "zona grigia", "6-9 righe sopra": "meno del caso", "10-19 righe sopra": "meno del caso", "20+ righe sopra": "meno del caso", "prime due righe della pagina (da riga 4)": "meno del caso"}, "dentro la parola": {"coda pagina precedente": "meno del caso", "testa di pagina": "zona grigia", "testa di riga": "piu' del caso", "stessa riga: parola da scrivere (segni gia' scritti)": "piu' del caso", "stessa riga: parola prima": "piu' del caso", "stessa riga: seconda prima": "piu' del caso", "stessa riga: altre": "piu' del caso", "1 riga sopra": "piu' del caso", "2 righe sopra": "piu' del caso", "3 righe sopra": "come il caso", "4-5 righe sopra": "zona grigia", "6-9 righe sopra": "meno del caso", "10-19 righe sopra": "meno del caso", "20+ righe sopra": "meno del caso", "prime due righe della pagina (da riga 4)": "meno del caso"}, "fine parola (spazio o a capo)": {"coda pagina precedente": "meno del caso", "testa di pagina": "come il caso", "testa di riga": "piu' del caso", "stessa riga: parola da scrivere (segni gia' scritti)": "piu' del caso", "stessa riga: parola prima": "piu' del caso", "stessa riga: seconda prima": "piu' del caso", "stessa riga: altre": "piu' del caso", "1 riga sopra": "piu' del caso", "2 righe sopra": "piu' del caso", "3 righe sopra": "come il caso", "4-5 righe sopra": "zona grigia", "6-9 righe sopra": "meno del caso", "10-19 righe sopra": "meno del caso", "20+ righe sopra": "meno del caso", "prime due righe della pagina (da riga 4)": "meno del caso"}}
- **B_bit:** {"senza_prec": "non dipende (maschera sulle righe: include l effetto di un contesto mai visto)", "k0": "dipende (maschera sulle righe: include l effetto di un contesto mai visto)", "k1": "dipende (maschera sulle righe: include l effetto di un contesto mai visto)", "k2": "non dipende (maschera sulle righe: include l effetto di un contesto mai visto)", "k4": "non dipende (maschera sulle righe: include l effetto di un contesto mai visto)", "k8": "non dipende (maschera sulle righe: include l effetto di un contesto mai visto)", "eco_via": "conta", "eco_uguale_via": "conta"}
- **B_caduta_per_eco:** "conta"
- **B_memoria_entro_k_righe:** 1
- **B_libri:** {"K0": "l'eco cala ma resta", "K1": "l'eco cala ma resta", "K3": "l'eco non cambia", "SP": "l'eco non cambia"}
- **C_regole:** {"P2 ordine": {"albero16_pezzi": "zona grigia", "albero16_pezzi_contro_ia13": "come ia13 (entro 0,05)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "zona grigia", "migliore_tabella_pezzi": "zona grigia", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P2 mem_k0": {"albero16_pezzi": "zona grigia", "albero16_pezzi_contro_ia13": "come ia13 (entro 0,05)", "albero16_eco": "zona grigia", "albero16_pezzi_e_eco": "zona grigia", "migliore_tabella_pezzi": "zona grigia", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "zona grigia"}, "P2 mem_k1": {"albero16_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P2 mem_k2": {"albero16_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P2 mem_senza_prec": {"albero16_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P1 ordine": {"albero16_pezzi": "zona grigia", "albero16_pezzi_contro_ia13": "come ia13 (entro 0,05)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "zona grigia", "migliore_tabella_pezzi": "zona grigia", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P1 mem_k0": {"albero16_pezzi": "zona grigia", "albero16_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_eco": "zona grigia", "albero16_pezzi_e_eco": "zona grigia", "migliore_tabella_pezzi": "zona grigia", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P1 mem_k1": {"albero16_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}, "P1 mem_k2": {"albero16_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "albero16_pezzi_e_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_pezzi_contro_ia13": "meno spiegabile di ia13 (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)", "migliore_tabella_eco": "poco (con riserva: sensibilità dello strumento non provata, il controllo con l eco piantata non è riuscito)"}}

## Tempi (minuti per lavoro)

- leggi: 15 lavori, media 1.4, massimo 2.2, totale 21.5.
- sint: 2 lavori, media 64.8, massimo 72.5, totale 129.5.
- libro: 21 lavori, media 2.8, massimo 4.3, totale 59.5.
- M: 26 lavori, media 0.4, massimo 0.4, totale 9.7.
- D: 5 lavori, media 0.1, massimo 0.1, totale 0.6.
- regole: 2 lavori, media 0.6, massimo 0.7, totale 1.2.
