# GitHub Issue 1: Stale Girder Segment Table in Consecutive Runs When Span is Modified

**Repository:** `https://github.com/Orlando712/OsdagBridge.git` (upstream fork: `Nidhikhare12/OsdagBridge.git`)  
**Branch:** `dev`  
**Commit SHA:** `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`  
**Test Case File:** `test_cases/kakinada_run2_span32m.osi` (and `evidence/run2_input_before_design.json`)  
**Issue Title:** `[Bug] Girder segment table retains stale span length in consecutive runs after span is modified`  
**Labels:** `bug`, `core`, `state-management`, `CAD`, `sizing`  
**Severity:** High  
**Status:** **CONFIRMED BUG**  
**Upstream Issue:** Matches upstream [#168](https://github.com/Nidhikhare12/OsdagBridge/issues/168)  
**Verification Comment:** [Issue #168 Comment #7101687339](https://github.com/Nidhikhare12/OsdagBridge/issues/168#issuecomment-7101687339) (macOS Apple Silicon independent verification)  
**Screencast Video:** [https://youtu.be/HB8rdGHgBVs](https://youtu.be/HB8rdGHgBVs) (Timestamp ~1:15-2:10)

---

### 1. Description
In OsdagBridge, when a user completes a design run, unlocks the project in the desktop GUI (which calls `backend.reset()`), modifies the bridge span (e.g. from 30.0 m to 32.0 m), and re-triggers the design execution, the girder segment tables (`member_properties.girder_details.segment_table.G{n}`) retain the previous span length (`end = 30.0`) instead of updating to the new span (`end = 32.0`).

This causes a severe geometry mismatch across subsystems:
1. **Grillage FEA Analysis:** The grillage mesh and node coordinates are generated for the updated $32.0\text{ m}$ span.
2. **Member Sizing & CAD Solids:** Sizing and segment definitions retain $L = 30.0\text{ m}$. As a result, downstream 3D CAD builders and drawing generators construct girder plates only up to $30.0\text{ m}$, leaving an un-modeled $2.0\text{ m}$ gap/overhang and misaligned bearing support locations.

---

### 2. Steps to Reproduce
1. Launch OsdagBridge:
   ```bash
   conda activate osdagbridge-env
   python -m osdagbridge.desktop
   ```
2. On the home page, select **Plate Girder Bridge**.
3. Set **Span (m)** to `30.0`, configure baseline fields (Kakinada AP, 15 m Carriageway, Median Yes, Footpaths Both Sides, E 350A, M40), and click **Design**.
4. Inspect `input_dict["member_properties.girder_details.segment_table.G1"]`:
   ```json
   [{"id": "G1M1", "start": 0.0, "end": 30.0}]
   ```
5. Click **Unlock** on the Input Dock and confirm the warning dialog.
6. Change **Span (m)** from `30` to `32`.
7. Click **Design** (or trigger `solve_extend_basic_input_dict(input_dict)`).
8. Inspect `input_dict["member_properties.girder_details.segment_table.G1"]` (or open **Additional Inputs $\rightarrow$ Member Properties $\rightarrow$ Girder Details $\rightarrow$ Segment Table** in the GUI).

---

### 3. Expected vs. Actual Values

| Parameter | Key | Expected Value (Run 2) | Actual Observed Value (Run 2) | Discrepancy Status |
| :--- | :--- | :--- | :--- | :--- |
| **Bridge Span** | `geometry.span` | `32.0` m | `32.0` m | Correctly updated |
| **CAD Span Parameter**| `cad_params.span_length_L` | `32000.0` mm | `32000.0` mm | Correctly updated |
| **Girder Depth ($D$)**| `member_properties.girder_depth.G1.M1` | `1780` mm | `1780` mm | Dynamically resized |
| **G1 Segment 1 End** | `member_properties.girder_details.segment_table.G1[0]['end']` | **`32.0` m** | **`30.0` m** | **FAIL: Stale data retained from Run 1!** |
| **G2 Segment 1 End** | `member_properties.girder_details.segment_table.G2[0]['end']` | **`32.0` m** | **`30.0` m** | **FAIL: Stale data retained from Run 1!** |
| **All Girders $G_n$** | `segment_table.G{n}[0]['end']` | **`32.0` m** | **`30.0` m** | **FAIL: All girder segment ends stale!** |

---

### 4. Root Cause Analysis
In `src/osdagbridge/core/bridge_types/plate_girder/defaults.py`, inside `_on_no_of_girders_changed(working_input_dict)`:

```python
# defaults.py: Lines 552-558 (Commit d74f56dd7f22925fb8148cabf5740ed8d1e39ff3)
for girder_idx in range(1, count + 1):
    working_input_dict[f"{KEY_MP_GD_SELECT_GIRDER}.G{girder_idx}"] = f"G{girder_idx}"
    seg_table_key = f"{KEY_MP_GD_SEGMENT_TABLE}.G{girder_idx}"
    if seg_table_key not in working_input_dict:
        working_input_dict[seg_table_key] = [
            {"id": f"G{girder_idx}M1", "start": 0.0, "end": span}
        ]
```

**Why the bug occurs:**
* The check `if seg_table_key not in working_input_dict:` assumes the key is only populated once during initial project creation.
* In consecutive runs within the same session, `seg_table_key` already exists in `working_input_dict` with `end: 30.0`.
* Consequently, the `if` check evaluates to `False`, the block is bypassed, and the segment table retains the old span length (`30.0 m`) even though the bridge span has been modified to `32.0 m`.

---

### 5. Proposed Code-Level Fix

In `src/osdagbridge/core/bridge_types/plate_girder/defaults.py` (replace lines 554–559):

```python
    # --- Girder selector key + default segment table: only a .G{n} suffix ---
    for girder_idx in range(1, count + 1):
        working_input_dict[f"{KEY_MP_GD_SELECT_GIRDER}.G{girder_idx}"] = f"G{girder_idx}"
        seg_table_key = f"{KEY_MP_GD_SEGMENT_TABLE}.G{girder_idx}"
        existing_segs = working_input_dict.get(seg_table_key)
        
        # If key is missing or empty, populate with default single segment matching span
        if not existing_segs:
            working_input_dict[seg_table_key] = [
                {"id": f"G{girder_idx}M1", "start": 0.0, "end": span}
            ]
        elif len(existing_segs) == 1 and existing_segs[0].get("id") == f"G{girder_idx}M1":
            # For default single-segment girders, automatically synchronize end with current span
            existing_segs[0]["end"] = span
            working_input_dict[seg_table_key] = existing_segs
```

This fix ensures that whenever the span is changed, single-segment girders are automatically synchronized to the new span length without clobbering multi-segment user splices.
