# e112 — Risolutore a sillabe: prova di fattibilità sul controllo

Macer cifrato in sillabe con varianti (e104); trigrammi di sillabe da Ovidio, Lucrezio, Virgilio e Plinio. Preregistrazione: `preregistrazioni/e112.md`.

| prova | simboli | accuratezza | copertura 4+ | copertura 6+ |
|---|---|---|---|---|
| tetto: Macer in chiaro | – | – | 80.0% | 53.5% |
| cifrato, mu 0.0 | 1245 | 0.03 | 82.7% | 38.4% |
| cifrato, mu 0.3 | 3345 | 0.02 | 87.1% | 39.2% |
| cifrato, mu 0.6 | 4732 | 0.02 | 90.5% | 44.6% |
| negativo: mu 0.6 rimescolato | 4732 | – | 94.4% | 44.1% |
| negativo: Timm e Schinner | 4602 | – | 90.6% | 41.3% |

Risolutore valido: **no**. Fattibile: μ 0.0: no, μ 0.3: no, μ 0.6: no.

Esempi decifrati (μ 0,6):

    de se re re re re re re de de re re re
    qua re qui re re mo re re re re in o re
    re re re se re re re re re se re re fer re
    se de re de re re re re pa ra re re
    re re re re re se re re re de re de re bus
    de re re re de re fer re fer re re re re
