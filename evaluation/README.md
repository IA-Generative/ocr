# ocr-evaluation

Standalone project (own `pyproject.toml`) that evaluates models against HuggingFace
datasets and writes one JSON report per dataset. A model is either the deployed API (through `ocr-sdk`,
end to end) or a model loaded locally in-process, no API.

## Usage

```bash
cd evaluation
uv sync
export OCR_API_URL=http://localhost:5000
export OCR_API_KEY=...            # if the API needs one
uv run ocr-eval run configs/ocr_example.yaml --output-dir reports
```

Exit code: `0` all datasets pass, `2` a threshold in the config is violated (reports are still
written), `1` crash. Local runs write to `reports_local/` by default.
Env vars `OCR_API_URL` / `OCR_API_KEY` override the config file.

## Layout

- `configs/` – one YAML per run (dataset, columns, sample cap, thresholds)
- `src/ocr_eval/dataset/` – HF loading (fixed-seed shuffle) + one adapter per dataset schema, normalized to `Sample` (words + pixel bboxes)
- `src/ocr_eval/metrics.py` – CER / WER
- `src/ocr_eval/models/` – backends producing a `Prediction` (text + pixel-bbox words): `api`, plus local models
- `src/ocr_eval/tasks/` – one class per task (what is scored); register it in `tasks/__init__.py`
- `src/ocr_eval/runner.py` – loop + report

## Adding a task (layout, tables, ...)

Subclass `Task` (`score`, `check`), add it to `TASKS`, set `task:` in the config.

## Tests

```bash
uv run pytest && uv run ruff check .
```

## Adding a dataset schema

Datasets differ in column names, box format (xyxy/xywh) and scale (pixel/0..1/0..1000).
An adapter in `src/ocr_eval/dataset/` maps a raw row to `Sample(words=[Word(text, bbox)])`
with bboxes in pixels. Either subclass `GenericAdapter` with the schema defaults (see
`funsd.py`) and register it in `ADAPTERS`, or use `adapter: generic` and describe the
columns in the config (`image_column`, `text_column`, `bboxes_column`, `bbox_format`, `bbox_scale`).

## Adding a local model (no API)

Subclass `LocalModel` in `src/ocr_eval/models/`, import the heavy libs inside `load()`,
return a `Prediction` from `predict(sample)`, register it in `MODELS`, then:

```yaml
model:
  type: my_model      # key in MODELS
  device: cuda        # every other key is passed to the model as params
  weights: /path/to/weights
```

Tasks and datasets are independent of the backend, so any model runs on any task/dataset.

## Profiling

Every report has a `profiling` section and a per-sample `profile`: image size, inference
time, and (codecarbon) energy in kWh and emissions in kgCO2eq. The summary gives mean/p50/p95,
seconds per megapixel and mean time per image-size bucket (<1MP, 1-4MP, >=4MP).
codecarbon runs offline (set `profiling.country_iso_code`); disable with `codecarbon: false`.
It measures the machine running `ocr-eval`, so for the API backend it only sees the client.

## Hardware metadata

Each report has a `hardware` section (CPU model/cores, RAM, GPUs, OS, Python, torch/onnxruntime/
paddle versions, CI/container flags) so results stay comparable across machines. It describes
the machine running `ocr-eval`; for the API backend set `hardware.label` to describe the server.

## Reports

A config lists several `datasets`. The model is loaded once; each dataset is evaluated on its
own and gets its own report (scores, profiling, energy, hardware) in
`reports/<name>/<dataset>__<split>/{report.json,README.md}`, plus `reports/<name>/index.json` and a
`README.md` listing the datasets. `label:` renames a report; a dataset-level `thresholds:` overrides the global one.
The exit code is 1 if any dataset fails.

## CI and versioned reports

`.github/workflows/evaluation.yml` evaluates every config that has `ci: true`:

- **On a pull request** it plans what to run (`ocr-eval plan`): configs added or modified by the
  PR, every config if the evaluation code or its dependencies changed, and any config that has
  never produced a report (so the first run launches everything). Each selected config runs **in
  parallel on its own runner**, one failure never cancels the others, and the updated reports
  are pushed as one commit to the PR branch. Do not make this workflow a required check: it
  takes hours.
- **On `main`, weekly and manually** it runs every config and opens (or updates) one PR,
  `chore/evaluation-reports`, **only if the reports changed**.

A new model = a new `configs/<model>.yaml` with `ci: true` (and, for a new backend, its entry in
`MODEL_EXTRAS` in `plan.py`). Configs without `ci: true` (e.g. the API one) are only run by hand.

Nothing is written unless an input changed, because each dataset report carries a fingerprint of:
the evaluation code, the task, the model (parameters, library versions, weights hash), the dataset
config (split, `max_samples`, seed, adapter...), the dataset's HF revision, and the hardware label
(`OCR_EVAL_HARDWARE_LABEL`, set by CI). If it matches the committed report, the dataset is not
re-run and its report is left byte-identical, timings included. Thresholds are not in the
fingerprint: pass/fail is recomputed. `--force` (or the workflow's `force` input) re-runs everything.

`reports/` is what CI produced on a given runner class; local runs go to `reports_local/` so they
cannot overwrite it. Per-sample details are in `samples.jsonl` next to each report: gitignored, and
uploaded by CI as the `evaluation-samples` artifact.

Latency is reported as mean, p50, p90, p95, p99 and max (linear interpolation), and p95 per
image-size bucket. p99 is only meaningful with ~1000 samples; FUNSD's test split has 50.

## Models

| `type` | Config | Needs |
|---|---|---|
| `api` | `ocr_example.yaml` | a running API (`OCR_API_URL`, `OCR_API_KEY`); never cached |
| `paddleocr_onnx` | `paddleocr_v6_tiny_onnx.yaml` | `uv sync --extra paddle` |
| `tesseract` | `tesseract_fra.yaml` | `uv sync --extra tesseract` + `apt install tesseract-ocr tesseract-ocr-fra` |

Tesseract has no single multilingual model: languages are combined, `lang: fra+eng`. It is run
single-threaded (`threads: 1`) for reproducible scores and comparable timings. `psm: 3` (auto page
layout) suits forms and PDF pages; on RIMES' single lines `psm: 7` only moves CER from 0.63 to 0.62
(30 samples), so the poor RIMES score is Tesseract on handwriting, not a segmentation setting.
