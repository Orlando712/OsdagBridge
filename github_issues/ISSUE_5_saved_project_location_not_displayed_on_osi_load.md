# Issue 5: Saved project location is not displayed after loading an .osi file

**Status:** Confirmed / Reproducible (GUI & File Reload Verification)  
**Severity:** Medium (Data Persistence & UI State Inconsistency)  
**Component:** `osdagbridge.desktop.ui.docks.input_dock.InputDock.populate_from_dict`  
**Git Commit SHA:** `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`  
**Git Branch:** `dev`  
**Test Case File:** `test_cases/location-reload-test.osi`  
**Live Upstream Issue URL:** [Issue #278](https://github.com/Nidhikhare12/OsdagBridge/issues/278)  
**Location Tested:** Bapatla, Andhra Pradesh (in demo screencast and saved `location-reload-test.osi`; baseline used Kakinada; both reproduce identical UI desynchronization)  
**Screencast Video:** [https://youtu.be/HB8rdGHgBVs](https://youtu.be/HB8rdGHgBVs) (Timestamp ~3:00-3:38)

---

### Description
When a user sets a project location (e.g., Kakinada, Andhra Pradesh) via the "Select Location" dialog and saves the project inputs to an `.osi` file, the location data is serialized completely into the file under the `project.location` key.

However, when this saved `.osi` file is subsequently loaded via **Load Design Inputs**, the application fails to restore the location display in the UI. While the "Select Location" button is displayed normally, the informational label and pin icon directly below the button (which previously displayed `Kakinada, Andhra Pradesh`) remain hidden and blank. This gives the user the false impression that the project location was lost during file saving or loading.

---

### Environment
- **Operating System:** macOS (Apple Silicon, macOS 15.x / Darwin 24.x)
- **Environment:** Conda (`osdagbridge-env`), Python 3.12
- **Framework:** PySide6 (Qt for Python)
- **Repository:** `https://github.com/Orlando712/OsdagBridge.git`

---

### Steps to Reproduce
1. Launch OsdagBridge desktop application:
   ```bash
   python -m osdagbridge.desktop.main
   ```
2. In the **Input Dock**, under the **Project Location** section, click the **Select Location** button.
3. In the `ProjectLocationDialog`:
   - Keep the method as **Location Name**.
   - Select State: **Andhra Pradesh**.
   - Select District: **Kakinada**.
   - Click **OK / Save**.
4. **Observe Before-Save UI:** Directly beneath the "Select Location" button, an info row appears showing the location pin icon and text:
   `Kakinada, Andhra Pradesh`.
5. Click **Save Inputs (.osi)** and save the file (e.g. `location-reload-test.osi`).
6. Reset or restart the application session (or unlock inputs).
7. Click **Load Design Inputs** and open `location-reload-test.osi`.
8. **Observe After-Reload UI:** The span (30 m) and carriageway width (15 m) restore properly, and the button displays "Select Location" as normal. However, look below the button: **the label `Kakinada, Andhra Pradesh` has disappeared completely**.

---

### Expected Behavior
After successfully loading a valid `.osi` file containing `project.location` data:
- The sub-row widget `project.location_info_row` should be set to visible (`show_display = True`).
- The sub-label `project.location_info_label` should display the saved location string (e.g., `Kakinada, Andhra Pradesh`).

---

### Actual Behavior
- The `project.location_info_row` remains hidden (`setVisible(False)`).
- The `project.location_info_label` remains empty (`""`).
- Only the static "Select Location" button is visible.
- The UI gives no visual feedback that a project location is loaded.

---

### Evidence: App-Saved File Verification
Inspection of the app-saved test case [test_cases/location-reload-test.osi](file:///Users/chaitra/OsdagBridge/test_cases/location-reload-test.osi#L1035-L1049) confirms that `project.location` is indeed written to disk during `saveOSI_inputs()`:

```yaml
project.location:
  data:
    district: Kakinada
    state: Andhra Pradesh
  display_text: Kakinada, Andhra Pradesh
  method: location_name
  show_display: true
  weather_data:
    latitude: 16.9891
    longitude: 82.2475
    max_temp: 47.2
    min_temp: 12
    wind_speed: 50
    z_value: 0.16
    zone: III
```

---

### Root Cause Analysis
In `src/osdagbridge/desktop/ui/docks/input_dock.py`, the `populate_from_dict(self, data: dict)` method loads saved dictionary values into UI widgets:

```python
for widget in self.input_widget.findChildren(QWidget):
    key = widget.objectName()
    if not key or key not in data:
        continue
    value = data[key]
    if value is None:
        continue
    text = str(value)
    if isinstance(widget, QLineEdit):
        widget.blockSignals(True)
        widget.setText(text)
        widget.blockSignals(False)
    elif isinstance(widget, QComboBox):
        if widget.findText(text) < 0:
            widget.addItem(text)
        self._set_combo_silently(widget, text)
```

1. The widget whose `objectName` is `"project.location"` is a `QPushButton` created in `_make_button_row()`. `populate_from_dict()` only handles `QLineEdit` and `QComboBox`, so `QPushButton` is skipped.
2. The display text is rendered inside a separate `QLabel` (`objectName="project.location_info_label"`) wrapped in an `info_row` (`objectName="project.location_info_row"`). Neither of these widget names exists as a top-level key in `data` (where the key is `"project.location"`).
3. As a result, `populate_from_dict()` contains no code to extract `data.get("project.location")` and refresh the text or visibility of `project.location_info_label` and `project.location_info_row`.

---

### Proposed Code-Level Fix
In `src/osdagbridge/desktop/ui/docks/input_dock.py`, inside `populate_from_dict(self, data: dict)`, add explicit logic to refresh the location info label and visibility from the loaded dictionary:

```python
# Restore Project Location display label and visibility from loaded data
loc = data.get(KEY_PROJECT_LOCATION)
info_lbl = self._w(f"{KEY_PROJECT_LOCATION}_info_label")
info_row = self._w(f"{KEY_PROJECT_LOCATION}_info_row")
if isinstance(loc, dict):
    display_text = loc.get("display_text", "")
    show_display = loc.get("show_display", bool(display_text))
    if info_lbl:
        info_lbl.setText(display_text or "Location not selected")
    if info_row:
        info_row.setVisible(show_display)
else:
    if info_lbl:
        info_lbl.setText("")
    if info_row:
        info_row.setVisible(False)
```

*(Note: Dialog prefill and backend solver behaviors remain decoupled from this UI label fix.)*
