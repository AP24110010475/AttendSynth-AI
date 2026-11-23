# Deployment Guide — Streamlit Community Cloud

This guide explains how to deploy **AttendSynth AI** directly to **Streamlit Community Cloud** from a GitHub repository.

---

## Step 1: Create a GitHub Repository
1. Log in to [GitHub](https://github.com).
2. Click **New Repository** in the top right corner.
3. Name your repository: `attendsynth-ai`.
4. Choose **Public** (required for free Streamlit Community Cloud hosting).
5. Leave "Initialize this repository with a README" unchecked (since we already have a full project).
6. Click **Create repository**.

---

## Step 2: Push Local Files to GitHub
Open your terminal in the `AttendSynth AI` project folder and run:

```bash
# Initialize git if not already initialized
git init

# Add all files
git add .

# Create the initial commit
git commit -m "Initial release of AttendSynth AI"

# Set branch name to main
git branch -M main

# Link to your remote GitHub repository
git remote add origin https://github.com/<your-username>/attendsynth-ai.git

# Push the code
git push -u origin main
```

---

## Step 3: Access Streamlit Community Cloud
1. Navigate to [share.streamlit.io](https://share.streamlit.io).
2. Sign in using your GitHub account credentials.
3. Authorize Streamlit to access your repositories if prompted.

---

## Step 4: Configure the New App Deployment
1. On your Streamlit Cloud workspace, click **Create app**.
2. Select **I have an existing app**.
3. Fill in the deployment form:
   - **Repository:** `<your-username>/attendsynth-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** Choose a custom subdomain like `attendsynth-ai.streamlit.app`.
4. Click **Advanced settings** (optional): Ensure Python 3.11+ is selected.

---

## Step 5: Deploy the Application
1. Click the **Deploy!** button.
2. Streamlit Cloud will:
   - Clone your repository.
   - Install packages specified in `requirements.txt`.
   - Launch `app.py`.
3. The build logs will stream in real time. Once ready, the app will open at your URL.

---

## Step 6: Post-Deployment Verification Checklist
- [ ] Verify that the **Home Dashboard** renders with default KPI indicators.
- [ ] Navigate to **1. Synthetic Data Generator**, set student count to 200, and click **Generate Dataset**.
- [ ] Check **2. Dataset Explorer** to confirm table filtering and search work.
- [ ] Inspect **3. Analytics Dashboard** to verify Plotly charts render properly.
- [ ] Review **4. Early Warning Analysis** to confirm risk category breakdowns.
- [ ] Test **5. Machine Learning** by running the Random Forest classifier.
- [ ] Confirm **6. Data Quality Report** shows 100% data quality score.
- [ ] Test CSV and JSON downloads in **7. Export Center**.
