# GitHub Issue 3: Output Dock DCR Percent Bars Fail to Populate Due to Load Case Name Mismatch

**Repository:** `https://github.com/Nidhikhare12/OsdagBridge.git` (or upstream fork)  
**Issue Title:** `[Bug] Output dock DCR percentage bars fail to populate due to load case naming mismatch ("Envelope" vs "Design Envelope")`  
**Labels:** `bug`, `ui`, `output-dock`, `DCR`  
**Severity:** Medium  
**Live Upstream Issue URL:** [Issue #277](https://github.com/Nidhikhare12/OsdagBridge/issues/277)  
**Status:** **CONFIRMED BUG**

---

### Description
Following a completed design execution, the percentage bars in the Output Dock (representing Strength Limit State Flexure, Shear, Interaction, LTB, Longitudinal Shear, Fatigue, Stress Limitation, and Deflection) remain completely blank (0% / empty). 

This occurs because `output_dock.py` requests results for `"Envelope"` by default, whereas `plategirderbridge.py` registers the aggregated design envelope under the name `"Design Envelope"`. When `"Envelope"` is passed, `backend.get_dcr_for_selection("All", "Envelope")` finds no matching load case and returns an empty dictionary `{}`.

### Steps to Reproduce
1. Execute any valid plate girder design in the desktop GUI.
2. Observe the Output Dock under the **Superstructure -> Girder Design** section.
3. The percent bars for flexure, shear, LTB, etc., remain at 0% or unpopulated.
4. Manually change the load case dropdown in the Output Dock to another load case, then change it to `"Design Envelope"`: the percentage bars suddenly appear with valid calculated values.

### Root Cause Analysis
1. In `src/osdagbridge/desktop/ui/docks/output_dock.py`:
```python
# Line 886:
girder_name  = member_combo.currentText() if member_combo else "All"
load_case    = lc_combo.currentText()     if lc_combo     else "Envelope"  # <-- Default is "Envelope"
dcr_values = self.backend.get_dcr_for_selection(girder_name, load_case)
```
2. In `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py`:
```python
# Lines 3793-3794:
if load_case == "Design Envelope":
    return design_envelope_engine(girder_names, per_girder)

# Lines 3820-3823:
g_data = per_girder.get(g_name, {})
per_lc = g_data.get("per_lc", {})
lc_demand = per_lc.get(load_case)
if not lc_demand:
    continue  # "Envelope" is not in per_lc (only specific cases like BASIC_1, etc.) -> returns None -> {}
```

Because `load_case == "Envelope"` is neither `"Design Envelope"` nor an individual load case in `per_lc`, the method falls through and returns `None` (resulting in `{}`).

### Proposed Fix
In `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py` (Line 3793), accept both `"Design Envelope"` and `"Envelope"` as aliases:

```python
if load_case in ("Design Envelope", "Envelope"):
    return design_envelope_engine(girder_names, per_girder)
```

Additionally, in `src/osdagbridge/desktop/ui/docks/output_dock.py` (Line 886), default to `"Design Envelope"`:
```python
load_case = lc_combo.currentText() if lc_combo else "Design Envelope"
```
