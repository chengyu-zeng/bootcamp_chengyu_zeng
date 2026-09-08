# Stage 13 Homework - Prediction API

This self-contained API serves predictions from a `LinearRegression` model trained on a deterministic two-feature synthetic dataset. It loads `model/model.pkl` once when the Flask process starts; both routes reuse that in-memory model.

## Run

From `homework/homework13/`:

```bash
python app.py
```

The API listens on `http://127.0.0.1:5001`.

## POST `/predict`

```bash
curl -X POST http://127.0.0.1:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.1, 0.2]}'
```

Response:

```json
{"prediction": 23.5896}
```

## GET `/predict/<f1>/<f2>`

```bash
curl http://127.0.0.1:5001/predict/0.1/0.2
```

Response:

```json
{"prediction": 23.5896}
```

## Bad input

Missing keys, the wrong number of values, nonnumeric values, and non-finite values return JSON with HTTP 400. For example, `GET /predict/abc/0.2` returns:

```json
{"error":"features must contain only numbers"}
```
