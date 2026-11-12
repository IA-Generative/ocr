# paddleocr-v5-server-onnx — lightonai/fc-amf-ocr (train)

**Date:** 2026-11-12T19:49:20+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [lightonai/fc-amf-ocr](https://huggingface.co/datasets/lightonai/fc-amf-ocr) · revision `036bd28ba275`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_server_det, rec_model=PP-OCRv5_server_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.6953 |
| wer | 0.3810 |

## Speed and energy

| | |
|---|---|
| Inference mean | 19.438s |
| Inference p50 / p90 / p95 / p99 | 19.166s / 27.830s / 31.280s / 39.994s |
| Inference max | 80.042s |
| Seconds per megapixel | 9.696 |
| Energy | 1.489467 kWh |
| Emissions | 0.083556 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| 1-4MP | 998 | 19.370s | 31.182s |
| >=4MP | 2 | 53.464s | 59.867s |

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
| 163_2013_07_FC16303… | 334.000 | a | KPMG Rapport des commissaires aux comtes sur lescomptesconsolidés Richel Serres de France… |
| 163_2013_07_FC16303… | 133.364 | 2 3 € e 3 3 | ω 2 Exercice closle3lmars2013 Associé John Evans les documentsadressésauxactionnairessurl… |
| pdf_323_2022_07_FC3… | 5.618 | a € a (D D a - & 8 - E E o a a P 1 1 : 8 e N co 8 9 S 5 N 00 8 2 : 5 N a W S - E 2 8 B d … | les"resulttsavantamortissementetrovisionsontoberedemoinvluelielapuremetdettredeciteantcss… |
| pdf_323_2021_09_FC3… | 3.723 | a A a L L DLDDDIDDI a X L D D E a 00 L. D &00 0 D0 800 0 D - 9 D D e00 800 800 Q00 000 00… | era crre rrc ra arcra rorcr TRR EETRTT eeee ree e eee e cee r 一 reeecre  e ee re o crnrar… |
| pdf_182_2022_04_FC1… | 3.713 | o o o o o o o o 0 o o O O o & d8 4 o o o a de & a 0 o o o b de  9 Bs o o o e 6 8 6 8 o 4 … | ee seope Teeeereeeee 10000 609 1128 156 O 0 0 0 0 0 1 3 82 A A100 A0OA 20000 20000 200 20… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `cd1c0b855228`
