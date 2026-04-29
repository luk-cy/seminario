# Extracción fotométrica para una lista de TICs de TESS con `psfmachine`

Este repositorio contiene un flujo reproducible para aplicar `psfmachine` (SSDataLab) a objetivos de la misión **TESS** usando una lista de TIC IDs.

## TICs solicitados

- 11300044
- 199780530
- 264459850
- 427395094
- 427395136
- 200093870
- 138829413
- 200093884
- 269118295
- 264462165
- 264462237
- 284284106
- 284284069
- 427347825
- 427347969
- 427393284
- 427394530
- 427395536
- 50897998
- 712930938

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Ejecución

El script descarga Target Pixel Files de TESS vía `lightkurve`, construye un `TPFMachine` y exporta curvas de luz (PSF/SAP cuando existan) en CSV por cada TIC.

```bash
python scripts/run_tess_psfmachine.py \
  --tic-file data/tics.txt \
  --sectors all \
  --cadence short \
  --output-dir outputs
```

Opciones útiles:

- `--sectors 70,71`: procesa solo sectores específicos.
- `--cadence long`: usa cadencia larga (útil si no hay short cadence disponible).
- `--limit 5`: prueba rápida con los primeros 5 TIC.

## Salida esperada

Por cada TIC se crea una carpeta en `outputs/` con:

- `log.json`: metadatos del procesamiento.
- `lc_*.csv`: curvas de luz extraídas.
- `error.txt` si no fue posible procesar el objetivo.

## Notas

- `psfmachine` está pensado para campos congestionados y puede mejorar la deconvolución frente a aperturas simples.
- Si un TIC no tiene TPF en un sector/cadencia dado, se reporta en `error.txt` y el flujo continúa.
