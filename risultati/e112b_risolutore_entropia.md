# e112b — Risolutore a sillabe con entropia: prova di fattibilità sul controllo

Macer cifrato in sillabe con varianti (e104); trigrammi di sillabe da Ovidio, Lucrezio, Virgilio e Plinio. Preregistrazione: `preregistrazioni/e112b.md`.

| prova | simboli | accuratezza | copertura 4+ | copertura 6+ |
|---|---|---|---|---|
| tetto: Macer in chiaro | – | – | 80.0% | 53.5% |
| cifrato, mu 0.0 | 1245 | 0.02 | 59.0% | 22.9% |
| cifrato, mu 0.3 | 3345 | 0.02 | 57.7% | 20.7% |
| cifrato, mu 0.6 | 4732 | 0.02 | 56.7% | 23.7% |
| negativo: mu 0.6 rimescolato | 4732 | – | 53.7% | 20.7% |
| negativo: Timm e Schinner | 4602 | – | 55.1% | 20.8% |
| diagnosi: modello barato, mu 0.0 | 1245 | 0.96 | 78.2% | 51.2% |
| diagnosi: modello barato, mu 0.6 | 4732 | 0.08 | 48.7% | 16.2% |

Risolutore valido: **no**. Fattibile: μ 0.0: no, μ 0.3: no, μ 0.6: no.

Esempi decifrati (μ 0,6):

    le ge no sed dit la pe quam spes et ra ma me
    i re mean di lit tra re ne te mo rer flam mae
    mis ce que mi ri sub tis da ta va na que tue ri
    sol ce rum da re gu lo bus cum o leo lae
    hoc te quod na per se que a res ri les vi li quit
    le ti te ma nus di dae si ve a sa quae est
