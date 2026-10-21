"""Serving policy only; never changes the saved model or training metadata."""
from datetime import datetime, timezone


def year_policy(metadata):
    minimum = metadata["recommended_prediction_year_range"][0]
    maximum = max(2026, datetime.now(timezone.utc).year) + 5
    return {
        "accepted_prediction_year_range": [minimum, maximum],
        "dataset_year_range": metadata["dataset_info"]["years"],
        "train_year_range": metadata["train_year_range"],
        "test_year_range": metadata["test_year_range"],
        "future_accuracy_validated": False,
    }


def estimate_context(metadata, year):
    policy = year_policy(metadata)
    experimental = year > policy["dataset_year_range"][1]
    return {
        **policy,
        "estimate_type": "experimental" if experimental else "historical",
        "estimate_label": "Experimental estimate — future accuracy not validated" if experimental else "Historical yield estimate",
        "warning": (
            "No observed outcomes beyond the saved dataset coverage were evaluated. "
            if experimental else "Holdout metrics describe aggregate performance, not accuracy for this individual estimate. "
        ) + "The model was trained through " + str(policy["train_year_range"][1]) +
        ". Random Forest trees do not extrapolate a year trend beyond training splits; later years may return identical estimates. "
        "No current soil, weather or market inputs are used. This is not a field-specific forecast.",
    }
