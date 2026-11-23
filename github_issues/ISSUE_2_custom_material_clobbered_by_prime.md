# GitHub Issue 2: Custom Material Handling: Script Harness Artifact vs. Reopening Saved Material in Edit Mode

**Repository:** `https://github.com/Nidhikhare12/OsdagBridge.git` (or upstream fork)  
**Issue Title:** `[Investigation / Pending GUI Verification] Custom material lifecycle: scripted test harness artifact vs. reopening saved material in edit mode`  
**Labels:** `investigation`, `ui`, `materials`, `pending-verification`  
**Severity:** Medium (Pending Verification)  
**Status:** **PENDING VERIFICATION IN DESKTOP GUI**

---

### 1. Context & Background
During the initial testing phase of the FOSSEE OsdagBridge screening task, custom steel ($f_y = 450.0\text{ MPa}$, $f_u = 570.0\text{ MPa}$, $E = 210.0\text{ GPa}$) and custom deck concrete ($f_{ck} = 50.0\text{ MPa}$) inputs were tested to verify whether user-defined material properties propagate correctly from the GUI to `input_dict` and into the design check engines.

### 2. Analysis of Initial Scripted Test Artifact
In the initial automated test script (`run_full_test_suite.py`), the test helper instantiated:
```python
MaterialPropertiesDialog(read_only=False, selected_material=selected, member=key, custom_fields=custom_fields)
```
and immediately called:
```python
fields = dlg.get_export_fields() or {}
```
**Key Finding:** The script read the dialog before entering any values into the dialog text fields and without clicking **Save** (`_save_form()`). 
* Because `read_only=False` was passed, `MaterialPropertiesDialog.__init__()` initialized `self.form_data["fields"]` with `_defaults_for_material()`.
* Because no widget interaction occurred and `_save_form()` was not triggered, `dlg.get_export_fields()` naturally exported the unedited default values (250 MPa steel / 40 MPa concrete).
* **Conclusion:** This scripted test result was an artifact of how the dialog was called in the test script, and does **not** demonstrate that clicking Design overwrites custom materials in the application.

### 3. Desktop Application Code Path (One-Way Creation)
Code analysis of the desktop application reveals how custom materials are normally saved during a one-way creation workflow:
1. **User Enters Values:** In `InputDock`, selecting "Custom" opens `MaterialPropertiesDialog(read_only=False)`.
2. **User Clicks Save:** The user enters numbers into the text boxes and clicks **Save**. `_validate_and_save()` calls `_save_form()`, which extracts the text from `self.field_inputs` into `self.form_data["fields"]`.
3. **Storage in InputDock:** `_on_material_changed()` intercepts `QDialog.Accepted`, stores the fields into `self._material_custom_fields[mat]`, and writes the canonical keys to `self.parent.input_dict`.
4. **Pre-Design Priming:** Before design execution, `_prime_material_inputs()` runs:
   ```python
   custom_flds = self._material_custom_fields.get(selected)
   dlg = MaterialPropertiesDialog(read_only=True, selected_material=selected, member=key, custom_fields=custom_flds)
   ```
   Because `read_only=True`, line 286 runs:
   ```python
   if self.custom_fields:
       self.form_data["fields"] = self.custom_fields.copy()
   ```
   This preserves the custom properties and passes them to `PlateGirderBridge`.

### 4. Potential Latent Bug: Reopening Saved Custom Material in Edit Mode
While the one-way creation flow preserves custom fields, a potential defect exists when a user **reopens an already-saved custom material in edit mode** to modify it:
* In `src/osdagbridge/desktop/ui/dialogs/material_properties.py` (`__init__`):
  ```python
  default_prefix = CUSTOM_CONCRETE_PREFIX if self.is_deck_material else CUSTOM_STEEL_PREFIX
  initial_material = self.selected_material.strip() if self.read_only else default_prefix
  self.form_data = {
      "material": initial_material or default_prefix,
      "fields": self._defaults_for_material(initial_material or default_prefix),
  }
  ```
* When reopened in edit mode (`read_only=False`), `self.custom_fields` is not loaded during `__init__`.
* Instead, `self._defaults_for_material()` is loaded, and `_populate_fields()` populates the text fields with standard defaults (e.g., 250 MPa steel) rather than the user's previously saved custom numbers.
* If the user clicks Save without re-typing their custom values, their custom properties would be overwritten with defaults.

### 5. Verification Status
* **Status:** **PENDING VERIFICATION IN DESKTOP APP**
* **Verification Objective for Screencast:** In the live macOS GUI, define and save a custom steel and concrete material, then re-open that saved custom material in edit mode to directly observe whether the dialog displays the previously saved custom values or resets them to defaults.
