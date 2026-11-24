"""
config.py — App-wide constants and default configuration for AttendSynth AI.
"""

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_TITLE = "AttendSynth AI"
APP_SUBTITLE = "Synthetic Student Engagement Generator"
APP_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Data generation defaults
# ---------------------------------------------------------------------------
DEFAULT_N_STUDENTS = 300
DEFAULT_SEED = 42
DEFAULT_ACADEMIC_YEAR = "2024-25"
DEFAULT_SEMESTER = "Odd"

DEFAULT_DEPARTMENTS = [
    "Computer Science",
    "Electronics",
    "Mechanical",
    "Civil",
    "Business Administration",
]

# Attendance behavioural pattern mix (must sum to 1.0)
DEFAULT_ATTENDANCE_DISTRIBUTION = {
    "Regular":     0.40,   # attendance 85-100 %
    "Moderate":    0.30,   # attendance 65-85 %
    "Irregular":   0.20,   # attendance 45-65 %
    "Low":         0.10,   # attendance 20-45 %
}

# Engagement behavioural pattern mix (must sum to 1.0)
DEFAULT_ENGAGEMENT_DISTRIBUTION = {
    "High":   0.35,
    "Medium": 0.45,
    "Low":    0.20,
}

# ---------------------------------------------------------------------------
# Field value ranges
# ---------------------------------------------------------------------------
AGE_RANGE = (17, 26)
TOTAL_CLASSES_RANGE = (60, 90)

# Attendance % ranges per behavioural pattern
ATTENDANCE_RANGES = {
    "Regular":   (82, 100),
    "Moderate":  (63, 85),
    "Irregular": (42, 65),
    "Low":       (18, 45),
}

# Engagement score 0-100
ENGAGEMENT_SCORE_RANGE = (0, 100)

# Academic performance 0-100
ACADEMIC_PERFORMANCE_RANGE = (0, 100)

# Risk score 0-100 (higher = more at risk)
RISK_SCORE_RANGE = (0, 100)

# ---------------------------------------------------------------------------
# Risk thresholds
# ---------------------------------------------------------------------------
RISK_LOW_MAX = 35       # risk_score < 35  → Low
RISK_MEDIUM_MAX = 60    # 35 ≤ score < 60  → Medium
                        # score ≥ 60        → High

RISK_CATEGORIES = ["Low", "Medium", "High"]

# ---------------------------------------------------------------------------
# Risk score formula weights (must sum to 1.0)
# ---------------------------------------------------------------------------
RISK_WEIGHTS = {
    "attendance":        0.35,
    "engagement":        0.25,
    "assignment":        0.25,
    "academic_perf":     0.15,
}

# ---------------------------------------------------------------------------
# ML model settings
# ---------------------------------------------------------------------------
ML_TEST_SIZE = 0.25
ML_N_ESTIMATORS = 100
ML_RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# Export filenames
# ---------------------------------------------------------------------------
EXPORT_CSV_FULL = "attendsynth_dataset_full.csv"
EXPORT_JSON_FULL = "attendsynth_dataset_full.json"
EXPORT_CSV_FILTERED = "attendsynth_dataset_filtered.csv"
EXPORT_QUALITY_REPORT = "attendsynth_quality_report.csv"

# ---------------------------------------------------------------------------
# UI colour palette (used in Plotly charts & UI accents)
# ---------------------------------------------------------------------------
COLOUR_PRIMARY   = "#3B82F6"   # primary blue
COLOUR_SECONDARY = "#60A5FA"   # secondary blue
COLOUR_TEAL      = "#14B8A6"   # accent teal
COLOUR_SUCCESS   = "#10B981"   # restrained green (low risk)
COLOUR_WARNING   = "#F59E0B"   # restrained amber (medium risk)
COLOUR_DANGER    = "#EF4444"   # restrained red (high risk)
COLOUR_NEUTRAL   = "#6B7280"   # secondary text grey

RISK_COLOURS = {
    "Low":    COLOUR_SUCCESS,
    "Medium": COLOUR_WARNING,
    "High":   COLOUR_DANGER,
}

CHART_TEMPLATE = "plotly_white"
