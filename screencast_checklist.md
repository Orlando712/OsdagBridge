# OsdagBridge Screening Task — GUI Screencast Recording Checklist

**Target Video Length:** 3–5 minutes (Single continuous screencast)  
**Host Platform:** macOS (Apple Silicon) &nbsp;|&nbsp; **Environment:** `osdagbridge-env`  
**Launch Command:**
```bash
conda activate osdagbridge-env
python -m osdagbridge.desktop
```

---

### Step 1: Baseline Bridge Run (30 m Span, 34.45 m Width, 5.12 m Spacing)
1. **Module Selection:** On the homepage, click **Plate Girder Bridge**.
2. **Project Location:**
   - Click the map / location selector icon.
   - Choose State: **Andhra Pradesh**, District/City: **Kakinada** (Wind Speed $V_b = 50\text{ m/s}$, Zone III, $Z=0.16$). Click **Apply**.
3. **Input Dock Entries:**
   - **Span (m):** `30`
   - **Carriageway Width (m):** `15.0`
   - **Include Median:** `Yes`
   - **Footpath:** `Both Sides`
   - **Skew Angle (°):** `10`
   - **Design Mode:** `Optimized`
   - **Materials:** Girder `E 350A`, Cross Bracing `E 350A`, End Diaphragm `E 350A`, Deck Concrete `M40`.
4. **Typical Section Verification:**
   - Click **Additional Inputs** $\rightarrow$ navigate to **Typical Section** tab.
   - Confirm / enter:
     - **Number of Girders:** `7`
     - **Girder Spacing:** `5.12` m
     - **Overall Bridge Width:** `34.45` m (with Footpath width `0.80` m or default curb dimensions).
   - Click **Save / Close**.
5. **Execution & Evidence:**
   - Click **Design**.
   - **Record 3D CAD Window:** Orbit (left-drag), pan, and zoom the generated 3D solid model showing 7 wide-spaced plate girders.
   - **Record Output Dock:**
     - Observe the initial state of the DCR bars (empty under `Envelope`).
     - In the Load Case combo box, switch from `Envelope` to `Design Envelope`: record the DCR progress bars populating with numerical percentages.
   - **Record Plots Dock:** Click the **Plots** icon on the dock sidebar to display the BMD, SFD, and Grillage Mesh views.

---

### Step 2: Consecutive Run 2 — Span Change (30 m $\rightarrow$ 32 m in Same Session)
1. **Unlock Project:** Click the **Unlock** padlock icon on the Input Dock and confirm the prompt.
2. **Modify Span:** Change **Span (m)** from `30` to `32`.
3. **Re-run Design:** Click **Design**.
4. **Record Observations:**
   - Record the 3D CAD model updating to 32 m length.
   - *(Check Issue 1 in GUI)*: Open Additional Inputs $\rightarrow$ Member Properties $\rightarrow$ Girder Details $\rightarrow$ Segment Table for G1. Observe whether the segment end updated to `32.0` m or remained at `30.0` m.

---

### Step 3: Consecutive Run 3 — Custom Steel & Concrete Inputs
1. **Unlock Project:** Click **Unlock** on the Input Dock.
2. **Define Custom Steel:**
   - In **Girder Steel Grade** combo, select **Custom...**
   - In the dialog, enter:
     - Yield Strength ($f_y$): `450.0`
     - Ultimate Tensile Strength ($f_u$): `570.0`
     - Modulus of Elasticity ($E$): `210.0`
   - Click **Save**.
3. **Define Custom Deck Concrete:**
   - In **Deck Concrete Grade** combo, select **Custom...**
   - In the dialog, enter:
     - Characteristic Compressive Strength ($f_{ck}$): `50.0`
   - Click **Save**.
4. **Re-run Design:** Click **Design** and record the updated results.

---

### Step 4: Reopening Saved Material in Edit Mode (Testing Issue 2)
1. **Unlock Project:** Click **Unlock**.
2. **Reopen Custom Material Dialog in Edit Mode:**
   - Click the **Girder Steel Grade** or **Deck Concrete Grade** combo box and select **Custom...** again to edit the custom material.
   - **RECORD CAREFULLY:** Observe whether the text boxes display:
     - **A:** Your previously entered custom values ($f_y = 450\text{ MPa}$ / $f_{ck} = 50\text{ MPa}$), OR
     - **B:** Standard default values ($f_y = 250\text{ MPa}$ / $f_{ck} = 40\text{ MPa}$).
   - This single observation will definitively confirm or clear the latent edit-dialog pre-population defect.

---

### Step 5: Report Generation Limitation & Project Save
1. **Test Calculation Report Export:**
   - Click the **Design Report** icon on the toolbar.
   - Click **Generate / Preview**.
   - Record the resulting notice (LaTeX `.tex` generated, `pdflatex` missing limitation on Mac).
2. **Save Project State:**
   - Click menu **File $\rightarrow$ Save Inputs (.osi)**.
   - Save the session file as `kakinada_screening_test.osi`.
