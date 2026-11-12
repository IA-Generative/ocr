# paddleocr-v5-server-onnx — nielsr/funsd-layoutlmv3 (test)

**Date:** 2026-11-12T14:05:22+00:00  
**Status:** ✅ passed  
**Samples:** 50 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [nielsr/funsd-layoutlmv3](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3) · revision `ccd2a77745b0`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv5_server_det, rec_model=PP-OCRv5_server_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.4342 |
| wer | 0.6417 |

## Speed and energy

| | |
|---|---|
| Inference mean | 9.180s |
| Inference p50 / p90 / p95 / p99 | 8.837s / 12.870s / 14.867s / 17.884s |
| Inference max | 18.583s |
| Seconds per megapixel | 12.012 |
| Energy | 0.035800 kWh |
| Emissions | 0.002007 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 50 | 9.180s | 14.867s |

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
| 10 | 0.734 | COURT: Asbestos JUDGE: CASE FORM CASE NAME: LORILLARD ENTITIES DATE FILED DATE SERVED CAS… | CASE FORM CASE NAME: Donald D.Selers and Robin J.Sellers v. Raybestos-Manhattan, et al. C… |
| 9 | 0.725 | COURT: JUDGE: Asbestos CASE FORM CASE NAME: LORILLARD ENTITIES: DATE FILED: DATE SERVED: … | CASE FORM CASE NAME: Wanda G.Robinson and Carroll Robinson v. Raybestos-Manhattan, et al.… |
| 37 | 0.725 | Date: on BLEND CASTING RECASING MENIHOL Filters Cigarettes Maker Length Circumference Wei… | Date:3/14/90 90-B-1 Sample No. 1194-90 Type of Cigarette 100 mmn Filter Batch Size 47.5 l… |
| 28 | 0.661 | From: To: CC: Circulation(#) 86075409 Tiers II, & IV Lynnette Stevens Kelli Scruggs Vince… | From: Lynnette Stevens To: Kelli Scruggs CC: Vincent Losito Don Kisling George Baroody S.… |
| 31 | 0.659 | TO: FROM: SUBJECT: X GEOGRAPHY REGION: DIVISION: FULL PARTIAL x FULL PARTIAL DISTRIBUTION… | 12/12/96 08:33 504 7348616 LORILLARD TOB →→NYO1 001/004 K. A. Sparrow SUBMISSION-DATE. TO… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `ebd7cf024d92`
