# paddleocr-v6-tiny-onnx — nielsr/funsd-layoutlmv3 (test)

**Date:** 2026-11-12T13:58:04+00:00  
**Status:** ✅ passed  
**Samples:** 50 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [nielsr/funsd-layoutlmv3](https://huggingface.co/datasets/nielsr/funsd-layoutlmv3) · revision `ccd2a77745b0`  
**Model:** `paddleocr_onnx` det_model=PP-OCRv6_tiny_det, rec_model=PP-OCRv6_tiny_rec, device=cpu

## Scores

| Metric | Value |
|---|---|
| cer | 0.4191 |
| wer | 0.6155 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.482s |
| Inference p50 / p90 / p95 / p99 | 0.450s / 0.722s / 0.787s / 0.834s |
| Inference max | 0.844s |
| Seconds per megapixel | 0.631 |
| Energy | 0.000132 kWh |
| Emissions | 0.000008 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| <1MP | 50 | 0.482s | 0.787s |

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
| 10 | 0.741 | COURT: Asbestos JUDGE: CASE FORM CASE NAME: LORILLARD ENTITIES DATE FILED DATE SERVED CAS… | CASE FORM CASE NAME: Donald D. Sellers and Robin J . Sellers v. Raybestos-Manhattan, et a… |
| 37 | 0.725 | Date: on BLEND CASTING RECASING MENIHOL Filters Cigarettes Maker Length Circumference Wei… | Date:3/14/90 90-B-1 Sanple No. 1194-90 Type of Cigarette 100 mm Filter Batch Size 47.5 lb… |
| 9 | 0.719 | COURT: JUDGE: Asbestos CASE FORM CASE NAME: LORILLARD ENTITIES: DATE FILED: DATE SERVED: … | CASE FORM CASE NAME: Wanda G. Robinson and Carroll Robinson v. Raybestos-Manhattan, et al… |
| 28 | 0.672 | From: To: CC: Circulation(#) 86075409 Tiers II, & IV Lynnette Stevens Kelli Scruggs Vince… | From: Lynnette Stevens To: Keli Scruggs CC: Vincent Losito Don Kisling George Baroody S.T… |
| 31 | 0.661 | TO: FROM: SUBJECT: X GEOGRAPHY REGION: DIVISION: FULL PARTIAL x FULL PARTIAL DISTRIBUTION… | 12/12/96 08:33 504 7348616 LORILLARD TOB +→→NYO 1 001/004 1 TO: -SUBMTSsION.DATE. K. A. S… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `86844d3d8b2c`
