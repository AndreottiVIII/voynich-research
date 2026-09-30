# Esperimento 18: le parole del Voynich sono anagrammi ordinati?

- **ordine rispettato**: fra tutte le coppie di segni diversi dentro le parole (parole diverse, contate una volta), la quota che rispetta l'ordine dei segni migliore per quel testo. Parole con le lettere in ordine fisso: 100%. Nessun ordine scende sotto il 50%.
- **anagrammi**: quota delle parole diverse che hanno gli stessi segni di un'altra parola del testo, in un altro ordine. Parole ordinate: 0%.
- **rotazioni**: quota delle parole diverse che sono un'altra parola con un pezzo spostato da un capo all'altro (*chol* → *lcho*).

Testi naturali (93, 35.000 parole ciascuno): ordine rispettato 59.5–96.0% (mediana 66.2%); anagrammi 0.8–27.2% (mediana 5.3%); rotazioni 0.0–11.9% (mediana 1.0%).

| testo | ordine rispettato | anagrammi | rotazioni | parole diverse | ordine dei segni (i primi 20) |
|---|---|---|---|---|---|
| Voynich (ZL, segni EVA) | 78.5% | 35.4% | 8.7% | 7022 | v q c t z p sh f ch cph cth o k ckh cfh e d s a l |
| Voynich (v101) | 78.9% | 26.8% | 6.9% | 8045 | w 4 E k g + % j 3 f ! v 2 1 G U J K # o |
| Voynich, lingua A di Currier | 79.1% | 26.4% | 7.8% | 3217 | v q c t z p k f sh ch cph cth cfh o ckh e d s a l |
| Voynich, lingua B di Currier | 79.7% | 29.9% | 7.7% | 4785 | q p sh o c f t l k ch ckh cth cfh cph z e s d b a |
| Naibbe (Plinio cifrato) | 79.2% | 27.3% | 9.1% | 5600 | cph q x o f p t l k sh ch ckh cth e s d a y i r |
| controllo: latino con le lettere in ordine alfabetico | 100.0% | 0.0% | 0.0% | 5811 | a b c d e f g h i l m n o p q r s t u v |
| controllo: latino con le lettere mescolate | 50.6% | 85.7% | 22.1% | 20040 | z t i l m s f x n u a p r v e g d c o h |
| Bibbia: Hebrew | 65.0% | 27.2% | 8.9% | 7173 | w מ ב א ה ג פ ש ל ח ז כ צ ע ק נ ו ט ס ד |
| Bibbia: Syriac | 67.8% | 22.7% | 4.9% | 6691 | ܕ ܒ ܫ ܠ ܡ ܚ ܙ ܨ ܥ ܤ ܦ ܩ ܛ ܓ ܟ ܘ ܬ ܪ ܝ ܢ |
| Bibbia: Potawatomi | 61.5% | 19.2% | 2.8% | 7490 | g p m s h k o c i d w a l y n t u v e r |
| Bibbia: Maori | 68.7% | 15.8% | 9.5% | 1459 | w h p k m t o a u r e i n g |
| Bibbia: Arabic | 65.6% | 14.6% | 3.6% | 7879 | ف أ و إ ا ل آ ش خ ص غ س ت ط ح ج ث ب ي ز |
| Bibbia: Chinese (pinyin, una sillaba per parola) | 96.0% | 4.8% | 0.0% | 798 | b c d f j k l ü m p q s t w x y z r h u |
| Bibbia: Vietnamese | 79.3% | 4.1% | 1.6% | 1624 | v ð d x k b q đ l ặ j s ụ t r í ự ọ á c |
| Bibbia: Chinantec (Quiotepec) | 75.6% | 0.8% | 0.3% | 3297 | k c z ü d p j h l y s f n a q m i t ú g |
| Bibbia: Indonesian | 71.3% | 5.5% | 0.7% | 2756 | z q m b e d f c p j w r s o t g i u k l |
| Bibbia: Tamajaq (Tuareg) | 70.5% | 7.3% | 2.7% | 4726 | i ṃ ç t â ə š ó ṣ s v ṭ h j ḍ x o ŋ g ̣ |

Nella tabella, dopo il Voynich e i controlli: i cinque testi naturali con più anagrammi e i cinque con l'ordine più rigido.
