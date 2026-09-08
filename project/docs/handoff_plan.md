# Stage14 Deployment Handoff Plan

- **Deploy surface:** run the saved model behind the local Flask API in `app.py`; it binds to `127.0.0.1:5050` and is not an internet-facing production service.
- **Startup check:** run `GET /health`; confirm the expected feature count and `training_end` before accepting any score.
- **Data contract:** `POST /predict` requires every named, finite model feature; schema and null failures are JSON HTTP 400. See [`src/productization.py`](../src/productization.py).
- **Model version and rollback:** `model/spy_risk_alert_model.pkl` contains the model, feature schema, threshold, cutoff, and training end. Keep the last approved artifact; rollback means replacing the current artifact only after risk-manager approval and restarting the service.
- **Daily operator:** the risk analyst runs the pipeline after close, reviews data freshness/schema checks, and reads the Stage12 stakeholder report before escalating an alert.
- **Monitoring runbook:** use [`monitoring_plan.md`](monitoring_plan.md) for Data, Model, System, and Business thresholds plus first-response actions.
- **Model review:** the model owner investigates PSI or PR-AUC breaches, evaluates any candidate chronologically, and never changes the cutoff from a live request.
- **Escalation and record:** platform on-call owns API failures; the portfolio risk manager owns business-risk escalation and rollback approval. Record incidents, evidence, decisions, and artifact versions in the project change log.
- **Stakeholder context:** [`stakeholder_handoff.md`](stakeholder_handoff.md) and [`../reports/spy_risk_alert_stakeholder_report.md`](../reports/spy_risk_alert_stakeholder_report.md) define limitations, decision boundaries, and next steps.
