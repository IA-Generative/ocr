# paddleocr-v6-medium-onnx — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T14:09:51+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv6_medium_det, rec_model=PP-OCRv6_medium_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.2004 |
| wer | 0.5731 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.402s |
| Inference p50 / p90 / p95 / p99 | 0.398s / 0.549s / 0.590s / 0.692s |
| Inference max | 0.868s |
| Seconds per megapixel | 1.884 |
| Energy | 0.002901 kWh |
| Emissions | 0.000164 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 0.402s | 0.590s |

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
| 685 | 4.667 | quelques mois ? | et imple: paurtz vous me faine ume offre sinilane a celle que arais refusee i ya |
| 374 | 3.500 | DISTINGUEES. | TESSIEORS, LEXPRESSION DE HES SAWTATIONS DISTINGUEES |
| 15 | 1.167 | Dans l'attente de votre offre, je vous prie de croire, | e vous raffelle que vaus me concidig abrs en nabais de 3o% sen l'abonnement d'en an. |
| 51 | 1.000 | au vu de ma nouvelle situation familiale, je |  |
| 85 | 1.000 | Je souhaiterais connaître les horaires |  |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `a3add2a5de30`
