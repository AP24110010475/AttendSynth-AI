# Synthetic Data Generation Methodology

## 1. Overview
Realistic synthetic data generation requires modeling the underlying joint distributions and dependencies observed in academic environments. AttendSynth AI uses a **hierarchical behavioral generation model** rather than independent random sampling.

---

## 2. Generation Stages

### Stage 1: Demographics and Baseline Setup
- **Student ID:** Synthesized with a unique prefix format `STU-XXXXX` drawn without replacement from a space of 90,000 values.
- **Age:** Sampled uniformly from collegiate bounds $[17, 26]$.
- **Department:** Distributed uniformly across configured departments.
- **Academic Year & Semester:** Assigned as configured by the user.
- **Total Classes:** Drawn uniformly from $[60, 90]$.

### Stage 2: Latent Behavioral Pattern Assignment
Each student is assigned a latent behavioral profile $P_i$:
- `Regular` (Default: 40%)
- `Moderate` (Default: 30%)
- `Irregular` (Default: 20%)
- `Low` (Default: 10%)

### Stage 3: Attendance Modeling
For each pattern, attendance percentage $A_i$ is drawn from a bounded normal distribution:

$$\mu_P = \frac{L_P + U_P}{2}, \quad \sigma_P = \frac{U_P - L_P}{6}$$

Where $[L_P, U_P]$ are defined as:
- Regular: $[82\%, 100\%]$
- Moderate: $[63\%, 85\%]$
- Irregular: $[42\%, 65\%]$
- Low: $[18\%, 45\%]$

Integer classes attended $c_i$ is computed:
$$c_i = \min\left(\left\lfloor \frac{C_i \cdot A_i}{100} + 0.5 \right\rfloor, C_i\right)$$
Attendance percentage is then updated to $c_i / C_i \times 100$, ensuring total mathematical consistency.

### Stage 4: Engagement Components Simulation
Engagement metrics correlate directly with student attendance:
- **Assignment Completion (%):**
  $$\text{Asgn}_i = \text{clip}(15 + 0.75 \cdot A_i + \mathcal{N}(0, 8^2), 0, 100)$$
- **Learning Platform Activity (0–100 score):**
  $$\text{Plat}_i = \text{clip}(10 + 0.80 \cdot A_i + \mathcal{N}(0, 10^2), 0, 100)$$
- **Participation Score (0–100 score):**
  $$\text{Part}_i = \text{clip}(10 + 0.70 \cdot A_i + \mathcal{N}(0, 12^2), 0, 100)$$

### Stage 5: Composite Engagement Score
$$\text{Eng}_i = 0.40 \cdot \text{Asgn}_i + 0.35 \cdot \text{Plat}_i + 0.25 \cdot \text{Part}_i$$

### Stage 6: Academic Performance Score
Academic performance is determined primarily by engagement and attendance, with bounded Gaussian noise:
$$\text{Acad}_i = \text{clip}(0.50 \cdot \text{Eng}_i + 0.30 \cdot A_i + 0.20 \cdot \text{Asgn}_i + \mathcal{N}(0, 5^2), 0, 100)$$

### Stage 7: Rule-Based Early Warning Risk Scoring
$$\text{Positive Index}_i = 0.35 \cdot A_i + 0.25 \cdot \text{Eng}_i + 0.25 \cdot \text{Asgn}_i + 0.15 \cdot \text{Acad}_i$$
$$\text{Risk Score}_i = 100 - \text{Positive Index}_i$$

- **Low Risk:** $< 35$
- **Medium Risk:** $[35, 60)$
- **High Risk:** $\ge 60$
