# tesseract-fra — lightonai/fc-amf-ocr (train)

**Date:** 2026-11-12T14:19:25+00:00  
**Status:** ✅ passed  
**Samples:** 1000 evaluated, 0 errors (seed 42, max_samples 1000)  
**Dataset:** [lightonai/fc-amf-ocr](https://huggingface.co/datasets/lightonai/fc-amf-ocr) · revision `036bd28ba275`  
**Model:** `tesseract` lang=fra, psm=3, oem=1, threads=1

## Scores

| Metric | Value |
|---|---|
| cer | 0.7321 |
| wer | 0.4109 |

## Speed and energy

| | |
|---|---|
| Inference mean | 0.986s |
| Inference p50 / p90 / p95 / p99 | 0.967s / 1.479s / 1.692s / 2.297s |
| Inference max | 6.252s |
| Seconds per megapixel | 0.492 |
| Energy | 0.003267 kWh |
| Emissions | 0.000207 kgCO2eq |

| Image size | Samples | Mean inference | p95 |
|---|---|---|---|
| 1-4MP | 998 | 0.980s | 1.688s |
| >=4MP | 2 | 4.146s | 5.002s |

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
| 163_2013_07_FC16303… | 338.000 | a | RSA Philippe Moumas KPMG AUDIT SUD-EST 480 avenue du Prado 167 rue Paradis 13269 Marseill… |
| 163_2013_07_FC16303… | 143.091 | 2 3 € e 3 3 | Richel Serres de France S.A. Rapport des commissaires aux comptes sur les comptes annuels… |
| pdf_323_2021_09_FC3… | 9.955 | a A a L L DLDDDIDDI a X L D D E a 00 L. D &00 0 D0 800 0 D - 9 D D e00 800 800 Q00 000 00… | ep Feu0D UonmAsU JuE ne O1 PEJIOU 8G 0} AE LOELLQQU euieN a1e10d109 “SSI 10 SA ‘IN / 21E2… |
| pdf_182_2022_04_FC1… | 4.584 | o o o o o o o o 0 o o O O o & d8 4 o o o a de & a 0 o o o b de  9 Bs o o o e 6 8 6 8 o 4 … | 9vr6 O9Z0U 18301 18 oszou 199 8 oszou N 609 Ovzou 509 806 ovzou EN z8 oEzou 18 2e9 69€ ol… |
| pdf_323_2022_07_FC3… | 4.345 | a € a (D D a - & 8 - E E o a a P 1 1 : 8 e N co 8 9 S 5 N 00 8 2 : 5 N a W S - E 2 8 B d … | [Nature des indications 2017 / 2018 2018 / 2019 2019 / 2020 2020 / 2021 2021 / 2022 1 - c… |

Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `5448d1601e8e`
