# IA26 (ia26) — Il righello e la taratura

Preregistrazione: `preregistrazioni/ia26.md`.

- Versioni: python 3.12.10, torch 2.15.0+cpu, numpy 2.5.3, sklearn 1.9.1.
- Testi del catalogo (senza il vero): 144.

## Il metro "vero contro vero"

Le pagine vere divise in due metà (per foglio, bilanciate per sezione e lingua): 200 divisioni per le misure di conteggio, 6 per k90 e R_rel; per i giudici, l'AUC con etichette a caso fra pagine vere. Scala = deviazione standard della differenza fra metà (per i giudici, del nullo). Fascia = 2,5-97,5 percentile della differenza.

| misura | vero | scala | fascia | scala / vero |
|---|---|---|---|---|
| copia netta (bit per parola) | 0,1122 | 0,0188 | [-0,0369, 0,0376] | 0,17 |
| quota locale Λ | 0,1371 | 0,0908 | [-0,1986, 0,1660] | 0,66 |
| contatto ultimo→primo glifo | 0,1884 | 0,0133 | [-0,0262, 0,0215] | 0,07 |
| ordine delle famiglie D | 0,1450 | 0,0220 | [-0,0422, 0,0452] | 0,15 |
| G9 vocabolario della pagina | 0,0402 | 0,0025 | [-0,0046, 0,0049] | 0,06 |
| bordi: inizio riga | 0,0790 | 0,0065 | [-0,0145, 0,0123] | 0,08 |
| bordi: fine riga | 0,0475 | 0,0048 | [-0,0095, 0,0083] | 0,10 |
| quota di parole nuove | 0,1484 | 0,0086 | [-0,0172, 0,0161] | 0,06 |
| costo di forma delle parole nuove (bit per glifo) | 3,4786 | 0,0528 | [-0,0933, 0,0948] | 0,02 |
| k90 (segni di contesto) | 2,1511 | 0,4673 | [-0,9160, 0,9160] | 0,22 |
| R_rel (mai viste / viste) | 1,0080 | 0,0306 | [-0,0600, 0,0600] | 0,03 |

| giudice | media del nullo | scala (deviazione standard) | fascia 2,5-97,5 | etichettature |
|---|---|---|---|---|
| giudice 1 (e231) | 0,504 | 0,052 | [0,412, 0,606] | 200 |
| giudice 2 (e266) | 0,504 | 0,052 | [0,406, 0,606] | 200 |
| giudice K | 0,497 | 0,056 | [0,391, 0,590] | 200 |
| giudice A (rete) | 0,493 | 0,056 | [0,372, 0,587] | 200 |
| giudice N (n-grammi, nuovo) | 0,497 | 0,047 | [0,423, 0,579] | 60 |
| giudice KN (Kneser-Ney, nuovo) | 0,497 | 0,056 | [0,403, 0,606] | 200 |

Misure poco informative (scala ≥ 0,5 volte il valore del vero): lam.

## Distanza dal vero dei testi del catalogo (media di min(|z|, 6) su 11 misure e 6 giudici; pesi uguali)

| gruppo | libri | distanza | media quadratica | fuori fascia (|z| > 1,96) | e231 | e266 | K | A | N | KN |
|---|---|---|---|---|---|---|---|---|---|---|
| V21 | 10 | 1,90 ± 0,04 | 2,41 ± 0,04 | 0,45 ± 0,02 | 0,575 ± 0,008 | 0,620 ± 0,009 | 0,766 ± 0,005 | 0,746 ± 0,005 | 0,599 ± 0,011 | 0,677 ± 0,007 |
| TS | 3 | 4,98 ± 0,06 | 12,54 ± 0,74 | 0,82 ± 0,00 | 1,000 ± 0,000 | 1,000 ± 0,000 | 0,997 ± 0,000 | 1,000 ± 0,000 | 1,000 ± 0,000 | 0,999 ± 0,000 |
| NAIBBE | 1 | 5,38 ± — | 9,91 ± — | 0,88 ± — | 1,000 ± — | 1,000 ± — | 0,992 ± — | 0,997 ± — | 1,000 ± — | 0,997 ± — |
| ia07 | 5 | 2,96 ± 0,06 | 3,80 ± 0,07 | 0,54 ± 0,01 | 0,788 ± 0,008 | 0,848 ± 0,009 | 0,765 ± 0,010 | 0,686 ± 0,006 | 0,793 ± 0,007 | 0,796 ± 0,008 |
| ia16_P2 | 5 | 2,95 ± 0,03 | 4,33 ± 0,03 | 0,49 ± 0,01 | 0,850 ± 0,008 | 0,874 ± 0,009 | 0,811 ± 0,006 | 0,786 ± 0,008 | 0,955 ± 0,002 | 0,824 ± 0,004 |
| ia16_P1 | 5 | 2,64 ± 0,04 | 3,84 ± 0,06 | 0,49 ± 0,01 | 0,817 ± 0,008 | 0,839 ± 0,009 | 0,747 ± 0,006 | 0,705 ± 0,009 | 0,923 ± 0,002 | 0,776 ± 0,007 |
| ia16_R | 5 | 3,35 ± 0,05 | 4,64 ± 0,01 | 0,68 ± 0,03 | 0,892 ± 0,006 | 0,927 ± 0,006 | 0,718 ± 0,007 | 0,658 ± 0,006 | 0,962 ± 0,002 | 0,740 ± 0,009 |
| ia20_M1 | 5 | 3,06 ± 0,05 | 4,01 ± 0,05 | 0,54 ± 0,01 | 0,778 ± 0,016 | 0,851 ± 0,008 | 0,780 ± 0,007 | 0,694 ± 0,009 | 0,784 ± 0,003 | 0,808 ± 0,007 |
| ia20_M2 | 5 | 3,09 ± 0,03 | 3,82 ± 0,04 | 0,55 ± 0,02 | 0,777 ± 0,007 | 0,844 ± 0,005 | 0,772 ± 0,007 | 0,652 ± 0,012 | 0,793 ± 0,004 | 0,794 ± 0,008 |
| ia20_M3 | 5 | 2,67 ± 0,05 | 3,55 ± 0,06 | 0,52 ± 0,01 | 0,777 ± 0,014 | 0,793 ± 0,011 | 0,802 ± 0,003 | 0,711 ± 0,002 | 0,812 ± 0,008 | 0,815 ± 0,004 |
| ia20_M4 | 5 | 2,95 ± 0,02 | 3,86 ± 0,05 | 0,58 ± 0,02 | 0,821 ± 0,009 | 0,852 ± 0,007 | 0,760 ± 0,010 | 0,627 ± 0,010 | 0,849 ± 0,003 | 0,757 ± 0,010 |
| ia20_M5 | 5 | 2,90 ± 0,05 | 3,51 ± 0,02 | 0,58 ± 0,02 | 0,769 ± 0,007 | 0,791 ± 0,008 | 0,788 ± 0,009 | 0,706 ± 0,006 | 0,785 ± 0,006 | 0,803 ± 0,007 |
| ia22_E0 | 5 | 3,21 ± 0,04 | 4,35 ± 0,06 | 0,54 ± 0,01 | 0,831 ± 0,004 | 0,896 ± 0,007 | 0,784 ± 0,005 | 0,727 ± 0,003 | 0,827 ± 0,005 | 0,808 ± 0,006 |
| ia22_E1 | 5 | 2,89 ± 0,02 | 3,71 ± 0,04 | 0,54 ± 0,01 | 0,779 ± 0,010 | 0,854 ± 0,010 | 0,772 ± 0,004 | 0,653 ± 0,010 | 0,806 ± 0,006 | 0,782 ± 0,002 |
| ia22_E2 | 5 | 3,04 ± 0,04 | 4,11 ± 0,03 | 0,52 ± 0,02 | 0,833 ± 0,004 | 0,864 ± 0,005 | 0,778 ± 0,005 | 0,680 ± 0,007 | 0,882 ± 0,004 | 0,787 ± 0,004 |
| ia22_E3 | 5 | 2,94 ± 0,04 | 3,80 ± 0,06 | 0,53 ± 0,00 | 0,794 ± 0,014 | 0,839 ± 0,007 | 0,774 ± 0,006 | 0,686 ± 0,009 | 0,796 ± 0,008 | 0,797 ± 0,008 |
| ia23_P1 | 5 | 2,89 ± 0,05 | 3,93 ± 0,04 | 0,47 ± 0,00 | 0,801 ± 0,008 | 0,819 ± 0,009 | 0,810 ± 0,008 | 0,769 ± 0,003 | 0,837 ± 0,004 | 0,807 ± 0,009 |
| ia23_P2 | 5 | 3,38 ± 0,03 | 4,31 ± 0,05 | 0,58 ± 0,01 | 0,796 ± 0,008 | 0,841 ± 0,003 | 0,838 ± 0,007 | 0,795 ± 0,008 | 0,823 ± 0,006 | 0,851 ± 0,008 |
| ia23_P3 | 5 | 3,34 ± 0,06 | 4,18 ± 0,04 | 0,59 ± 0,00 | 0,803 ± 0,012 | 0,836 ± 0,011 | 0,799 ± 0,008 | 0,739 ± 0,006 | 0,845 ± 0,007 | 0,808 ± 0,007 |
| ia24_W1 | 5 | 2,88 ± 0,08 | 3,53 ± 0,06 | 0,62 ± 0,02 | 0,774 ± 0,007 | 0,839 ± 0,004 | 0,646 ± 0,007 | 0,574 ± 0,011 | 0,768 ± 0,012 | 0,681 ± 0,007 |
| ia24_W2 | 5 | 3,32 ± 0,03 | 4,02 ± 0,05 | 0,58 ± 0,01 | 0,759 ± 0,007 | 0,835 ± 0,004 | 0,802 ± 0,008 | 0,778 ± 0,007 | 0,785 ± 0,004 | 0,828 ± 0,008 |
| ia24_W3 | 5 | 3,28 ± 0,03 | 4,49 ± 0,07 | 0,55 ± 0,01 | 0,837 ± 0,011 | 0,867 ± 0,013 | 0,849 ± 0,005 | 0,788 ± 0,005 | 0,875 ± 0,006 | 0,849 ± 0,005 |
| CIF:V_1 | 1 | 5,52 ± — | 37,53 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:V_3 | 1 | 5,37 ± — | 43,75 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:V_6 | 1 | 5,53 ± — | 41,30 ± — | 1,00 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:S_1 | 1 | 5,71 ± — | 47,01 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:S_2 | 1 | 5,44 ± — | 41,88 ± — | 0,88 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:S_4 | 1 | 5,47 ± — | 40,64 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:N_30 | 1 | 5,35 ± — | 44,11 ± — | 0,88 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:N_150 | 1 | 5,56 ± — | 41,50 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:N_600 | 1 | 5,11 ± — | 43,33 ± — | 0,88 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:C_4 | 1 | 5,73 ± — | 217,87 ± — | 1,00 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:C_16 | 1 | 5,55 ± — | 202,66 ± — | 1,00 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:C_64 | 1 | 5,48 ± — | 206,21 ± — | 0,88 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:R_6 | 1 | 5,80 ± — | 46,04 ± — | 1,00 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:R_12 | 1 | 5,70 ± — | 44,57 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:R_24 | 1 | 5,93 ± — | 54,80 ± — | 1,00 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:F_3p5 | 1 | 5,37 ± — | 37,83 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:F_5p0 | 1 | 5,38 ± — | 41,77 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:F_7p0 | 1 | 5,84 ± — | 45,45 ± — | 1,00 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:P_1 | 1 | 5,62 ± — | 43,02 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:P_5 | 1 | 5,60 ± — | 44,25 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:P_25 | 1 | 5,58 ± — | 43,94 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:V_3_italiano | 1 | 5,49 ± — | 42,04 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:V_3_tedesco | 1 | 5,48 ± — | 38,43 ± — | 0,94 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| CIF:T0 | 1 | 5,37 ± — | 43,13 ± — | 0,88 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — | 1,000 ± — |
| LG | 8 | 5,59 ± 0,04 | 43,33 ± 0,62 | 0,93 ± 0,01 | 1,000 ± 0,000 | 1,000 ± 0,000 | 1,000 ± 0,000 | 1,000 ± 0,000 | 1,000 ± 0,000 | 1,000 ± 0,000 |
| CTRL | 3 | 3,17 ± 1,30 | 6,06 ± 2,39 | 0,49 ± 0,23 | 0,829 ± 0,166 | 0,861 ± 0,136 | 0,855 ± 0,136 | 0,858 ± 0,135 | 0,833 ± 0,166 | 0,916 ± 0,079 |

### z medio per misura (valore del gruppo meno il vero, in scale)

| gruppo | copia_netta | lam | contatto | D | G9 | bordi_inizio | bordi_fine | parole_nuove | costo_forma | k90 | R_rel |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V21 | -3,0 | -0,5 | -0,3 | -2,5 | -0,4 | -0,2 | -1,3 | -0,6 | 3,4 | -0,8 | -0,1 |
| TS | 25,7 | -0,1 | -13,1 | -6,6 | 1,6 | -12,0 | -9,7 | 22,2 | 14,4 | 11,9 | -1,1 |
| NAIBBE | -5,7 | 13,1 | -14,0 | -7,0 | -13,1 | -12,0 | -9,8 | 15,5 | 5,9 | -1,1 | -0,8 |
| ia07 | -3,3 | 0,2 | -1,0 | 0,2 | -5,7 | -0,4 | -1,2 | -0,5 | 4,5 | -0,6 | -1,3 |
| ia16_P2 | -1,3 | -0,5 | -4,0 | -0,8 | -0,3 | 0,7 | 3,1 | -1,6 | -1,8 | -0,8 | 0,2 |
| ia16_P1 | -1,1 | -0,6 | -2,8 | -0,3 | 1,0 | 0,1 | 4,1 | -2,0 | -0,4 | -0,6 | -0,8 |
| ia16_R | -4,1 | -2,4 | -5,2 | -2,4 | -6,1 | 2,1 | -1,4 | 0,9 | -1,2 | -1,1 | -1,2 |
| ia20_M1 | -4,2 | -0,7 | -0,4 | 0,3 | -6,8 | 0,1 | -0,6 | -0,6 | 5,1 | -0,8 | -0,7 |
| ia20_M2 | -3,5 | 0,5 | -1,7 | -1,4 | -6,3 | -1,1 | 0,6 | 1,8 | 3,8 | -0,7 | -0,8 |
| ia20_M3 | -1,2 | -0,9 | 0,7 | 0,2 | -3,1 | 2,0 | -0,2 | 0,1 | 4,0 | -0,6 | -0,4 |
| ia20_M4 | -1,8 | -0,5 | -2,9 | -1,9 | -4,9 | -0,1 | -0,7 | 0,4 | 4,8 | -0,8 | -1,5 |
| ia20_M5 | 0,8 | 1,2 | -2,5 | -1,7 | -3,4 | 0,3 | -1,2 | 1,8 | 3,7 | -0,6 | -1,1 |
| ia22_E0 | -1,2 | 3,6 | -1,3 | -0,6 | -7,4 | 0,5 | 0,5 | 0,9 | 5,2 | -0,8 | -1,1 |
| ia22_E1 | -1,3 | 3,0 | -0,4 | 0,2 | -4,8 | 1,2 | 0,7 | -0,7 | 4,4 | -0,7 | -1,6 |
| ia22_E2 | 1,1 | 2,2 | 1,2 | 1,0 | -4,9 | 0,6 | -0,6 | -1,1 | 5,7 | -0,7 | -0,9 |
| ia22_E3 | 0,2 | 3,5 | -1,0 | 0,5 | -4,9 | 0,3 | -0,9 | -0,3 | 5,2 | -0,6 | -0,9 |
| ia23_P1 | 0,6 | -0,7 | -1,1 | -0,6 | -3,2 | 0,3 | -0,0 | 0,8 | 6,2 | -0,7 | -1,5 |
| ia23_P2 | 4,6 | 0,9 | -1,4 | -0,1 | -5,8 | 0,3 | -0,6 | 2,2 | 4,7 | -0,7 | -1,3 |
| ia23_P3 | 5,0 | 1,0 | 1,0 | -0,6 | -5,8 | 1,0 | 0,3 | 3,1 | 3,7 | -0,7 | -1,4 |
| ia24_W1 | -4,2 | -0,2 | -2,2 | -0,2 | -5,8 | 0,4 | 1,2 | -3,5 | 3,7 | -0,9 | -1,1 |
| ia24_W2 | -0,4 | 3,0 | -2,0 | -1,1 | -5,9 | -1,7 | -1,6 | 0,3 | 4,9 | -0,9 | -1,2 |
| ia24_W3 | -3,6 | -0,1 | -0,5 | -0,3 | -5,2 | -1,7 | 0,2 | 1,0 | 6,0 | -0,6 | -1,1 |
| CIF:V_1 | -5,8 | 5,6 | -8,5 | -6,6 | -12,5 | -12,0 | -9,8 | 96,4 | 116,3 | 1,8 | -2,7 |
| CIF:V_3 | -5,9 | -3,6 | -12,6 | -6,6 | -12,5 | -12,0 | -9,8 | 97,7 | 147,7 | 3,0 | 0,8 |
| CIF:V_6 | -5,8 | -3,8 | -13,9 | -6,6 | -12,5 | -12,0 | -9,8 | 97,4 | 135,1 | 3,7 | 2,8 |
| CIF:S_1 | 10,0 | 1,0 | -11,0 | -6,6 | -12,6 | -12,0 | -9,7 | 95,9 | 164,0 | 6,7 | 15,0 |
| CIF:S_2 | -1,7 | -0,8 | -13,1 | -6,6 | -12,9 | -12,0 | -9,8 | 93,3 | 140,9 | 6,0 | 8,5 |
| CIF:S_4 | -4,9 | 0,8 | -14,0 | -6,6 | -13,5 | -12,0 | -9,6 | 93,9 | 134,2 | 4,5 | 4,7 |
| CIF:N_30 | 1,3 | -0,3 | -12,7 | -6,6 | -13,3 | -12,0 | -9,7 | 98,9 | 148,6 | 5,3 | 6,7 |
| CIF:N_150 | 6,2 | -0,6 | -13,2 | -6,6 | -12,2 | -12,0 | -9,7 | 94,5 | 138,2 | 3,9 | 6,7 |
| CIF:N_600 | 0,2 | -0,0 | -13,4 | -6,6 | -12,8 | -12,0 | -9,7 | 92,4 | 148,9 | 4,5 | 4,2 |
| CIF:C_4 | 877,4 | 2,8 | -14,0 | -6,6 | 24,6 | -12,0 | -9,8 | 90,4 | 148,1 | 72,4 | -4,6 |
| CIF:C_16 | 805,8 | 2,0 | -14,4 | -6,6 | 31,3 | -12,0 | -9,8 | 90,4 | 132,2 | 146,1 | -2,3 |
| CIF:C_64 | 737,9 | 1,2 | -13,9 | -6,6 | 44,2 | -12,0 | -9,7 | 94,5 | 152,6 | 378,4 | -1,9 |
| CIF:R_6 | 26,7 | 8,8 | 14,0 | -6,6 | -10,1 | -12,0 | -9,7 | 99,0 | 149,0 | 2,7 | — |
| CIF:R_12 | 74,6 | 7,4 | -1,2 | -6,6 | -8,3 | -12,0 | -9,7 | 99,0 | 124,1 | 7,9 | — |
| CIF:R_24 | 130,8 | 4,8 | -11,2 | -6,6 | -6,8 | -12,0 | -9,6 | 98,8 | 146,2 | 39,3 | 15,7 |
| CIF:F_3p5 | -5,6 | -2,4 | 24,3 | -6,6 | -12,2 | -12,0 | -9,7 | 83,2 | 125,7 | 3,9 | 1,2 |
| CIF:F_5p0 | -5,6 | -2,3 | 24,9 | -6,6 | -13,7 | -12,0 | -9,8 | 95,8 | 137,1 | 3,7 | 1,9 |
| CIF:F_7p0 | -5,6 | -5,0 | 30,0 | -6,6 | -13,7 | -12,0 | -9,8 | 98,8 | 145,9 | 4,8 | — |
| CIF:P_1 | -5,9 | -18,5 | -4,9 | -6,6 | -13,0 | -12,0 | -9,6 | 95,9 | 135,9 | 49,2 | -0,8 |
| CIF:P_5 | -5,9 | -17,7 | -5,1 | -6,6 | -13,4 | -12,0 | -9,7 | 95,8 | 138,9 | 58,7 | -0,2 |
| CIF:P_25 | -5,9 | -9,4 | -4,2 | -6,6 | -13,6 | -12,0 | -9,7 | 95,6 | 136,4 | 62,7 | -0,8 |
| CIF:V_3_italiano | -5,8 | 10,4 | -11,6 | -6,6 | -12,4 | -12,1 | -9,8 | 98,3 | 138,3 | 3,2 | -0,2 |
| CIF:V_3_tedesco | -5,7 | 7,7 | -10,9 | -6,6 | -12,6 | -12,0 | -9,7 | 94,5 | 122,4 | 3,4 | -0,2 |
| CIF:T0 | 0,7 | -1,5 | -12,2 | -6,6 | -12,7 | -12,0 | -9,7 | 98,1 | 144,1 | 5,0 | 9,5 |
| LG | 6,6 | -0,3 | -8,8 | -6,7 | -9,8 | -12,0 | -9,7 | 90,2 | 150,0 | 6,3 | 11,6 |
| CTRL | -2,2 | 1,6 | -9,5 | -4,6 | -4,1 | -7,9 | -6,4 | -4,5 | 0,4 | -1,0 | -1,0 |

## Le affermazioni delle voci precedenti, rilette con la fascia (B3)

- (a) G9 mai al vero: NON regge per tutti; non fuori fascia: ia16_P2, ia16_P1.
- (a) costo di forma delle parole nuove mai al vero: NON regge per tutti; non fuori fascia: ia16_P2, ia16_P1, ia16_R.
- (b) Λ fuori fascia nei gruppi con eco: ia22_E0, ia22_E1, ia22_E3; dentro o misti: ia16_P2, ia16_P1, ia16_R, ia20_M2, ia20_M3, ia20_M4, ia20_M5, ia22_E2, ia23_P1, ia23_P2, ia23_P3.
- (c) contatto per gruppo: ia07 dentro la fascia; ia16_P2 fuori fascia; ia16_P1 fuori fascia; ia16_R fuori fascia; ia20_M1 dentro la fascia; ia20_M2 dentro la fascia; ia20_M3 dentro la fascia; ia20_M4 fuori fascia; ia20_M5 fuori fascia; ia22_E0 dentro la fascia; ia22_E1 dentro la fascia; ia22_E2 dentro la fascia; ia22_E3 dentro la fascia; ia23_P1 dentro la fascia; ia23_P2 dentro la fascia; ia23_P3 dentro la fascia; ia24_W1 fuori fascia; ia24_W2 misto; ia24_W3 dentro la fascia.
- (d) M1: contatto dentro la fascia, D dentro la fascia.
- (e) v21: z di e231 e e266 OrderedDict({'e231': 1.3587585734327754, 'e266': 2.2420623245275864}); imitatori con z più piccolo del v21 su tutti e due: nessuno.

### Giudici nuovi contro vecchi (B4): correlazione di rango fra i 48 gruppi

e231~e266 0,98, K~e231 0,90, K~e266 0,88, K~N 0,89, K~KN 0,99, A~e231 0,89, A~e266 0,87, A~K 0,98, A~N 0,89, A~KN 0,98, N~e231 0,99, N~e266 0,96, KN~e231 0,90, KN~e266 0,89, KN~N 0,89.
N e KN concordano con K (rho ≥ 0,7): sì.


## Controlli

- Controllo negativo del catalogo: parole rimescolate in tutto il libro fuori fascia su almeno 0,50 di misure e giudici: 0,82 → sì; parole rimescolate dentro la riga fuori fascia su contatto, D e almeno un giudice a sorpresa (z contatto -14,3, D -7,1, K 8,7, A 8,8, N 10,6, KN 8,8) → sì.
- Metro disponibile: sì.
- Calibrazione del mondo "calibrato" (entro 0,15): errori relativi copia_netta 0,008, lam 0,067, contatto 0,026, G9 0,730 → NO.
- Positivo (M1 su catena di Markov di ordine 2: e231, e266, K al massimo 0,60): e231 0.7551683905101358, e266 0.7543770751652187, K 0.8496666993432017 → NO.
- Negativo, gemello del mondo markov2 (fuori fascia ≤ 0,20, con i giudici non puliti centrati sul gemello): fuori fascia 0,00, distanza 0,41, AUC e231 0,525, e266 0,527, K 0,477; giudici non puliti (gemello fuori dal nullo): nessuno → sì.
- Negativo, gemello del mondo tec (fuori fascia ≤ 0,20, con i giudici non puliti centrati sul gemello): fuori fascia 0,00, distanza 0,39, AUC e231 0,481, e266 0,469, K 0,476; giudici non puliti (gemello fuori dal nullo): nessuno → sì.
- Negativo, gemello del mondo calibrato (fuori fascia ≤ 0,20, con i giudici non puliti centrati sul gemello): fuori fascia 0,00, distanza 0,72, AUC e231 0,472, e266 0,481, K 0,424; giudici non puliti (gemello fuori dal nullo): nessuno → sì.

## Taratura: gli imitatori su processi noti

| mondo | imitatore | libri | distanza | fuori fascia | classe | sul Voynich: distanza | classe | rapporto mondo / Voynich | gemello |
|---|---|---|---|---|---|---|---|---|---|
| markov2 | M1 | 4 | 3,21 | 0,58 | lontano | 3,06 | lontano | 1,05 | 0,41 |
| tec | M1 | 4 | 4,05 | 0,78 | lontano | 3,06 | lontano | 1,32 | 0,39 |
| tec | M5 | 4 | 3,44 | 0,62 | lontano | 2,90 | lontano | 1,19 | 0,39 |
| tec | E2 | 4 | 3,38 | 0,58 | lontano | 3,04 | lontano | 1,11 | 0,39 |
| calibrato | M1 | 4 | 3,37 | 0,54 | lontano | 3,06 | lontano | 1,10 | 0,72 |
| calibrato | M5 | 4 | 3,54 | 0,68 | lontano | 2,90 | lontano | 1,22 | 0,72 |
| calibrato | E2 | 4 | 3,46 | 0,62 | lontano | 3,04 | lontano | 1,14 | 0,72 |

## Letture preregistrate

- Mondo primario: tec; controlli validi: NO.
- **Esito: lettura non valida (controlli: positivo markov2).**
- Imitatori lontani nel mondo noto quanto sul Voynich: M1, M5, E2. Imitatori al vero nel mondo noto e lontani sul Voynich: nessuno.

### Misura per misura (mondo primario; z medio sui libri dell'imitatore)

**M1**

| misura | z nel mondo | z sul Voynich | classe |
|---|---|---|---|
| copia netta (bit per parola) | -34,7 | -4,2 | fuori in tutti e due (limite degli imitatori) |
| quota locale Λ | -7,6 | -0,7 | fuori solo nel mondo noto |
| contatto ultimo→primo glifo | -2,6 | -0,4 | fuori solo nel mondo noto |
| ordine delle famiglie D | -0,2 | 0,3 | dentro in tutti e due |
| G9 vocabolario della pagina | -7,5 | -6,8 | fuori in tutti e due (limite degli imitatori) |
| bordi: inizio riga | -0,6 | 0,1 | dentro in tutti e due |
| bordi: fine riga | 0,3 | -0,6 | dentro in tutti e due |
| quota di parole nuove | 9,2 | -0,6 | fuori solo nel mondo noto |
| costo di forma delle parole nuove (bit per glifo) | -3,7 | 5,1 | fuori in tutti e due (limite degli imitatori) |
| giudice 1 (e231) | 9,9 | 5,2 | fuori in tutti e due (limite degli imitatori) |
| giudice 2 (e266) | 9,9 | 6,7 | fuori in tutti e due (limite degli imitatori) |
| giudice K | 8,2 | 5,1 | fuori in tutti e due (limite degli imitatori) |
| giudice A (rete) | 3,7 | 3,6 | fuori in tutti e due (limite degli imitatori) |
| giudice N (n-grammi, nuovo) | 5,0 | 6,1 | fuori in tutti e due (limite degli imitatori) |
| giudice KN (Kneser-Ney, nuovo) | 3,5 | 5,6 | fuori in tutti e due (limite degli imitatori) |

**M5**

| misura | z nel mondo | z sul Voynich | classe |
|---|---|---|---|
| copia netta (bit per parola) | -11,1 | 0,8 | fuori solo nel mondo noto |
| quota locale Λ | 10,7 | 1,2 | fuori solo nel mondo noto |
| contatto ultimo→primo glifo | -0,4 | -2,5 | fuori solo sul Voynich (bersaglio) |
| ordine delle famiglie D | 0,2 | -1,7 | dentro in tutti e due |
| G9 vocabolario della pagina | -1,3 | -3,4 | fuori solo sul Voynich (bersaglio) |
| bordi: inizio riga | 1,1 | 0,3 | dentro in tutti e due |
| bordi: fine riga | -0,4 | -1,2 | dentro in tutti e due |
| quota di parole nuove | 7,6 | 1,8 | fuori solo nel mondo noto |
| costo di forma delle parole nuove (bit per glifo) | -1,7 | 3,7 | fuori solo sul Voynich (bersaglio) |
| giudice 1 (e231) | 8,2 | 5,0 | fuori in tutti e due (limite degli imitatori) |
| giudice 2 (e266) | 8,3 | 5,5 | fuori in tutti e due (limite degli imitatori) |
| giudice K | 5,6 | 5,2 | fuori in tutti e due (limite degli imitatori) |
| giudice A (rete) | 2,7 | 3,8 | fuori in tutti e due (limite degli imitatori) |
| giudice N (n-grammi, nuovo) | 6,0 | 6,1 | fuori in tutti e due (limite degli imitatori) |
| giudice KN (Kneser-Ney, nuovo) | 2,1 | 5,5 | fuori in tutti e due (limite degli imitatori) |

**E2**

| misura | z nel mondo | z sul Voynich | classe |
|---|---|---|---|
| copia netta (bit per parola) | -12,0 | 1,1 | fuori solo nel mondo noto |
| quota locale Λ | 10,6 | 2,2 | fuori in tutti e due (limite degli imitatori) |
| contatto ultimo→primo glifo | 0,8 | 1,2 | dentro in tutti e due |
| ordine delle famiglie D | 0,7 | 1,0 | dentro in tutti e due |
| G9 vocabolario della pagina | -0,9 | -4,9 | fuori solo sul Voynich (bersaglio) |
| bordi: inizio riga | 1,8 | 0,6 | dentro in tutti e due |
| bordi: fine riga | 0,5 | -0,6 | dentro in tutti e due |
| quota di parole nuove | 6,3 | -1,1 | fuori solo nel mondo noto |
| costo di forma delle parole nuove (bit per glifo) | -2,0 | 5,7 | fuori in tutti e due (limite degli imitatori) |
| giudice 1 (e231) | 8,1 | 6,3 | fuori in tutti e due (limite degli imitatori) |
| giudice 2 (e266) | 8,2 | 6,9 | fuori in tutti e due (limite degli imitatori) |
| giudice K | 4,3 | 5,0 | fuori in tutti e due (limite degli imitatori) |
| giudice A (rete) | 2,5 | 3,3 | fuori in tutti e due (limite degli imitatori) |
| giudice N (n-grammi, nuovo) | 5,6 | 8,1 | fuori in tutti e due (limite degli imitatori) |
| giudice KN (Kneser-Ney, nuovo) | 1,8 | 5,2 | fuori solo sul Voynich (bersaglio) |

## Calibrazione

Parametri scelti: eco 0,007, tema 0,132, contatto 0,150, ritocco 0,600, inizio 0,000, n_tema 25,000, freq_min_tema 3,000. Valori del vero (banco): copia_netta 0,112, lam 0,137, contatto 0,188, G9 0,040. Ottenuti: copia_netta 0,113, lam 0,146, contatto 0,193, G9 0,011. Errori relativi: copia_netta 0,01, lam 0,07, contatto 0,03, G9 0,73. Valori pubblicati (ia20-ia24, solo confronto): copia_netta 0,114, lam 0,207, contatto 0,188, D 0,144, G9 0,040, costo_forma 3,480.

## Tempi (minuti per lavoro)

- addestra: 35 lavori, media 36.7, massimo 55.5, totale 1284.3.
- libro: 28 lavori, media 6.4, massimo 12.8, totale 178.7.
- K: 30 lavori, media 0.2, massimo 0.4, totale 6.3.
- KN: 30 lavori, media 0.3, massimo 0.6, totale 7.9.
- D: 30 lavori, media 0.3, massimo 0.8, totale 8.6.
- M: 179 lavori, media 0.8, massimo 2.3, totale 139.3.
- J: 175 lavori, media 0.7, massimo 2.1, totale 122.0.
- G: 322 lavori, media 2.2, massimo 4.7, totale 704.1.
- gm: 36 lavori, media 2.0, massimo 3.2, totale 72.7.
- lmA: 40 lavori, media 2.6, massimo 4.8, totale 103.3.
- metro: 4 lavori, media 1.7, massimo 3.1, totale 6.8.
- nullo: 24 lavori, media 3.4, massimo 5.1, totale 81.4.
- cal: 34 lavori, media 0.8, massimo 1.0, totale 28.0.
