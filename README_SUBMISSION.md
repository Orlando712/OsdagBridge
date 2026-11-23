# FOSSEE OsdagBridge Software Testing & Issue Reporting — Screening Submission

**Candidate:** Charitha Tubati ([@Orlando712](https://github.com/Orlando712))  
**Repository Fork:** [Orlando712/OsdagBridge](https://github.com/Orlando712/OsdagBridge)  
**Submission Branch:** `screening-submission`  
**Upstream Repository:** [Nidhikhare12/OsdagBridge](https://github.com/Nidhikhare12/OsdagBridge)  
**Evaluator Invited:** `Nidhikhare12` (Collaborator invitation sent)  
**Target Commit SHA:** `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (`dev` branch)  
**Environment:** macOS 15 (Apple Silicon / Darwin arm64), Conda (`osdagbridge-env`, Python 3.12.16, PySide6)  

---

## 📹 Screencast Demo Video

**Full Screening Screencast:** **[https://youtu.be/HB8rdGHgBVs](https://youtu.be/HB8rdGHgBVs)**  
*(Duration: 3 minutes 38 seconds &bull; 1080p / 60fps)*

### Video Timeline & Verification Milestones:
- **0:00 – 1:15 &bull; Run 1 (30 m Baseline):** 30 m span, 15 m carriageway per direction, Kakinada AP, 10° skew, E 350A steel, M40 concrete. Generation of interactive 3D CAD model with 7 plate girders (34.45 m overall deck width, 5.12 m spacing), OpenSeesPy grillage FEA, and structural design execution.
- **1:15 – 2:10 &bull; Run 2 (32 m Consecutive Rerun):** In-session unlock and state reset, span modified from 30.0 m to 32.0 m, re-execution of Design. Verifies dynamic sizing refresh, OpenSeesPy grillage update, and 3D CAD model expansion to 32.0 m.
- **2:10 – 3:00 &bull; Run 3 (Custom Materials Run):** In-session unlock, custom structural steel ($f_y = 450\text{ MPa}$, $f_u = 590\text{ MPa}$) and custom deck concrete ($f_{ck} = 50\text{ MPa}$, $E_{cm} = 35.0\text{ GPa}$) configured and saved via Material Dialog. Design re-executed; custom properties verified in analysis plots and 3D model.
- **3:00 – 3:38 &bull; Location Reload Defect (Issue 5):** Setting project location to **Bapatla, Andhra Pradesh**, saving to `location-reload-test.osi`, and reopening the file via *Load Design Inputs*. Demonstrates that while span (30 m) and carriageway (15 m) restore cleanly, the location label below the "Select Location" button disappears completely from the UI.

---

## 🐛 Upstream Issue Tracker Contributions

| Issue | Title & Module | Upstream Status & Live Reference |
| :--- | :--- | :--- |
| **Issue 1** | Girder segment table retains stale span length in consecutive runs after span change | **CONFIRMED BUG** &bull; Matches upstream [#168](https://github.com/Nidhikhare12/OsdagBridge/issues/168). Independent macOS Apple Silicon confirmation (30m &rarr; 32m) posted in **[Issue #168 Comment #7101687339](https://github.com/Nidhikhare12/OsdagBridge/issues/168#issuecomment-7101687339)**. |
| **Issue 2** | Reopening saved custom material in edit dialog resets fields to defaults | **PENDING GUI VERIFICATION** &bull; Kept local; related to upstream [#266](https://github.com/Nidhikhare12/OsdagBridge/issues/266). |
| **Issue 3** | Output Dock DCR percentage bars fail to populate due to load case naming mismatch (`Envelope` vs `Design Envelope`) | **CONFIRMED BUG** &bull; Distinct defect logged upstream as **[Issue #277](https://github.com/Nidhikhare12/OsdagBridge/issues/277)**. |
| **Issue 4** | Calculation report PDF fails with `FileNotFoundError` when `pdflatex` is missing | **HOST ENVIRONMENT LIMITATION** &bull; macOS Conda environment lacks bundled MacTeX; documented with graceful handling recommendation. |
| **Issue 5** | Saved project location label is not restored after loading an `.osi` file | **CONFIRMED BUG** &bull; Distinct UI desynchronization defect logged upstream as **[Issue #278](https://github.com/Nidhikhare12/OsdagBridge/issues/278)**. |

---

## 📂 Repository & Submission Structure

```text
screening-submission/
├── README_SUBMISSION.md                    # This screening submission guide
├── OsdagBridge_Testing_Report.pdf          # Publication-ready testing report PDF (8 pages, PySide6 native)
├── OsdagBridge_Testing_Report.md           # Full markdown testing report
├── OsdagBridge_Testing_Submission.zip      # Complete packaged ZIP archive (26 files, 358 KB)
├── screencast_checklist.md                 # Single-session screencast checklist
│
├── test_cases/                             # Validated .osi YAML project test cases
│   ├── location-reload-test.osi            # App-saved OSI case verifying Issue 5 reload (Bapatla AP)
│   ├── kakinada_config_b_7girders_gui.osi  # Config B: 30m span, 34.45m width, 7 girders @ 5.12m (GUI Baseline)
│   ├── kakinada_config_a_15girders.osi     # Config A: 30m span, 35.85m width, 15 girders @ 2.39m (Scripted)
│   ├── kakinada_run2_span32m.osi           # Run 2: 32m span consecutive run
│   └── kakinada_run3_custom_materials.osi  # Run 3: Custom steel & concrete
│
├── github_issues/                          # Detailed issue documentation with root causes & fixes
│   ├── ISSUE_1_stale_segment_table_on_span_change.md
│   ├── ISSUE_2_custom_material_clobbered_by_prime.md
│   ├── ISSUE_3_output_dock_loadcase_envelope_mismatch.md
│   ├── ISSUE_4_missing_pdflatex_graceful_handling.md
│   └── ISSUE_5_saved_project_location_not_displayed_on_osi_load.md
│
├── scripts/                                # Test execution & PDF generation scripts
│   ├── run_full_test_suite.py              # 3-run automated test suite
│   └── generate_report_pdf.py              # PySide6 QPdfWriter PDF generator
│
└── evidence/                               # Raw JSON input/output dumps & LaTeX source
    ├── session_summary.json                # Execution summary across all 3 runs
    ├── run1_input_before_design.json       # Run 1 raw input dictionary dump
    ├── run1_output_dict.json               # Run 1 raw output dictionary dump
    ├── run1_dcr.json                       # Run 1 DCR ratios dump
    ├── run2_input_before_design.json       # Run 2 raw input dictionary dump
    ├── run2_output_dict.json               # Run 2 raw output dictionary dump
    ├── run2_dcr.json                       # Run 2 DCR ratios dump
    ├── run3_input_before_design.json       # Run 3 raw input dictionary dump
    ├── run3_output_dict.json               # Run 3 raw output dictionary dump
    ├── run3_dcr.json                       # Run 3 DCR ratios dump
    └── kakinada_report.tex                 # 10-chapter generated calculation LaTeX source
```

---

## 🔒 Verification & Compliance
- **Core Source Integrity:** No application source code in `src/` has been altered.
- **Privacy & Security:** Excludes personal files, credentials, and raw recordings.
- **Reproducibility:** Every test case is standalone and reloadable via OsdagBridge GUI or backend API.
