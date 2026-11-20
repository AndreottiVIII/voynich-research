# ia08 — perche' la rete se ne accorge

Prima riga di lettura (soglie nella preregistrazione `preregistrazioni/ia08.md`). Le differenze sono "v21 meno vere" (media sui 10 libri), in bit per segno salvo dove detto; intervalli al 95% col bootstrap sulle pagine.

**H2, parole nuove:** ZONA GRIGIA. Quota di parole nuove (per token): vere 15.2%, v21 14.5% (differenza -0.007, nullo 97,5% 0.021); la parte "glifi di parole nuove" porta 36.5% della differenza (intervallo 18.2%-50.8%).
**H1, legami fra parole:** ZONA GRIGIA. Informazione mutua (ultimo glifo, primo della parola dopo) dovuta all'ordine: vere 0.188 bit (0.174-0.203), v21 0.185 (0.179-0.192), rapporto 0.98; sorpresa all'inizio delle parole note dopo una parola nota: +0.203 bit (nullo 0.083; ctrl:parole +0.656). Braccio informazione mutua: no; braccio rete: si.
**H3, dove cadono i picchi:** LETTO. Segni sopra la soglia: vere 5.0%, v21 6.4% (eccesso +0.0136, nullo 0.0041).
  - glifi di parole nuove: 49.5% dell'eccesso (42.7%-55.5%) -> zona grigia
  - primo glifo di parole note (non a inizio riga): 26.0% dell'eccesso (22.0%-30.9%) -> zona grigia
  - primo glifo di parole note a inizio riga: 1.3% dell'eccesso (0.2%-2.4%) -> no
  - glifi interni di parole note: 17.2% dell'eccesso (12.8%-22.1%) -> no
  - spazi e a capo: 6.0% dell'eccesso (3.5%-8.4%) -> no

## Controlli

- positivo H2, ctrl:nuove (15% delle parole cambiate in parole che non esistono): quota della differenza nelle parole nuove 143.7% (soglia 0.50), quota di parole nuove +0.126 (soglia 0.06): SUPERATO
- positivo H1, rete, ctrl:parole: sorpresa al primo glifo delle parole note dopo una nota +0.656 (97,5% del nullo 0.083): SUPERATO (condizione per il braccio rete di H1); differenza totale +0.222 (nullo 0.065): sopra il nullo (solo descrittivo)
- positivo e negativo H1 (informazione mutua) su latino: legami piantati 1.408 bit (soglia 0.10), latino vero 0.041 bit (intervallo 0.020-0.055, soglia 0.010): SUPERATO; due serie di rimescolamenti dello stesso testo, differenza -0.0019 (banda 0.01): SUPERATO
- sensibilita: differenza totale del v21 +0.143 bit per segno, 97,5% del nullo (200 divisioni a caso delle pagine vere) 0.065, rapporto richiesto almeno 2: SUPERATO
- quota di segni sopra la soglia nelle vere: 5.0% (attesa 4.5%-5.5%): SUPERATO
- riproduzione di ia01 (non e' una soglia): 10 modelli confrontati, differenza massima della perdita di validazione 0.00000, dei passi 0, dei bit medi per pagina 0.0001 (media 0.00003 su 4848 pagine)
- bit medi per segno, media sulle pagine (come ia01): vere 2.040, v21 2.172, differenza +0.1320 (ia01: +0.1320)

## Scomposizione della differenza v21 meno vere (bit per segno, tutti i segni insieme)

Quota = peso della parte sui segni; costo = bit per segno nella parte. La differenza della parte e' la somma di un effetto quota (cambia quanti segni ci sono in quella parte) e di un effetto costo (cambia quanto costano); i due effetti si calcolano col punto medio fra vere e v21 e sommano esattamente alla differenza. Le colonne ctrl: sono le stesse quote della differenza per i due controlli.

| parte | quota segni vere | quota segni v21 | costo vere | costo v21 | differenza (IC 95%) | quota della differenza (IC) | effetto quota | effetto costo | ctrl:parole | ctrl:nuove |
|---|---|---|---|---|---|---|---|---|---|---|
| glifi di parole nuove | 16.4% | 15.7% | 3.016 | 3.483 | +0.0523 (+0.0211; +0.0823) | 36.5% (18.2%-50.8%) | -0.0225 | +0.0749 | 16.0% | 143.7% |
| primo glifo di parole note (non a inizio riga) | 13.9% | 14.0% | 2.922 | 3.122 | +0.0307 (+0.0229; +0.0375) | 21.4% (15.1%-29.1%) | +0.0027 | +0.0280 | 37.0% | -16.2% |
| primo glifo di parole note a inizio riga | 1.6% | 1.6% | 3.298 | 3.400 | +0.0004 (-0.0020; +0.0025) | 0.3% (-1.4%-1.8%) | -0.0012 | +0.0016 | 12.8% | -2.1% |
| glifi interni di parole note | 49.8% | 50.5% | 1.675 | 1.742 | +0.0459 (+0.0354; +0.0560) | 32.0% (23.1%-43.0%) | +0.0125 | +0.0333 | 18.8% | -35.2% |
| spazi e a capo | 18.3% | 18.2% | 0.813 | 0.894 | +0.0140 (+0.0088; +0.0193) | 9.8% (6.5%-12.6%) | -0.0008 | +0.0148 | 15.5% | 9.8% |
| totale | | | 1.936 | 2.080 | +0.1434 (+0.1149; +0.1712) | 100% | -0.0093 (-0.0216; +0.0019) | +0.1527 (+0.1315; +0.1731) | +0.2216 | +0.3457 |

Distanza fra i profili (somma delle differenze assolute fra le quote della differenza): v21 da ctrl:parole 0.67, v21 da ctrl:nuove 2.14 (piu' piccola = piu' simile; descrittivo).

## H2: parole nuove

| misura | vere | v21 | differenza (IC 95%) | nullo 97,5% | ctrl:nuove |
|---|---|---|---|---|---|
| quota di parole nuove (per token) | 0.1521 | 0.1447 | -0.0074 (-0.0160; +0.0014) | 0.0208 | +0.1257 |
| quota di parole assenti da tutte le altre pagine vere | 0.1379 | 0.1405 | +0.0026 (-0.0060; +0.0108) | 0.0190 | +0.1276 |
| bit per segno nelle parole assenti | 3.0512 | 3.5039 | +0.4526 (+0.4055; +0.4964) | 0.0953 | +0.7959 |

Costo per segno delle parole nuove: vere 3.016, v21 3.483 bit (differenza +0.467).

## H3: segni sopra la soglia dei picchi (95o percentile delle vere, per modello)

| parte | picchi nella parte vere | v21 | parte dei picchi vere | parte dei picchi v21 | eccesso (IC 95%) | quota dell'eccesso (IC) |
|---|---|---|---|---|---|---|
| glifi di parole nuove | 14.4% | 19.3% | 47.2% | 47.7% | +0.0067 (+0.0051; +0.0084) | 49.5% (42.7%-55.5%) |
| primo glifo di parole note (non a inizio riga) | 5.7% | 8.2% | 16.0% | 18.1% | +0.0035 (+0.0030; +0.0041) | 26.0% (22.0%-30.9%) |
| primo glifo di parole note a inizio riga | 6.5% | 7.8% | 2.1% | 1.9% | +0.0002 (+0.0000; +0.0003) | 1.3% (0.2%-2.4%) |
| glifi interni di parole note | 2.8% | 3.2% | 27.4% | 25.2% | +0.0023 (+0.0017; +0.0029) | 17.2% (12.8%-22.1%) |
| spazi e a capo | 2.0% | 2.5% | 7.3% | 7.0% | +0.0008 (+0.0005; +0.0012) | 6.0% (3.5%-8.4%) |

## H1: informazione mutua fra ultimo glifo di una parola e primo della successiva (stessa riga), in bit

| testo | coppie | MI grezza | a caso (permutazioni) | corretta | rimescolato nella riga | dovuta all'ordine g (IC 95%) |
|---|---|---|---|---|---|---|
| vere | 30595 | 0.2065 | 0.0098 | 0.1967 | 0.0182 | +0.1882 (+0.1738; +0.2030) |
| a13 | 31366 | 0.2066 | 0.0097 | 0.1969 | 0.0201 | +0.1865 (+0.1773; +0.1974) |
| a14 | 31124 | 0.2081 | 0.0102 | 0.1979 | 0.0179 | +0.1902 (+0.1802; +0.2011) |
| a15 | 32014 | 0.1970 | 0.0097 | 0.1873 | 0.0166 | +0.1804 (+0.1709; +0.1896) |
| a16 | 31506 | 0.2028 | 0.0100 | 0.1928 | 0.0179 | +0.1849 (+0.1728; +0.1977) |
| a17 | 31758 | 0.1986 | 0.0100 | 0.1887 | 0.0168 | +0.1819 (+0.1713; +0.1935) |
| a18 | 31550 | 0.2060 | 0.0099 | 0.1961 | 0.0180 | +0.1879 (+0.1780; +0.1985) |
| a19 | 34022 | 0.1967 | 0.0093 | 0.1873 | 0.0171 | +0.1795 (+0.1705; +0.1901) |
| a20 | 32640 | 0.2007 | 0.0099 | 0.1908 | 0.0175 | +0.1832 (+0.1730; +0.1942) |
| a21 | 32235 | 0.2044 | 0.0100 | 0.1944 | 0.0191 | +0.1853 (+0.1742; +0.1976) |
| a22 | 32236 | 0.2053 | 0.0095 | 0.1958 | 0.0177 | +0.1876 (+0.1777; +0.1983) |

v21 (media dei libri): g +0.1847 (+0.1789; +0.1915), errore standard fra i libri 0.0011; vere meno v21 +0.0035 (-0.0105; +0.0164); rapporto v21/vere 0.98 (intervallo 0.91-1.05). Nullo (vere divise a caso in due, differenza di g): sd 0.0150, 97,5% del valore assoluto 0.0329.

Altre coppie di glifi (descrittivo, nessuna soglia): g nelle vere, nel v21 e differenza.

| coppia | g vere | g v21 | vere meno v21 (IC 95%) |
|---|---|---|---|
| pri_pri | +0.0519 | +0.0375 | +0.0144 (+0.0075; +0.0206) |
| ult_ult | +0.0080 | -0.0005 | +0.0086 (+0.0053; +0.0117) |

Latino (controllo): legami piantati g +1.4079, latino vero g +0.0412 (+0.0198; +0.0547).

## H1 con la rete: sorpresa all'inizio delle parole note

| misura | vere | v21 | differenza (IC 95%) | nullo 97,5% | ctrl:parole |
|---|---|---|---|---|---|
| primo glifo di parola nota dopo una parola nota | 2.905 | 3.108 | +0.2032 (+0.1674; +0.2371) | 0.0832 | +0.6557 |
| primo glifo di parola nota dopo una parola nuova | 3.032 | 3.220 | +0.1878 (+0.1295; +0.2400) | 0.1305 | +0.5228 |
| primo glifo di parola nota, tutte (non a inizio riga) | 2.922 | 3.122 | +0.2004 (+0.1662; +0.2335) | 0.0835 | +0.6381 |

## Parole note per frequenza (nelle pagine di addestramento della piega)

| classe | quota delle parole note vere | v21 | bit al primo glifo vere | v21 | bit dentro la parola vere | v21 |
|---|---|---|---|---|---|---|
| 1 volta | 6.1% | 3.0% | 3.212 | 3.333 | 2.423 | 2.491 |
| 2-4 volte | 9.7% | 12.2% | 3.295 | 3.407 | 2.193 | 2.341 |
| 5-19 volte | 19.1% | 20.1% | 3.225 | 3.331 | 1.998 | 2.066 |
| 20 o piu | 65.1% | 64.7% | 2.810 | 3.037 | 1.360 | 1.418 |

## Posizione e stato della parola: quota dei segni e bit per segno

| casella | quota segni vere | v21 | bit vere | v21 | differenza dei bit |
|---|---|---|---|---|---|
| riga|nota | 1.6% | 1.6% | 3.298 | 3.400 | +0.103 |
| riga|nuova | 0.6% | 0.5% | 3.059 | 3.427 | +0.368 |
| ini|nota | 13.9% | 14.0% | 2.922 | 3.122 | +0.200 |
| ini|nuova | 2.2% | 2.1% | 3.433 | 3.799 | +0.366 |
| dentro|nota | 49.8% | 50.5% | 1.675 | 1.742 | +0.066 |
| dentro|nuova | 13.6% | 13.0% | 2.946 | 3.434 | +0.489 |
| sp|nota | 13.9% | 14.0% | 0.576 | 0.609 | +0.033 |
| sp|nuova | 2.2% | 2.1% | 0.797 | 1.181 | +0.383 |
| nl|nota | 1.6% | 1.6% | 2.484 | 2.663 | +0.178 |
| nl|nuova | 0.5% | 0.5% | 1.958 | 2.064 | +0.106 |

## Per libro (differenza v21 meno vere)

| libro | bit per segno | picchi | quota di parole nuove | inizio note dopo nota | parti: nuove / inizio_note / riga_note / interno_note / spazi_acapo |
|---|---|---|---|---|---|
| a13 | +0.1239 | +0.0119 | -0.0136 | +0.1863 | +0.027 / +0.030 / +0.002 / +0.051 / +0.013 |
| a14 | +0.1632 | +0.0150 | -0.0011 | +0.2150 | +0.077 / +0.030 / -0.000 / +0.039 / +0.018 |
| a15 | +0.1482 | +0.0139 | -0.0065 | +0.2180 | +0.056 / +0.032 / +0.001 / +0.045 / +0.014 |
| a16 | +0.1425 | +0.0134 | -0.0071 | +0.2109 | +0.051 / +0.031 / +0.001 / +0.047 / +0.012 |
| a17 | +0.1534 | +0.0143 | -0.0110 | +0.2112 | +0.044 / +0.035 / +0.001 / +0.055 / +0.018 |
| a18 | +0.1404 | +0.0132 | -0.0057 | +0.1772 | +0.059 / +0.027 / +0.000 / +0.042 / +0.013 |
| a19 | +0.1300 | +0.0127 | -0.0114 | +0.2093 | +0.037 / +0.036 / -0.001 / +0.049 / +0.010 |
| a20 | +0.1446 | +0.0146 | -0.0027 | +0.2101 | +0.067 / +0.028 / -0.001 / +0.038 / +0.013 |
| a21 | +0.1512 | +0.0144 | -0.0065 | +0.2080 | +0.059 / +0.030 / +0.001 / +0.048 / +0.014 |
| a22 | +0.1365 | +0.0127 | -0.0083 | +0.1862 | +0.047 / +0.028 / +0.001 / +0.046 / +0.014 |

Modelli del testo: bit per segno sulla validazione 1.956; passi medi 1510.
