# Testing Report — AttendSynth AI

## 1. Overview
This document details the automated testing suite and verification results for **AttendSynth AI**. All tests were executed using `pytest 9.2.0` on Python 3.14.0 Windows environment.

- **Total Test Cases Executed:** 59
- **Passed:** 59
- **Failed:** 0
- **Errors:** 0
- **Pass Rate:** 100%

---

## 2. Test Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\manik\Desktop\java end sem project\AttendSynth AI
collected 59 items

tests/test_generator.py::test_generate_returns_dataframe PASSED          [  1%]
tests/test_generator.py::test_correct_number_of_rows PASSED              [  3%]
tests/test_generator.py::test_required_columns_present PASSED            [  5%]
tests/test_generator.py::test_reproducibility_same_seed PASSED           [  6%]
tests/test_generator.py::test_different_seed_different_data PASSED       [  8%]
tests/test_generator.py::test_unique_student_ids PASSED                  [ 10%]
tests/test_generator.py::test_student_id_format PASSED                   [ 11%]
tests/test_generator.py::test_attendance_pct_range PASSED                [ 13%]
tests/test_generator.py::test_attendance_pct_range_large PASSED          [ 15%]
tests/test_generator.py::test_classes_attended_le_total PASSED           [ 16%]
tests/test_generator.py::test_classes_attended_non_negative PASSED       [ 18%]
tests/test_generator.py::test_engagement_score_range PASSED              [ 20%]
tests/test_generator.py::test_assignment_completion_range PASSED         [ 22%]
tests/test_generator.py::test_academic_performance_range PASSED          [ 23%]
tests/test_generator.py::test_age_range PASSED                           [ 25%]
tests/test_generator.py::test_departments_assigned PASSED                [ 27%]
tests/test_generator.py::test_custom_departments PASSED                  [ 28%]
tests/test_generator.py::test_risk_categories_valid PASSED               [ 30%]
tests/test_generator.py::test_risk_score_range PASSED                    [ 32%]
tests/test_generator.py::test_no_missing_values PASSED                   [ 33%]
tests/test_generator.py::test_minimum_students_clamped PASSED            [ 35%]
tests/test_generator.py::test_maximum_students_clamped PASSED            [ 37%]
tests/test_ml_model.py::test_ml_pipeline_success PASSED                  [ 38%]
tests/test_ml_model.py::test_target_leakage_prevention PASSED            [ 40%]
tests/test_ml_model.py::test_feature_importance_format PASSED            [ 42%]
tests/test_ml_model.py::test_confusion_matrix_shape PASSED               [ 44%]
tests/test_ml_model.py::test_small_dataset_handled PASSED                [ 45%]
tests/test_risk_engine.py::test_risk_distribution_keys PASSED            [ 47%]
tests/test_risk_engine.py::test_risk_distribution_total_matches PASSED   [ 49%]
tests/test_risk_engine.py::test_risk_distribution_counts_sum PASSED      [ 50%]
tests/test_risk_engine.py::test_high_risk_all_high PASSED                [ 52%]
tests/test_risk_engine.py::test_high_risk_is_subset PASSED               [ 54%]
tests/test_risk_engine.py::test_risk_insights_non_empty PASSED           [ 55%]
tests/test_risk_engine.py::test_risk_insights_are_strings PASSED         [ 57%]
tests/test_risk_engine.py::test_contributing_factors_list PASSED         [ 59%]
tests/test_risk_engine.py::test_contributing_factors_all_strings PASSED  [ 61%]
tests/test_risk_engine.py::test_low_risk_scores_below_threshold PASSED   [ 62%]
tests/test_risk_engine.py::test_high_risk_scores_above_threshold PASSED  [ 64%]
tests/test_risk_engine.py::test_csv_export_returns_bytes PASSED          [ 66%]
tests/test_risk_engine.py::test_csv_export_non_empty PASSED              [ 67%]
tests/test_risk_engine.py::test_csv_export_contains_header PASSED        [ 69%]
tests/test_risk_engine.py::test_csv_export_row_count PASSED              [ 71%]
tests/test_risk_engine.py::test_json_export_returns_bytes PASSED         [ 72%]
tests/test_risk_engine.py::test_json_export_valid_json PASSED            [ 74%]
tests/test_risk_engine.py::test_json_export_contains_student_id PASSED   [ 76%]
tests/test_risk_engine.py::test_csv_empty_df PASSED                      [ 77%]
tests/test_risk_engine.py::test_json_empty_df PASSED                     [ 79%]
tests/test_validation.py::test_clean_dataset_passes_all_checks PASSED    [ 81%]
tests/test_validation.py::test_clean_dataset_quality_100 PASSED          [ 83%]
tests/test_validation.py::test_clean_dataset_no_invalid PASSED           [ 84%]
tests/test_validation.py::test_empty_df_returns_zero_quality PASSED      [ 86%]
tests/test_validation.py::test_none_df_handled PASSED                    [ 88%]
tests/test_validation.py::test_detects_invalid_attendance PASSED         [ 89%]
tests/test_validation.py::test_detects_invalid_engagement PASSED         [ 91%]
tests/test_validation.py::test_detects_duplicate_ids PASSED              [ 93%]
tests/test_validation.py::test_detects_classes_exceeded PASSED           [ 94%]
tests/test_validation.py::test_detects_invalid_risk_category PASSED      [ 96%]
tests/test_validation.py::test_summary_keys_present PASSED               [ 98%]
tests/test_validation.py::test_checks_list_non_empty PASSED              [100%]

================== 59 passed, 1 warning in 275.20s (0:04:35) ==================
```

---

## 3. Test Modules Breakdown

### Module 1: `test_generator.py` (22 tests)
- **Data Structure:** Verifies generated objects are valid `pd.DataFrame` instances with all 17 schema columns present.
- **Reproducibility:** Asserts that identical seeds produce bitwise-identical datasets, and distinct seeds yield varying distributions.
- **Identity & Formatting:** Asserts zero duplicate IDs and validates `STU-XXXXX` format.
- **Mathematical Invariants:** Enforces $0 \le A_i \le 100$, $0 \le c_i \le C_i$, and verified that attended classes never exceed total classes.
- **Metric Boundaries:** Validates bounds on engagement (0–100), assignments (0–100), academic performance (0–100), and ages (17–26).
- **Cohort Clamping:** Asserts input bounds clamping at minimum (50) and maximum (10,000) student thresholds.

### Module 2: `test_ml_model.py` (5 tests)
- **Pipeline Execution:** Confirms successful training of Random Forest classifier and generation of precision, recall, and macro F1 scores.
- **Target Leakage Prevention:** Verifies that neither `risk_score` nor `risk_category` appear in the input feature set.
- **Model Output Formatting:** Validates confusion matrix shape matching class dimensions and checks feature importance sum equals 1.0.
- **Fault Tolerance:** Asserts graceful handling of small cohorts without unhandled exceptions.

### Module 3: `test_risk_engine.py` (20 tests)
- **Heuristic Distribution:** Asserts proper calculation of high, medium, and low risk totals and percentages summing to cohort count.
- **High-Risk Subsets:** Verifies filtered high-risk records contain exclusively high-risk labeled students.
- **Explainability:** Asserts risk factors and automated textual insights generate clean, non-empty natural language strings.
- **Data Export Serialization:** Validates byte output, header structure, and row counts for CSV and JSON exporters, including handling of empty DataFrames.

### Module 4: `test_validation.py` (12 tests)
- **Clean Baseline:** Verifies generated cohorts achieve 100% quality scores with zero invalid records.
- **Fault Injection:** Injects deliberate anomalies (attendance $> 100\%$, engagement $< 0$, duplicate IDs, classes attended $>$ total classes, invalid risk labels) and verifies that corresponding checks capture them.
- **Empty & Null Safety:** Tests resilience against `None` and empty DataFrames.

---

## 4. Conclusion
The comprehensive test suite confirms that AttendSynth AI meets all mathematical, data engineering, machine learning, and architectural standards.
