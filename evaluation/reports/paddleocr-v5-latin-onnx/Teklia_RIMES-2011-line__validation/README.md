# paddleocr-v5-latin-onnx — Teklia/RIMES-2011-line (validation)

**Date:** 2026-11-12T14:01:04+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [Teklia/RIMES-2011-line](https://huggingface.co/datasets/Teklia/RIMES-2011-line) · revision `ba3e6b557309`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_mobile_det, rec_model=latin_PP-OCRv5_mobile_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.4501 |
| wer | 0.8284 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.132s |
| Inference p50 / p90 / p95 / p99 | 0.136s / 0.202s / 0.215s / 0.241s |
| Inference max | 0.333s |
| Seconds per megapixel | 0.621 |
| Energy | 0.000958 kWh |
| Emissions | 0.000054 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 1000 | 0.132s | 0.215s |

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
| 374 | 3.583 | DISTINGUEES. | DESSIEORS L'EXPRESSION OE HES SAWTATIONS D.STINGUEES 1 |
| 15 | 1.185 | Dans l'attente de votre offre, je vous prie de croire, | rafpll que vous mne concidiz abs un nabais de 30% sn l abonnement dun an. Je vous |
| 7 | 1.000 | nouvelles ni pour me dire si mon dossier était complet, ni pour me recevoir. |  |
| 21 | 1.000 | par le modèle à la référence suivante CH45 16. Je vous laisse bien sûr |  |
| 23 | 1.000 | Je souhaite vivement obtenir un rendez-vous avec un de vos conseillers pour |  |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `a94bcc3f95cb`
