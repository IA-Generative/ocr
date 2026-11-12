# paddleocr-v6-tiny-onnx — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T13:59:05+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv6_tiny_det, rec_model=PP-OCRv6_tiny_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.2736 |
| wer | 0.7733 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.051s |
| Inference p50 / p90 / p95 / p99 | 0.050s / 0.075s / 0.085s / 0.099s |
| Inference max | 0.116s |
| Seconds per megapixel | 0.237 |
| Energy | 0.000368 kWh |
| Emissions | 0.000022 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 0.051s | 0.085s |

## Hardware

| | |
|---|---|
| Label | github-ubuntu-latest |
| CPU | AMD EPYC 9V74 80-Core Processor (2 cores, 4 threads) |
| RAM | 15.6 GB |
| GPU | none |
| OS / Python | Linux-7.0.0-1019-azure-x86_64-with-glibc2.43 / 3.13.18 |
| Libraries | onnxruntime 1.31.1, codecarbon 3.3.2 |

Energy figures are estimates when CPU power counters are not readable (RAPL).

## Worst samples (by cer)

| Id | cer | Reference | Prediction |
|---|---|---|---|
| 685 | 4.933 | quelques mois ? | eol simyle : pourty- vous mi faine unm ofhe sinilavie  cell que j'avai refuse il y a |
| 374 | 3.083 | DISTINGUEES. | AESEORS,UExPREsiSN DE HEs SAWTAioNs DiSTiNGUEES- |
| 893 | 1.204 | agréer l'expression de mes sentiments distingués. | olernes u aut pout ls sute a olommes , J。 a freer I'expusion oe mes Sentmcut distnes |
| 15 | 1.204 | Dans l'attente de votre offre, je vous prie de croire, | Je vous rapelli que vous me comcidig abrs ien nabais de 30% sn d abonemeont d'um an. |
| 23 | 1.000 | Je souhaite vivement obtenir un rendez-vous avec un de vos conseillers pour |  |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `0ed95b6041af`
