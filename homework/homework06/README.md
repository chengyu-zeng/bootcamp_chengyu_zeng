# Stage 06: Data Preprocessing

This homework converts the Stage 06 starter dataset into a complete, scaled analytical table using reusable, non-mutating functions. The notebook demonstrates every required transformation, compares the original and cleaned data, saves a reproducible processed CSV, and documents the associated trade-offs.

## Deliverables

```text
homework/homework06/
├── README.md
├── homework06_data-preprocessing_submission.ipynb
├── data/
│   ├── raw/
│   │   └── sample_data.csv
│   └── processed/
│       ├── cleaning_summary.csv
│       └── sample_data_cleaned.csv
└── src/
    ├── __init__.py
    └── cleaning.py
```

## Cleaning Strategy

The raw dataset is the seven-row sample defined by the course starter notebook. Identifiers and categories are read as strings so that `zipcode` is never treated as a measurable quantity.

The transformations run in this order:

1. **Drop high-missingness columns:** `drop_missing(..., threshold=0.5, axis="columns")` removes columns with more than 50% missing values. This removes `extra_data`, which is missing in five of seven rows (71.4%). A column exactly at the threshold would be retained.
2. **Median imputation:** `fill_missing_median(...)` fills `age`, `income`, and `score`. Medians are resistant to extreme values and preserve all seven observations, but they reduce variability and can weaken relationships between variables.
3. **Min-max normalization:** `normalize_data(..., method="minmax")` maps the three imputed numeric columns to `[0, 1]`. This places features on a common scale while preserving rank, but the mapping remains sensitive to future values outside the fitted range.

The cleaned output contains seven rows and five columns with no missing values. `zipcode` and `city` are unchanged. All three functions return copies instead of modifying their inputs.

## Function Behavior

`src/cleaning.py` implements the three required functions with explicit validation:

- `fill_missing_median(frame, columns=None)` selects specified numeric columns—or all incomplete numeric columns by default—and rejects all-missing or nonnumeric inputs.
- `drop_missing(frame, threshold=0.5, axis="columns")` supports column-wise and row-wise missing-fraction policies and validates the threshold.
- `normalize_data(frame, columns, method="minmax")` supports min-max and z-score normalization, maps constant columns to `0.0`, and requires missingness to be handled first.

## Reproduce the Submission

Continue with the `fe-course` environment established in Stage 02. Only pandas is required beyond Jupyter:

```bash
conda activate fe-course
python -m pip install pandas
```

Execute from the repository root:

```bash
conda run -n fe-course jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  homework/homework06/homework06_data-preprocessing_submission.ipynb
```

The notebook locates `homework06` without relying on one launch directory and deterministically rewrites the two processed CSVs.

## Assumptions and Trade-offs

- `Unknown` is treated as an observed category, not as a missing value.
- `zipcode` is an identifier and is neither imputed with a numeric statistic nor normalized.
- Median values are calculated from this complete instructional dataset. In a predictive workflow, imputation and scaling parameters must be learned on training data only and then applied unchanged to validation, test, or production data.
- Median imputation is appropriate for this demonstration but is not automatically appropriate for missing SPY prices. Market-time-series gaps may represent holidays, outages, or source errors and require date-aware investigation; using a full-history median could create severe distortion and leakage.
- Min-max normalization changes interpretability from original units to relative position. The notebook records pre-normalization medians and before/after ranges so the transformation remains auditable.
- The sample is too small and artificial to support real-world conclusions. It demonstrates preprocessing mechanics rather than a fitted market-data policy.

## AI Assistance Disclosure

An AI assistant helped implement and validate this Stage 06 submission. The student is responsible for understanding each cleaning choice, its alternatives, and why training-only fitted parameters are necessary in later predictive stages.
