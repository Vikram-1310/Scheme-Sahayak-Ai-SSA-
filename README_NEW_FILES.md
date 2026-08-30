# SIH26092 — New/Updated AI Backend Files

These files implement SC-beneficiary scheme matching on top of your
existing 4693-row Schemes.csv dataset.

## How to use

1. Copy the `ai/` folder contents into your existing `SIH26092/ai/` folder,
   overwriting the files listed below. Your `.venv`, `ai_engine.py`,
   `__init__.py` (if you already have real content in it) and any other
   files not listed here are left untouched — do NOT overwrite your
   existing `ai_engine.py`.

Files included:
- ai/state_normalizer.py       (NEW)
- ai/caste_normalizer.py       (NEW)
- ai/business_normalizer.py    (NEW)
- ai/purpose_normalizer.py     (NEW)
- ai/financial_parser.py       (NEW)
- ai/scheme_models.py          (REPLACE)
- ai/scheme_importer.py        (REPLACE)
- ai/scheme_source.py          (REPLACE)
- ai/matching_engine.py        (REPLACE)
- ai/eligibility_engine.py     (REPLACE)
- ai/scheme_recommender.py     (REPLACE)
- ai/recommendation_service.py (NEW)
- ai/api_models.py             (NEW)
- ai/main.py                   (REPLACE — but re-check the
                                 `_run_ai_engine()` function against your
                                 real ai_engine.py's function name)
- ai/tests/test_scheme_system.py (NEW)

An empty `ai/__init__.py` is included in case you don't already have one;
if you already have one with content, keep yours instead.

## Run

From the project root (SIH26092/):

```
.\ai\.venv\Scripts\python.exe -m uvicorn ai.main:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000/docs

## Test

```
.\ai\.venv\Scripts\python.exe -m pytest ai/tests/test_scheme_system.py -v
```

## Important note

`ai/main.py`'s `_run_ai_engine()` function tries several common function
names (`process_message`, `handle_chat`, `chat`, `process_chat`, `run`) to
call your existing `ai_engine.py`. If none of these match your actual
function name/signature, edit that one function to call yours directly —
nothing else in this package depends on it.
