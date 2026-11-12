# paddleocr-v5-mobile-onnx — lightonai/fc-amf-ocr (train)

**Date:** 2026-11-12T15:06:06+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [lightonai/fc-amf-ocr](https://huggingface.co/datasets/lightonai/fc-amf-ocr) · revision `036bd28ba275`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_mobile_det, rec_model=PP-OCRv5_mobile_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.7078 |
| wer | 0.3929 |

## Speed and energy

| | |
|---|---|
| Inference mean | 3.675s |
| Inference p50 / p90 / p95 / p99 | 3.573s / 5.875s / 6.947s / 9.548s |
| Inference max | 18.939s |
| Seconds per megapixel | 1.833 |
| Energy | 0.232298 kWh |
| Emissions | 0.013098 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| 1-4MP | 998 | 3.656s | 6.831s |
| >=4MP | 2 | 12.923s | 14.004s |

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
| 163_2013_07_FC16303… | 338.000 | a | KPMG Rapport des commissaires aux comptes sur les comptes consolidés Richel Serres de Fra… |
| 163_2013_07_FC16303… | 141.636 | 2 3 € e 3 3 | ω N Johon Exercice closle31 mars2013 Associé John Evans les documents adressés aux action… |
| pdf_323_2021_09_FC3… | 6.914 | a A a L L DLDDDIDDI a X L D D E a 00 L. D &00 0 D0 800 0 D - 9 D D e00 800 800 Q00 000 00… | y an o ng a e s pe a  a s s n s o am - an  s ne s t  seos s s n e  a  as  s a an Sua poua… |
| pdf_323_2022_07_FC3… | 5.924 | a € a (D D a - & 8 - E E o a a P 1 1 : 8 e N co 8 9 S 5 N 00 8 2 : 5 N a W S - E 2 8 B d … | les " résultats avant amortissements et provisions " sont obérés des moins-values liées a… |
| pdf_182_2022_04_FC1… | 3.248 | o o o o o o o o 0 o o O O o & d8 4 o o o a de & a 0 o o o b de  9 Bs o o o e 6 8 6 8 o 4 … | aguue,pu!s saguuop) seesentoe 00 609 ∠L8 96 O 0 0 0 0 0 8 8 >  000  0800 0600       28 10… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `a08f6fe613b6`
