"""
generator.py — Core synthetic student data generation engine for AttendSynth AI.

Design principle:
  Each student is first assigned a *latent behavioural profile* drawn from
  the user-specified distribution.  Every correlated field is then derived
  from that profile so that the dataset exhibits realistic statistical
  relationships rather than independent random noise.

  Pipeline:
    behavioural_profile
        → attendance_pct
        → engagement_base
        → assignment_completion, participation, platform_activity
        → engagement_score
        → academic_performance_score
        → risk_score → risk_category
"""

import numpy as np
import pandas as pd
from faker import Faker
from typing import Dict, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _bounded(values: np.ndarray, low: float, high: float) -> np.ndarray:
    """Clip an array to [low, high] and return as float rounded to 2 dp."""
    return np.clip(np.round(values, 2), low, high)


def _normal_bounded(rng: np.random.Generator,
                    mean: float, std: float,
                    low: float, high: float,
                    n: int) -> np.ndarray:
    """Draw n samples from a normal distribution, bounded to [low, high]."""
    raw = rng.normal(loc=mean, scale=std, size=n)
    return _bounded(raw, low, high)


def _generate_student_ids(n: int, rng: np.random.Generator) -> List[str]:
    """Generate n unique synthetic student IDs like STU-20240001."""
    base = rng.choice(range(10_000, 99_999), size=n, replace=False)
    return [f"STU-{x}" for x in base]


def _assign_departments(n: int,
                        departments: List[str],
                        rng: np.random.Generator) -> np.ndarray:
    """Randomly assign departments with roughly equal probability."""
    return rng.choice(departments, size=n)


def _assign_behavioural_pattern(n: int,
                                 distribution: Dict[str, float],
                                 rng: np.random.Generator) -> np.ndarray:
    """
    Sample a behavioural attendance pattern label for each student.
    distribution = {"Regular": 0.4, "Moderate": 0.3, ...}
    """
    patterns = list(distribution.keys())
    probs = np.array(list(distribution.values()), dtype=float)
    probs = probs / probs.sum()           # normalise just in case
    return rng.choice(patterns, size=n, p=probs)


def _derive_attendance(patterns: np.ndarray,
                        rng: np.random.Generator) -> np.ndarray:
    """
    For each student, draw attendance % from a bounded normal distribution
    whose mean and std depend on the student's behavioural pattern.
    """
    att = np.zeros(len(patterns))
    ranges = config.ATTENDANCE_RANGES        # e.g. Regular: (82, 100)

    for pattern, (lo, hi) in ranges.items():
        mask = (patterns == pattern)
        n_p  = mask.sum()
        if n_p == 0:
            continue
        mid  = (lo + hi) / 2
        std  = (hi - lo) / 6              # ~3-sigma covers the range
        att[mask] = _normal_bounded(rng, mid, std, lo, hi, n_p)

    return np.round(att, 2)


def _derive_engagement_components(attendance: np.ndarray,
                                   rng: np.random.Generator
                                   ) -> Dict[str, np.ndarray]:
    """
    Derive correlated engagement components from attendance percentage.
    Returns assignment_completion, platform_activity, participation_score.
    """
    n = len(attendance)

    # Shared noise correlated to attendance
    base = attendance / 100.0            # 0-1 scale

    # Assignment completion: strong positive correlation with attendance
    asgn_mean = 15 + base * 75          # range 15-90 roughly
    asgn_noise = rng.normal(0, 8, n)
    assignment_completion = _bounded(np.round(asgn_mean + asgn_noise, 2), 0, 100)

    # Learning platform activity (0-100 score)
    plat_mean = 10 + base * 80
    plat_noise = rng.normal(0, 10, n)
    platform_activity = _bounded(np.round(plat_mean + plat_noise, 2), 0, 100)

    # Participation score (0-100)
    part_mean = 10 + base * 70
    part_noise = rng.normal(0, 12, n)
    participation_score = _bounded(np.round(part_mean + part_noise, 2), 0, 100)

    return {
        "assignment_completion": assignment_completion,
        "platform_activity":     platform_activity,
        "participation_score":   participation_score,
    }


def _compute_engagement_score(assignment_completion: np.ndarray,
                               platform_activity: np.ndarray,
                               participation_score: np.ndarray) -> np.ndarray:
    """
    Composite engagement score (0-100):
      40 % assignment + 35 % platform + 25 % participation
    """
    score = (0.40 * assignment_completion
             + 0.35 * platform_activity
             + 0.25 * participation_score)
    return _bounded(np.round(score, 2), 0, 100)


def _compute_academic_performance(attendance: np.ndarray,
                                   engagement_score: np.ndarray,
                                   assignment_completion: np.ndarray,
                                   rng: np.random.Generator) -> np.ndarray:
    """
    Academic performance (0-100) is a weighted combination with small noise.
      50 % engagement + 30 % attendance + 20 % assignment
    """
    base = (0.50 * engagement_score
            + 0.30 * attendance
            + 0.20 * assignment_completion)
    noise = rng.normal(0, 5, len(attendance))
    return _bounded(np.round(base + noise, 2), 0, 100)


def _compute_risk_score(attendance: np.ndarray,
                         engagement_score: np.ndarray,
                         assignment_completion: np.ndarray,
                         academic_performance: np.ndarray) -> np.ndarray:
    """
    Risk score 0-100 (higher = more at risk).

    Formula:
        risk = 100 - (w_att*att + w_eng*eng + w_asgn*asgn + w_acad*acad)
    """
    w = config.RISK_WEIGHTS
    positive_index = (w["attendance"]   * attendance
                      + w["engagement"] * engagement_score
                      + w["assignment"] * assignment_completion
                      + w["academic_perf"] * academic_performance)
    risk = 100.0 - positive_index
    return _bounded(np.round(risk, 2), 0, 100)


def _assign_risk_category(risk_scores: np.ndarray) -> np.ndarray:
    """Map numeric risk score to categorical label."""
    categories = np.where(
        risk_scores < config.RISK_LOW_MAX,  "Low",
        np.where(risk_scores < config.RISK_MEDIUM_MAX, "Medium", "High")
    )
    return categories


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_dataset(
    n_students:              int             = config.DEFAULT_N_STUDENTS,
    departments:             Optional[List[str]] = None,
    academic_year:           str             = config.DEFAULT_ACADEMIC_YEAR,
    semester:                str             = config.DEFAULT_SEMESTER,
    attendance_distribution: Optional[Dict[str, float]] = None,
    seed:                    int             = config.DEFAULT_SEED,
) -> pd.DataFrame:
    """
    Generate a synthetic student engagement dataset.

    Parameters
    ----------
    n_students : int
        Number of student records to generate (50 – 10 000).
    departments : list of str, optional
        Department names to assign.  Defaults to config.DEFAULT_DEPARTMENTS.
    academic_year : str
        Academic year label, e.g. "2024-25".
    semester : str
        Semester label, e.g. "Odd" or "Even".
    attendance_distribution : dict, optional
        Mapping of pattern label → proportion.
        Defaults to config.DEFAULT_ATTENDANCE_DISTRIBUTION.
    seed : int
        Random seed for full reproducibility.

    Returns
    -------
    pd.DataFrame with one row per student and all required columns.
    """
    # Validate inputs
    n_students = max(50, min(10_000, int(n_students)))

    if departments is None or len(departments) == 0:
        departments = config.DEFAULT_DEPARTMENTS

    if attendance_distribution is None:
        attendance_distribution = config.DEFAULT_ATTENDANCE_DISTRIBUTION

    # Initialise reproducible RNG
    rng  = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)

    # --- Step 1: Student identifiers ---
    student_ids = _generate_student_ids(n_students, rng)
    ages        = rng.integers(config.AGE_RANGE[0], config.AGE_RANGE[1] + 1, n_students)
    dept_col    = _assign_departments(n_students, departments, rng)
    yr_col      = rng.choice(["1st Year", "2nd Year", "3rd Year", "4th Year"], n_students)
    total_cls   = rng.integers(config.TOTAL_CLASSES_RANGE[0],
                               config.TOTAL_CLASSES_RANGE[1] + 1,
                               n_students)

    # --- Step 2: Behavioural profile ---
    patterns = _assign_behavioural_pattern(n_students, attendance_distribution, rng)

    # --- Step 3: Attendance ---
    attendance_pct = _derive_attendance(patterns, rng)
    classes_attended = np.minimum(
        np.round(total_cls * attendance_pct / 100).astype(int),
        total_cls
    )
    # Recalculate percentage from integer class count for consistency
    attendance_pct_recalc = np.round(classes_attended / total_cls * 100, 2)

    # --- Step 4: Engagement components ---
    eng_components = _derive_engagement_components(attendance_pct_recalc, rng)

    # --- Step 5: Composite engagement ---
    engagement_score = _compute_engagement_score(
        eng_components["assignment_completion"],
        eng_components["platform_activity"],
        eng_components["participation_score"],
    )

    # --- Step 6: Academic performance ---
    academic_performance = _compute_academic_performance(
        attendance_pct_recalc,
        engagement_score,
        eng_components["assignment_completion"],
        rng,
    )

    # --- Step 7: Risk ---
    risk_score    = _compute_risk_score(
        attendance_pct_recalc,
        engagement_score,
        eng_components["assignment_completion"],
        academic_performance,
    )
    risk_category = _assign_risk_category(risk_score)

    # --- Assemble DataFrame ---
    df = pd.DataFrame({
        "student_id":                      student_ids,
        "age":                             ages.astype(int),
        "department":                      dept_col,
        "academic_year":                   academic_year,
        "year_of_study":                   yr_col,
        "semester":                        semester,
        "attendance_pattern":              patterns,
        "total_classes":                   total_cls.astype(int),
        "classes_attended":                classes_attended,
        "attendance_percentage":           attendance_pct_recalc,
        "assignment_completion_percentage":eng_components["assignment_completion"],
        "learning_platform_activity":      eng_components["platform_activity"],
        "participation_score":             eng_components["participation_score"],
        "engagement_score":                engagement_score,
        "academic_performance_score":      academic_performance,
        "risk_score":                      risk_score,
        "risk_category":                   risk_category,
    })

    return df
