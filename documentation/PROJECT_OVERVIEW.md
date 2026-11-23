# Project Overview — AttendSynth AI

## 1. Executive Summary
**AttendSynth AI** is an advanced educational data generation platform engineered to synthesize realistic, correlated student engagement and attendance data. Its primary mission is to eliminate the data access and privacy barriers that impede the development of academic early-warning systems, retention models, and instructional analytics.

---

## 2. Core Problem
Institutions seeking to develop data-driven student intervention frameworks face significant obstacles:
- **Privacy Legislation (FERPA / GDPR):** Real student records cannot be distributed to developers or external researchers without extensive de-identification and legal reviews.
- **Cold-Start Problem:** New programs or modern learning management system (LMS) deployments lack longitudinal behavioral tracking.
- **Synthetic Data Quality Gap:** Rudimentary random mock data generators produce uncorrelated attributes (e.g., zero attendance with high grades), rendering predictive models trained on such data unrepresentative and unstable.

---

## 3. The AttendSynth AI Solution
AttendSynth AI bridges this gap through a multi-tier behavioral synthesis engine that:
1. Samples latent student behaviors (`Regular`, `Moderate`, `Irregular`, `Low`).
2. Generates interdependent indicators including attendance percentage, LMS activity hours, participation scores, and assignment completion.
3. Formulates transparent academic performance and rule-based risk indices.
4. Validates data integrity automatically across 11 critical consistency checks.
5. Provides an interactive Streamlit environment complete with analytics, early-warning profiling, machine learning demonstration, and export tools.

---

## 4. Key Target Audiences
- **Educational Researchers:** Investigating engagement patterns without requiring Institutional Review Board (IRB) waivers.
- **EdTech Software Engineers:** Prototyping student information systems (SIS) and early-warning dashboards.
- **Data Science Educators:** Providing student cohorts for classroom projects without distributing student private records.
- **Institutional Analysts:** Stress-testing analytics pipelines against various cohort size and risk scenarios.

---

## 5. Summary of Application Modules
1. **Home Dashboard:** High-level cohort KPIs and recent generation parameters.
2. **Synthetic Data Generator:** Parameter controls for cohort size (50–10,000), academic terms, and distribution ratios.
3. **Dataset Explorer:** Dynamic tabular browser with multi-attribute filtering and search.
4. **Analytics Dashboard:** Multi-dimensional Plotly visualizations and automated insight extraction.
5. **Early Warning Analysis:** Transparent heuristic risk calculation and individual factor diagnosis.
6. **Machine Learning Demonstration:** Benchmark Random Forest risk tier classifier with performance metrics and feature importances.
7. **Data Quality Report:** Comprehensive automated audit reporting on missingness, consistency, and bounds.
8. **Export Center:** One-click CSV and JSON exports of full and filtered cohorts.
9. **About Project:** System architecture, methodology documentation, and usage guidelines.
