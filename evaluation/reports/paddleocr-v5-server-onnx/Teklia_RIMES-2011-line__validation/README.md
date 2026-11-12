# paddleocr-v5-server-onnx — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T14:22:21+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_server_det, rec_model=PP-OCRv5_server_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.4508 |
| wer | 0.8602 |

## Speed and energy

| | |
|---|---|
| Inference mean | 1.009s |
| Inference p50 / p90 / p95 / p99 | 0.968s / 1.527s / 1.727s / 2.140s |
| Inference max | 2.892s |
| Seconds per megapixel | 4.734 |
| Energy | 0.081210 kWh |
| Emissions | 0.004553 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 1.009s | 1.727s |

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
| 374 | 3.333 | DISTINGUEES. | AESIEORS, UEXPRESSISN DE HES SAWTATIONS DSTiNGUEES |
| 893 | 1.163 | agréer l'expression de mes sentiments distingués. | ax semes tidn pour ts Ainte a dommet,e afreer I expurion she ues tentimeut distiniln |
| 15 | 1.111 | Dans l'attente de votre offre, je vous prie de croire, | nappll qul Concidig abrs un rabais de 30 au l abomnement dn an. vous me Je vous |
| 23 | 1.000 | Je souhaite vivement obtenir un rendez-vous avec un de vos conseillers pour |  |
| 99 | 1.000 | 21 rue Victor Hugo |  |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `f8e6ce9053c4`
