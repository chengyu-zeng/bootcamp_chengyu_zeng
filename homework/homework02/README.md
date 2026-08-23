# Stage 02: Tooling Setup

This homework builds and verifies a reproducible Python workspace for the boot camp. It uses the `fe-course` Conda environment with Python 3.11, keeps configuration in an ignored `.env` file, exposes reusable configuration helpers through `src/config.py`, and records an executed Jupyter check showing that the environment, dummy API key, data path, and NumPy installation all work together.

## Folder Structure

```text
homework/homework02/
├── .env.example
├── README.md
├── requirements.txt
├── data/
│   ├── processed/
│   └── raw/
├── docs/
├── model/
├── notebooks/
│   └── 00_project_setup.ipynb
├── reports/
└── src/
    └── config.py
```

## Environment

```bash
conda activate fe-course
python --version
python -m pip install -r requirements.txt
```

The expected Python major/minor version is 3.11. The environment used to execute the submitted notebook reports its exact interpreter path and package versions.

## Configuration and Secrets

Create the local configuration from the safe template:

```bash
cp .env.example .env
```

The template contains only the course-provided dummy key. The repository-level `.gitignore` excludes every file named `.env`, so a later real API key must remain local. The helper functions in `src/config.py` load this homework's `.env` explicitly instead of relying on the shell's current working directory.

## Notebook Check

Run the notebook from any location inside this repository:

```bash
conda run -n fe-course jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  homework/homework02/notebooks/00_project_setup.ipynb
```

A successful run prints `API_KEY present: True`, resolves `DATA_DIR` to this homework's `data/` directory, and completes a small NumPy array operation.

## AI Assistance Disclosure

An AI assistant helped organize the scaffold, improve path handling, and check the work against the Stage 02 rubric. The student is responsible for reviewing the code, understanding how environment variables and imports work, and validating the submission.
