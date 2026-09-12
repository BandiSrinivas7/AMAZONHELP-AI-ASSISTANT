from __future__ import annotations

import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline


def train(texts, labels, path):
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=.98,
            sublinear_tf=True
        )),
        ("clf", OneVsRestClassifier(
            LogisticRegression(
                max_iter=300,
                class_weight="balanced",
                solver="liblinear",
                C=2.0,
            )
        )),
    ])

    pipe.fit(texts, labels)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, path)

    return pipe


def _make_old_sklearn_model_compatible(model):
    clf = getattr(model, "named_steps", {}).get("clf")

    if isinstance(clf, OneVsRestClassifier):
        for estimator in getattr(clf, "estimators_", []):
            if (
                isinstance(estimator, LogisticRegression)
                and not hasattr(estimator, "multi_class")
            ):
                estimator.multi_class = "ovr"

    elif isinstance(clf, LogisticRegression):
        if not hasattr(clf, "multi_class"):
            clf.multi_class = "ovr"

    return model


def predict(model, text):
    try:
        p = model.predict_proba([text])[0]
        classes = model.classes_
        i = int(p.argmax())

        return str(classes[i]), float(p[i])

    except AttributeError as exc:
        if "multi_class" not in str(exc):
            raise

        model = _make_old_sklearn_model_compatible(model)

        p = model.predict_proba([text])[0]
        classes = model.classes_
        i = int(p.argmax())

        return str(classes[i]), float(p[i])