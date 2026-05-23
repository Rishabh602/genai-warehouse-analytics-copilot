def detect_anomaly(row, kpi_rules):

    anomaly_reasons = []

    for kpi, rule in kpi_rules.items():

        target = rule["target"]
        comparison = rule["comparison"]
        value = row[kpi]

        if comparison == "higher" and value < target:

            anomaly_reasons.append(
                f"{kpi} below target ({value} vs {target})"
            )

        elif comparison == "lower" and value > target:

            anomaly_reasons.append(
                f"{kpi} above target ({value} vs {target})"
            )

    if len(anomaly_reasons) > 0:

        return "Anomaly", "\n".join(anomaly_reasons)

    else:

        return "Normal", "No major KPI breach"