# IA24 (ia24) — Che cosa distingue le parole nuove del Voynich da quelle degli imitatori

Preregistrazione: `preregistrazioni/ia24.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, nuove nuove-1, echi echi-1, gradini gradini-1, sklearn 1.9.1.

## Controlli dei giudici

- Giudici del paper, positivo: AUC 0,988, soglia ≥ 0,95 → sì. Negativo: giudice 1 0,506, giudice 2 0,503 → sì.
- K, positivo: parole 0,982, e192 0,935 → sì. Negativo: 0,499 → sì. K vede il v21 (AUC 0,766) → sì.
- A (riportato, non decide), positivo: parole 0,986, e192 0,958 → sì. Negativo: 0,484 → sì.

## Controlli di sensibilità (testi sintetici)

Testo con ritocchi piantati (fogli tenuti fuori della piega 0): quota di parole nuove 0,255; fra le nuove a 1 modifica da una parola nota 0,901, a <= 2 0,993.
- M1: validazione 2,511; bit per segno sulle parole nuove 3,264, sulle note 2,236; nuove scritte 0,277 (a 1 modifica 0,898).
- W1: guadagno su M1 sulle parole piantate 0,097 bit per segno (soglia >= 0,100; sulle nuove -0,005), sulle note -0,089 rispetto a M1 (al massimo +0,100); quota a posteriori del lessico sulle nuove 0,842 (>= 0,500); nuove scritte 0,217, scarto dal piantato 0,038 (<= 0,050; M1 0,022) -> NO.
- W2: guadagno su M1 sulle parole piantate 0,105 bit per segno (soglia >= 0,100; sulle nuove -0,006), sulle note -0,088 rispetto a M1 (al massimo +0,100); quota a posteriori del lessico sulle nuove 0,847 (>= 0,500); nuove scritte 0,221, scarto dal piantato 0,035 (<= 0,050; M1 0,022) -> sì.
Testo con parole a caselle piantate: quota di nuove 0,279, conformi alla grammatica 0,733.
- M1: validazione 2,561; bit per segno sulle parole nuove 3,188, sulle note 2,262; nuove scritte conformi 0,528.
- W3: guadagno su M1 sulle parole piantate -0,068 bit per segno (soglia >= -0,020; sulle nuove -0,066), sulle note 0,021 rispetto a M1 (al massimo +0,100); porta aperta 0,840 sulle piantate contro 0,144 sulle altre (differenza >= 0,100); nuove scritte conformi 0,379 -> NO.
- Testo senza niente di piantato: W1 guadagno in validazione 0,071, sulle nuove -0,293 (nuove <= 0,100: sì); W2 guadagno in validazione 0,061, sulle nuove -0,330 (nuove <= 0,100: sì); W3 guadagno in validazione -0,015, sulle nuove -0,094 (<= 0,020 per W3: sì).

## Modelli (bit per segno; medie sui 10 modelli di ogni tipo)

| tipo | parametri | validazione | fuori piega | epoche scelte | al massimo | massa del lessico | posteriori del lessico: nuove / note | miscela (libero, 0, 1, 2 modifiche) | minuti per modello |
|---|---|---|---|---|---|---|---|---|---|
| W1 | 668469 | 1,970 ± 0,033 | 1,936 ± 0,020 | 20,3 | 0 | 0,270 | 0,054 / 0,305 | 0,730, 0,258, 0,012, 0,000 | 29.7 |
| W2 | 768150 | 1,979 ± 0,035 | 1,948 ± 0,019 | 17,2 | 0 | 0,337 | 0,059 / 0,328 | 0,663, 0,264, 0,015, 0,000 | 32.8 |
| W3 | 665741 | 1,969 ± 0,033 | 1,941 ± 0,020 | 29,1 | 0 | — | — / — | — | 16.1 |
| M1 (cache) | — | 1,965 ± 0,031 | 1,940 ± 0,019 | — | — | — | — | — | — |
| M5 (cache) | — | 1,960 ± 0,032 | 1,926 ± 0,022 | — | — | — | — | — | — |
| E2 (cache) | — | 1,967 ± 0,031 | 1,951 ± 0,019 | — | — | — | — | — | — |

Numeri imparati (medie): W1 [{"kappa": [1.1751, 0.8078], "gamma": [0.3285, 0.8152], "tau": [0.2752, 0.2255, 0.4993]}, {"kappa": [1.1942, 0.8012], "gamma": [0.3073, 0.7801], "tau": [0.2678, 0.2271, 0.5051]}]; W2 [{"kappa": [1.1494, 0.8615], "gamma": [0.3589, 0.82], "tau": [0.296, 0.2472, 0.4568], "beta": [-2.4907, -4.6164, -4.8058, -4.049], "gam_pagina": 0.1072}, {"kappa": [1.1737, 0.8086], "gamma": [0.3214, 0.7605], "tau": [0.2976, 0.2433, 0.4591], "beta": [-2.2462, -4.9608, -5.0835, -4.097], "gam_pagina": 0.1753}]; W3 [{"porta_bias": -1.0466, "porta_peso_norma": 0.7973, "porta_posto": [0.0259, -0.1944, -0.0747]}, {"porta_bias": -1.0587, "porta_peso_norma": 0.8296, "porta_posto": [0.0849, -0.1689, -0.1145]}] (prime due repliche).

## Giudici: libri contro libro vero (AUC, più basso = più vicino al vero)

| libri | n | giudice 1 (e231) | giudice 2 (e266) | K | A (riportato) |
|---|---|---|---|---|---|
| M1 | 10 | 0,785 ± 0,009 | 0,841 ± 0,007 | 0,774 ± 0,005 | 0,675 ± 0,009 |
| E2 | 10 | 0,801 ± 0,012 | 0,864 ± 0,004 | 0,797 ± 0,007 | 0,695 ± 0,007 |
| M5 | 10 | 0,782 ± 0,008 | 0,799 ± 0,007 | 0,797 ± 0,007 | 0,707 ± 0,006 |
| W1 | 10 | 0,779 ± 0,005 | 0,836 ± 0,004 | 0,664 ± 0,007 | 0,602 ± 0,012 |
| W2 | 10 | 0,789 ± 0,015 | 0,855 ± 0,010 | 0,796 ± 0,005 | 0,786 ± 0,005 |
| W3 | 10 | 0,832 ± 0,009 | 0,861 ± 0,008 | 0,859 ± 0,004 | 0,803 ± 0,007 |
| v21 | 10 | 0,554 ± 0,004 (paper) | 0,601 ± 0,005 (paper) | 0,766 ± 0,005 | 0,746 ± 0,005 |

Repliche diverse (più di 2 errori): M1: e231 NO, e266 NO; E2: e231 sì, e266 NO; M5: e231 NO, e266 NO; W1: e231 NO, e266 NO; W2: e231 sì, e266 sì; W3: e231 NO, e266 NO.

## Struttura (media ± errore standard sui libri)

| testo | copia netta (bit per parola) | quota locale Λ | contatto ultimo→primo glifo | ordine delle famiglie D | G9 vocabolario della pagina | bordi: inizio riga | bordi: fine riga | quota di parole nuove | costo di forma delle parole nuove (bit per glifo) |
|---|---|---|---|---|---|---|---|---|---|
| **vero** | 0,1138 | 0,2074 | 0,1884 | 0,1444 | 0,0402 | 0,0790 | 0,0475 | 0,1530 | 3,4786 |
| M1 (10 libri) | 0,0360 ± 0,0016 | 0,0538 ± 0,0368 | 0,1891 ± 0,0025 | 0,1486 ± 0,0017 | 0,0245 ± 0,0006 | 0,0837 ± 0,0015 | 0,0457 ± 0,0007 | 0,1472 ± 0,0015 | 3,7459 ± 0,0062 |
| E2 (10 libri) | 0,1134 ± 0,0079 | 0,3605 ± 0,0150 | 0,1796 ± 0,0083 | 0,1432 ± 0,0081 | 0,0259 ± 0,0007 | 0,0803 ± 0,0012 | 0,0449 ± 0,0006 | 0,1460 ± 0,0023 | 3,8170 ± 0,0136 |
| M5 (10 libri) | 0,1416 ± 0,0059 | 0,2362 ± 0,0111 | 0,1578 ± 0,0015 | 0,1078 ± 0,0014 | 0,0316 ± 0,0002 | 0,0760 ± 0,0017 | 0,0417 ± 0,0006 | 0,1725 ± 0,0030 | 3,6971 ± 0,0097 |
| W1 (10 libri) | 0,0296 ± 0,0009 | -0,0697 ± 0,0697 | 0,1612 ± 0,0013 | 0,1328 ± 0,0027 | 0,0256 ± 0,0001 | 0,0802 ± 0,0011 | 0,0509 ± 0,0011 | 0,1295 ± 0,0038 | 3,6711 ± 0,0048 |
| W2 (10 libri) | 0,0990 ± 0,0026 | 0,4234 ± 0,0146 | 0,1582 ± 0,0014 | 0,1119 ± 0,0029 | 0,0237 ± 0,0006 | 0,0713 ± 0,0015 | 0,0414 ± 0,0006 | 0,1530 ± 0,0009 | 3,7450 ± 0,0054 |
| W3 (10 libri) | 0,0457 ± 0,0019 | 0,0150 ± 0,0362 | 0,1677 ± 0,0049 | 0,1371 ± 0,0020 | 0,0285 ± 0,0006 | 0,0695 ± 0,0009 | 0,0465 ± 0,0009 | 0,1580 ± 0,0006 | 3,7547 ± 0,0146 |
| V21 (10 libri) | 0,0548 ± 0,0016 | 0,0906 ± 0,0177 | 0,1850 ± 0,0011 | 0,0898 ± 0,0017 | 0,0392 ± 0,0005 | 0,0777 ± 0,0009 | 0,0414 ± 0,0007 | 0,1430 ± 0,0012 | 3,6608 ± 0,0053 |

## Letture preregistrate

- Validità: giudici del paper sì, K sì, A sì; sensibilità: W1 NO, W2 sì, W3 NO; controlli della fase 0 sì.

### L1: il costo di forma delle parole nuove al vero, senza rompere contatto, D e quota di parole nuove?

**Imitatori con costo di forma al vero: nessuno. Con anche contatto, D e parole nuove al vero: nessuno.**

| tipo | costo di forma | contatto | D | parole nuove | forma al vero | resto al vero | tutti |
|---|---|---|---|---|---|---|---|
| vero | 3,479 | 0,188 | 0,144 | 0,153 | | | |
| M1 | 3,746 | 0,189 ✓ | 0,149 ✓ | 0,147 ✓ | NO | sì | NO |
| E2 | 3,817 | 0,180 ✓ | 0,143 ✓ | 0,146 ✓ | NO | sì | NO |
| M5 | 3,697 | 0,158 | 0,108 | 0,173 | NO | NO | NO |
| W1 | 3,671 | 0,161 | 0,133 | 0,130 | NO | NO | NO |
| W2 | 3,745 | 0,158 | 0,112 | 0,153 ✓ | NO | NO | NO |
| W3 | 3,755 | 0,168 | 0,137 | 0,158 ✓ | NO | NO | NO |

### L2: ogni imitatore contro M1 (bersagli: costo di forma e parole nuove)

| confronto | lettura | misure corrette | misure rotte | sensibilità |
|---|---|---|---|---|
| W1 contro M1 | **corregge ma rompe** | costo di forma delle parole nuove (bit per glifo), giudice K | copia netta (bit per parola), contatto ultimo→primo glifo, ordine delle famiglie D, quota di parole nuove | NON provata (con riserva) |
| W2 contro M1 | **corregge ma rompe** | copia netta (bit per parola), quota di parole nuove | contatto ultimo→primo glifo, ordine delle famiglie D, bordi: fine riga, giudice K | provata |
| W3 contro M1 | **rompe** | copia netta (bit per parola), G9 vocabolario della pagina | contatto ultimo→primo glifo, bordi: inizio riga, giudice 1 (e231), giudice K | NON provata (con riserva) |
| W2 contro E2 | **corregge ma rompe** | quota di parole nuove, costo di forma delle parole nuove (bit per glifo) | quota locale Λ, contatto ultimo→primo glifo, ordine delle famiglie D, G9 vocabolario della pagina, bordi: inizio riga, bordi: fine riga | provata |

### L3: contro il v21

- **Tipo migliore (AUC media di e231, e266, K): W1.**
  - M1: più lontano dal vero del v21 (e231 più lontano (diff. 0,231 ± 0,010); e266 più lontano (diff. 0,240 ± 0,008); K uguale entro l'errore (diff. 0,007 ± 0,007)).
  - E2: più lontano dal vero del v21 (e231 più lontano (diff. 0,247 ± 0,012); e266 più lontano (diff. 0,263 ± 0,007); K più lontano (diff. 0,031 ± 0,009)).
  - M5: più lontano dal vero del v21 (e231 più lontano (diff. 0,228 ± 0,009); e266 più lontano (diff. 0,198 ± 0,009); K più lontano (diff. 0,031 ± 0,008)).
  - W1: solo K scende: possibile giudice amico (K ha una memoria di pagina come l'imitatore), non vale come sì (e almeno due giudici su tre sono "più lontano") (e231 più lontano (diff. 0,225 ± 0,007); e266 più lontano (diff. 0,235 ± 0,007); K più vicino (diff. -0,102 ± 0,009)).
  - W2: più lontano dal vero del v21 (e231 più lontano (diff. 0,235 ± 0,015); e266 più lontano (diff. 0,254 ± 0,011); K più lontano (diff. 0,030 ± 0,007)).
  - W3: più lontano dal vero del v21 (e231 più lontano (diff. 0,278 ± 0,010); e266 più lontano (diff. 0,260 ± 0,010); K più lontano (diff. 0,093 ± 0,006)).

### L4: fase 0 — dove nasce lo scarto delle parole nuove

- Controllo ritocco: differenza 0,792 ± 0,007 → **presente**.
- Controllo caselle: differenza 1,858 ± 0,020 → **presente**.
- Vero contro M1 e E2, ritocco: differenza -0,040 ± 0,007 → **assente**.
- Vero contro M1 e E2, caselle: differenza 0,055 ± 0,020 → **zona grigia**.
- **Esito: zona grigia.**

| misura | vero | v21 | M1 | M5 | E2 | W1 | W2 | W3 | piantato_ritocco | piantato_libero | piantato_caselle |
|---|---|---|---|---|---|---|---|---|---|---|---|
| quota di parole nuove | 0,148 ± 0,004 | 0,143 ± 0,001 | 0,147 ± 0,002 | 0,173 ± 0,003 | 0,146 ± 0,002 | 0,130 ± 0,004 | 0,153 ± 0,001 | 0,158 ± 0,001 | 0,148 ± 0,004 | 0,148 ± 0,004 | 0,148 ± 0,004 |
| nuove a 1 modifica da una parola nota | 0,831 ± 0,006 | 0,735 ± 0,002 | 0,835 ± 0,002 | 0,824 ± 0,003 | 0,851 ± 0,002 | 0,844 ± 0,004 | 0,831 ± 0,002 | 0,842 ± 0,002 | 0,848 ± 0,005 | 0,136 ± 0,006 | 0,438 ± 0,007 |
| a 2 modifiche | 0,136 ± 0,005 | 0,213 ± 0,002 | 0,132 ± 0,002 | 0,135 ± 0,002 | 0,120 ± 0,002 | 0,126 ± 0,003 | 0,134 ± 0,002 | 0,127 ± 0,002 | 0,152 ± 0,005 | 0,341 ± 0,008 | 0,320 ± 0,007 |
| a 3 o piu' | 0,033 ± 0,003 | 0,052 ± 0,001 | 0,033 ± 0,001 | 0,041 ± 0,002 | 0,029 ± 0,001 | 0,030 ± 0,001 | 0,034 ± 0,001 | 0,031 ± 0,001 | 0,000 ± 0,000 | 0,524 ± 0,009 | 0,242 ± 0,007 |
| a 1 modifica da una parola con almeno 5 occorrenze | 0,528 ± 0,009 | 0,349 ± 0,002 | 0,572 ± 0,004 | 0,563 ± 0,003 | 0,602 ± 0,002 | 0,562 ± 0,004 | 0,560 ± 0,003 | 0,591 ± 0,006 | 0,786 ± 0,006 | 0,068 ± 0,004 | 0,279 ± 0,007 |
| a 1 modifica da una delle K piu' frequenti | 0,273 ± 0,008 | 0,148 ± 0,001 | 0,319 ± 0,005 | 0,319 ± 0,002 | 0,360 ± 0,003 | 0,307 ± 0,004 | 0,328 ± 0,002 | 0,348 ± 0,005 | 0,732 ± 0,006 | 0,030 ± 0,003 | 0,168 ± 0,005 |
| a <= 2 modifiche da una delle K piu' frequenti | 0,710 ± 0,007 | 0,579 ± 0,002 | 0,737 ± 0,004 | 0,732 ± 0,002 | 0,763 ± 0,001 | 0,730 ± 0,005 | 0,726 ± 0,002 | 0,753 ± 0,004 | 1,000 ± 0,000 | 0,208 ± 0,007 | 0,510 ± 0,008 |
| lunghezza media (nuove) | 5,887 ± 0,032 | 5,964 ± 0,008 | 5,716 ± 0,008 | 5,882 ± 0,012 | 5,669 ± 0,020 | 5,816 ± 0,020 | 5,857 ± 0,009 | 5,761 ± 0,025 | 4,457 ± 0,024 | 5,887 ± 0,035 | 5,866 ± 0,028 |
| lunghezza media (note) | 4,211 ± 0,029 | 4,242 ± 0,003 | 4,103 ± 0,011 | 4,240 ± 0,006 | 4,208 ± 0,036 | 4,273 ± 0,010 | 4,323 ± 0,010 | 4,204 ± 0,020 | 4,211 ± 0,033 | 4,211 ± 0,031 | 4,211 ± 0,029 |
| JS primo glifo (bit) | 0,037 ± 0,003 | 0,050 ± 0,001 | 0,041 ± 0,000 | 0,039 ± 0,001 | 0,044 ± 0,001 | 0,049 ± 0,001 | 0,043 ± 0,001 | 0,046 ± 0,001 | 0,094 ± 0,003 | 0,204 ± 0,006 | 0,054 ± 0,003 |
| JS glifi interni (bit) | 0,049 ± 0,002 | 0,074 ± 0,001 | 0,052 ± 0,001 | 0,045 ± 0,000 | 0,051 ± 0,001 | 0,043 ± 0,001 | 0,045 ± 0,001 | 0,044 ± 0,000 | 0,093 ± 0,002 | 0,149 ± 0,003 | 0,053 ± 0,002 |
| JS ultimo glifo (bit) | 0,037 ± 0,003 | 0,078 ± 0,001 | 0,036 ± 0,001 | 0,034 ± 0,001 | 0,039 ± 0,001 | 0,035 ± 0,001 | 0,033 ± 0,000 | 0,029 ± 0,001 | 0,146 ± 0,004 | 0,451 ± 0,008 | 0,038 ± 0,003 |
| parola nota + pezzo frequente | 0,540 ± 0,008 | 0,423 ± 0,002 | 0,515 ± 0,004 | 0,499 ± 0,002 | 0,518 ± 0,003 | 0,505 ± 0,004 | 0,500 ± 0,004 | 0,513 ± 0,002 | 0,254 ± 0,006 | 0,037 ± 0,003 | 0,192 ± 0,006 |
| parola nota + pezzo qualsiasi (<= 3 glifi) | 0,920 ± 0,004 | 0,890 ± 0,001 | 0,915 ± 0,001 | 0,905 ± 0,002 | 0,924 ± 0,002 | 0,919 ± 0,003 | 0,912 ± 0,002 | 0,914 ± 0,001 | 0,869 ± 0,005 | 0,387 ± 0,009 | 0,608 ± 0,007 |
| costo di forma (bit per glifo) | 3,479 ± 0,027 | 3,661 ± 0,005 | 3,746 ± 0,006 | 3,697 ± 0,010 | 3,817 ± 0,014 | 3,671 ± 0,005 | 3,745 ± 0,005 | 3,755 ± 0,015 | 7,120 ± 0,039 | 8,925 ± 0,027 | 6,486 ± 0,034 |
| di cui primo glifo | 0,662 ± 0,008 | 0,679 ± 0,001 | 0,690 ± 0,001 | 0,677 ± 0,003 | 0,718 ± 0,002 | 0,684 ± 0,002 | 0,682 ± 0,003 | 0,713 ± 0,002 | 1,276 ± 0,020 | 0,924 ± 0,011 | 0,667 ± 0,005 |
| secondo | 0,523 ± 0,009 | 0,570 ± 0,003 | 0,607 ± 0,003 | 0,595 ± 0,006 | 0,641 ± 0,005 | 0,587 ± 0,005 | 0,604 ± 0,003 | 0,591 ± 0,005 | 1,645 ± 0,027 | 1,390 ± 0,016 | 1,219 ± 0,018 |
| terzo | 0,620 ± 0,012 | 0,616 ± 0,002 | 0,698 ± 0,004 | 0,668 ± 0,003 | 0,705 ± 0,008 | 0,665 ± 0,005 | 0,675 ± 0,003 | 0,679 ± 0,005 | 1,406 ± 0,021 | 1,459 ± 0,013 | 1,183 ± 0,013 |
| dal quarto | 1,552 ± 0,012 | 1,634 ± 0,002 | 1,620 ± 0,004 | 1,623 ± 0,013 | 1,610 ± 0,004 | 1,601 ± 0,010 | 1,655 ± 0,005 | 1,648 ± 0,004 | 2,306 ± 0,031 | 4,238 ± 0,032 | 3,270 ± 0,027 |
| fine parola | 0,121 ± 0,005 | 0,162 ± 0,001 | 0,131 ± 0,002 | 0,135 ± 0,003 | 0,142 ± 0,003 | 0,134 ± 0,002 | 0,128 ± 0,002 | 0,125 ± 0,005 | 0,487 ± 0,010 | 0,915 ± 0,011 | 0,146 ± 0,004 |
| costo sotto le caselle (bit per glifo) | 3,764 ± 0,019 | 3,951 ± 0,003 | 3,806 ± 0,005 | 3,780 ± 0,007 | 3,833 ± 0,011 | 3,772 ± 0,004 | 3,805 ± 0,003 | 3,736 ± 0,004 | 5,289 ± 0,025 | 5,608 ± 0,017 | 3,750 ± 0,010 |

## Copia a memoria e ripetizioni (soglie severe di ia20)

| | 5-grammi | 3-grammi | righe intere (≥ 4 parole) | parole nuove |
|---|---|---|---|---|
| M1 | 0,0000 ± 0,0000 | 0,0077 ± 0,0002 | 0,0000 ± 0,0000 | 0,1508 ± 0,0016 |
| E2 | 0,0000 ± 0,0000 | 0,0077 ± 0,0005 | 0,0000 ± 0,0000 | 0,1500 ± 0,0024 |
| M5 | 0,0000 ± 0,0000 | 0,0059 ± 0,0003 | 0,0000 ± 0,0000 | 0,1768 ± 0,0032 |
| W1 | 0,0000 ± 0,0000 | 0,0066 ± 0,0003 | 0,0000 ± 0,0000 | 0,1326 ± 0,0039 |
| W2 | 0,0000 ± 0,0000 | 0,0055 ± 0,0002 | 0,0000 ± 0,0000 | 0,1565 ± 0,0009 |
| W3 | 0,0000 ± 0,0000 | 0,0073 ± 0,0002 | 0,0000 ± 0,0000 | 0,1623 ± 0,0007 |
| naturale | 0,0000 | 0,0089 | 0,0000 | 0,1530 |
- M1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- E2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- M5: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- W1: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- W2: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.
- W3: 5-grammi → nessuna copia rilevante, righe → nessuna copia rilevante; si avvita: NO; parola uguale alla prima alta: NO; parole nuove nella fascia.

Modi di scrittura delle parole (conti sui libri): W1: libero 259209, lessico0 91857, lessico0_nota 91857, lessico1 4184, lessico1_nota 1912, lessico1_nuova 2272, lessico2 16, lessico2_nuova 13, lessico2_nota 3; W2: libero 225513, lessico0 93954, lessico0_nota 93954, pagina_uguale 14097, pagina_toglie 2579, lessico1 4912, lessico1_nota 2242, lessico1_nuova 2670, pagina_aggiunge 1050, pagina_cambia 1252, lessico2 49, lessico2_nota 14, lessico2_nuova 35.

## Tempi (minuti per lavoro)

- addestra: 30 lavori, media 26.2, massimo 40.0, totale 786.8.
- sens: 9 lavori, media 18.6, massimo 35.2, totale 167.2.
- libro: 30 lavori, media 2.0, massimo 2.5, totale 61.2.
- riflibro: 30 lavori, media 0.3, massimo 0.3, totale 7.6.
- K: 5 lavori, media 0.2, massimo 0.3, totale 1.2.
- M: 71 lavori, media 0.4, massimo 0.5, totale 29.5.
- D: 5 lavori, media 0.2, massimo 0.2, totale 1.1.
- F0: 71 lavori, media 0.1, massimo 0.2, totale 7.6.
