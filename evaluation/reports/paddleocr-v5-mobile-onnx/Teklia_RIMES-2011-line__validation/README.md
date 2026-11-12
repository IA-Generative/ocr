# paddleocr-v5-mobile-onnx — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T14:02:08+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_mobile_det, rec_model=PP-OCRv5_mobile_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.5028 |
| wer | 0.9087 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.170s |
| Inference p50 / p90 / p95 / p99 | 0.175s / 0.257s / 0.272s / 0.321s |
| Inference max | 0.568s |
| Seconds per megapixel | 0.798 |
| Energy | 0.013728 kWh |
| Emissions | 0.000772 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 0.170s | 0.272s |

## Hardware

| | |
|---|---|
| Label | github-ubuntu-latest |
| CPU | AMD EPYC 7763 64-Core Processor (2 cores, 4 threads) |
| RAM | 15.6 GB |
| GPU | none |
| OS / Python | Linux-7.0.0-1019-azure-x86_64-with-glibc2.43 / 3.13.18 |
| Libraries | onnxruntime 1.31.1, codecarbon 3.3.2 |

Energy figures are estimates when CPU power counters are not readable (RAPL).

## Worst samples (by cer)

| Id | cer | Reference | Prediction |
|---|---|---|---|
| 374 | 3.333 | DISTINGUEES. | AESSEORS UEXPRESSISN DE HES SAWTATISNS DSTINGUEES 1 |
| 15 | 1.074 | Dans l'attente de votre offre, je vous prie de croire, | naypl qul vous me concidiy abrs im nabsi de 3ol sn l'abonnemend d'in an. Leou |
| 7 | 1.000 | nouvelles ni pour me dire si mon dossier était complet, ni pour me recevoir. |  |
| 21 | 1.000 | par le modèle à la référence suivante CH45 16. Je vous laisse bien sûr |  |
| 23 | 1.000 | Je souhaite vivement obtenir un rendez-vous avec un de vos conseillers pour |  |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `1eca5d1414fa`
