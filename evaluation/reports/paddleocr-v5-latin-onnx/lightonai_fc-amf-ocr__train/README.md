# paddleocr-v5-latin-onnx — lightonai/fc-amf-ocr (train)

**Date:** 2026-11-12T14:51:32+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [lightonai/fc-amf-ocr](https://huggingface.co/datasets/lightonai/fc-amf-ocr) · revision `036bd28ba275`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_mobile_det, rec_model=latin_PP-OCRv5_mobile_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.7092 |
| wer | 0.3921 |

## Speed and energy

| | |
|---|---|
| Inference mean | 2.859s |
| Inference p50 / p90 / p95 / p99 | 2.755s / 4.488s / 5.556s / 7.227s |
| Inference max | 13.208s |
| Seconds per megapixel | 1.426 |
| Energy | 0.017839 kWh |
| Emissions | 0.001022 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| 1-4MP | 998 | 2.846s | 5.489s |
| >=4MP | 2 | 9.297s | 9.865s |

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
| 163_2013_07_FC16303… | 339.000 | a | KPMG Rapport des commissaires aux comptes sur les comptes consolidés Richel Serres de Fra… |
| 163_2013_07_FC16303… | 142.182 | 2 3 € e 3 3 | 3 2 PohEn Exercice clos le 31 mars 2013 Associé John Evans les documents adressés aux act… |
| pdf_323_2022_07_FC3… | 6.021 | a € a (D D a - & 8 - E E o a a P 1 1 : 8 e N co 8 9 S 5 N 00 8 2 : 5 N a W S - E 2 8 B d … | les " résultats avant amortissements et provisions " sont obérés des moins-values liées à… |
| pdf_323_2021_09_FC3… | 5.997 | a A a L L DLDDDIDDI a X L D D E a 00 L. D &00 0 D0 800 0 D - 9 D D e00 800 800 Q00 000 00… | ct a te too h de cb pue e ss  so  p s uode co - uro he se ne cub te c 'uodd s s ne e  mo … |
| pdf_182_2022_04_FC1… | 4.317 | o o o o o o o o 0 o o O O o & d8 4 o o o a de & a 0 o o o b de  9 Bs o o o e 6 8 6 8 o 4 … | enue,punn suuop) (sesns G6000 609 ZLz 8 9 6 o O o o O o 88 8 e ROLOO ROLLO ROLL0 ROLL0 RL… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `9a00061b7428`
