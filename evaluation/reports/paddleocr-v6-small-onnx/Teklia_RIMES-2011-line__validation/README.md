# paddleocr-v6-small-onnx — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T13:59:11+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv6_small_det, rec_model=PP-OCRv6_small_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.1925 |
| wer | 0.6192 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.041s |
| Inference p50 / p90 / p95 / p99 | 0.041s / 0.062s / 0.068s / 0.081s |
| Inference max | 0.110s |
| Seconds per megapixel | 0.194 |
| Energy | 0.000230 kWh |
| Emissions | 0.000014 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 0.041s | 0.068s |

## Hardware

| | |
|---|---|
| Label | github-ubuntu-latest |
| CPU | AMD EPYC 9V45 96-Core Processor (2 cores, 4 threads) |
| RAM | 15.6 GB |
| GPU | none |
| OS / Python | Linux-7.0.0-1019-azure-x86_64-with-glibc2.43 / 3.13.18 |
| Libraries | onnxruntime 1.31.1, codecarbon 3.3.2 |

Energy figures are estimates when CPU power counters are not readable (RAPL).

## Worst samples (by cer)

| Id | cer | Reference | Prediction |
|---|---|---|---|
| 685 | 5.200 | quelques mois ? | est sinple : pauvtz- vous me faire une sffre sninilavre i celle que járais refuse il y a |
| 374 | 3.500 | DISTINGUEES. | AESSIEORS, UEXPRESSION DE HES SAWTATIONS DISTINGUEES |
| 15 | 1.222 | Dans l'attente de votre offre, je vous prie de croire, | Te vous rappelli que vaus me concediz abs een nabais de 3o% sun l abonnement d'en an. |
| 23 | 1.000 | Je souhaite vivement obtenir un rendez-vous avec un de vos conseillers pour |  |
| 51 | 1.000 | au vu de ma nouvelle situation familiale, je |  |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `f4fee4b9db24`
