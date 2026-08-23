# Stage 03: Python Fundamentals

This homework applies NumPy vectorization, pandas inspection and aggregation, reusable function design, and file output to the course-provided `starter_data.csv`. The completed notebook compares a Python loop with a vectorized NumPy calculation, validates and profiles the dataset, imports summary helpers from `src/utils.py`, saves reproducible CSV outputs, and creates a bonus category-level plot.

## Deliverables

```text
homework/homework03/
├── README.md
├── homework03_python-fundamentals_submission.ipynb
├── data/
│   ├── raw/
│   │   └── starter_data.csv
│   └── processed/
│       ├── category_summary.csv
│       └── summary.csv
├── reports/
│   └── category_mean_value.png
└── src/
    └── utils.py
```

## Environment

Continue with the Stage 02 environment and add the Stage 03 analysis packages:

```bash
conda activate fe-course
python -m pip install pandas matplotlib
```

The submitted notebook was executed with Python 3.11, NumPy 2.4.6, pandas 3.0.5, and matplotlib 3.11.1.

## Run the Notebook

From the repository root:

```bash
conda run -n fe-course jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  homework/homework03/homework03_python-fundamentals_submission.ipynb
```

The notebook locates `homework03` without relying on a single launch directory, imports the reusable helpers from `src/utils.py`, and recreates every processed output.

## Main Findings

- The course dataset contains 10 complete observations across categories A, B, and C.
- The overall mean of `value` is 17.6.
- Category C has the highest mean value at approximately 27.67; category A has the lowest at 11.50.
- The dataset is a small instructional sample, so these summaries demonstrate the workflow rather than support a general real-world conclusion.
- The measured loop/vectorization speed comparison is environment-dependent; the notebook verifies identical numerical results before reporting the timing ratio.

## AI Assistance Disclosure

An AI assistant helped structure the notebook, implement reusable utilities, and check the submission against the Stage 03 rubric. The student is responsible for reviewing the code, understanding the vectorization and pandas operations, and validating the conclusions.
