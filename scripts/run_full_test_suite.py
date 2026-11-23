import sys
import os
import json
import copy
import traceback
import pprint

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.bridge_types.plate_girder.defaults import BASIC_INPUT_DICT, solve_extend_basic_input_dict
from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog
from osdagbridge.core.bridge_types.plate_girder.plot_generator import (
    build_figure_sfd, build_figure_bmd, build_figure_deflection, build_figure_grillage
)
from osdagbridge.core.bridge_types.plate_girder.cad_generator import PlateGirderCADGenerator
from osdagbridge.core.reports.report_generator import ReportRequest, generate_report
from osdagbridge.core.utils.common import *

OUTPUT_DIR = "/Users/chaitra/.gemini/antigravity/brain/2492061f-1c2d-43ea-ab1a-ad5cde51db81/scratch/results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def prime_material(input_dict, key, selected, custom_fields=None):
    dlg = MaterialPropertiesDialog(read_only=(custom_fields is None), selected_material=selected, member=key, custom_fields=custom_fields)
    fields = dlg.get_export_fields() or {}
    for fld_key, fld_val in fields.items():
        input_dict[fld_key] = fld_val
    input_dict[key] = selected

def get_kakinada_location():
    return {
        'method': 'location_name',
        'data': {'state': 'Andhra Pradesh', 'district': 'Kakinada'},
        'weather_data': {
            'wind_speed': 50,
            'zone': 'III',
            'z_value': 0.16,
            'max_temp': 47.2,
            'min_temp': 12.0,
            'latitude': 16.9891,
            'longitude': 82.2475
        },
        'display_text': 'Kakinada, Andhra Pradesh',
        'show_display': True
    }

def serialize_dict(d):
    clean = {}
    for k, v in d.items():
        try:
            json.dumps({k: v})
            clean[k] = v
        except Exception:
            clean[k] = str(v)
    return clean

def test_cad(backend, run_id):
    try:
        cad_params = backend.get_3d_cad_parameters()
        gen = PlateGirderCADGenerator()
        model_data = gen.generate(cad_params)
        shapes_count = len(model_data) if isinstance(model_data, dict) else 0
        return {"status": "SUCCESS", "shapes_count": shapes_count, "span_mm": cad_params.span_length_L}
    except Exception as e:
        return {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}

def test_plots(backend, run_id):
    try:
        ds = backend.get_results_dataset()
        loadcases = backend.get_available_loadcases()
        fig_g = build_figure_grillage(backend.grillage_model)
        fig_bmd = build_figure_bmd(backend, ds, "Envelope")
        fig_sfd = build_figure_sfd(backend, ds, "Envelope")
        fig_defl = build_figure_deflection(backend, ds, "Envelope")
        return {
            "status": "SUCCESS",
            "loadcases_count": len(loadcases) if loadcases else 0,
            "has_grillage_fig": fig_g is not None,
            "has_bmd_fig": fig_bmd is not None,
            "has_sfd_fig": fig_sfd is not None,
            "has_defl_fig": fig_defl is not None,
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}

def test_report(backend, run_id):
    try:
        req = ReportRequest(
            output_dir=os.path.join(OUTPUT_DIR, f"report_{run_id}"),
            file_stem=f"report_{run_id}",
            project_name=f"OsdagBridge_Run_{run_id}",
            engineer_name="QA Engineer"
        )
        res = backend.generate_design_report(req, None, is_preview=False)
        return {
            "status": "SUCCESS" if res and getattr(res, 'pdf_path', None) else "PARTIAL_OR_FAILED",
            "pdf_path": getattr(res, 'pdf_path', None),
            "tex_path": getattr(res, 'tex_path', None)
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}

session_log = []

# =========================================================================
# RUN 1: Baseline (30m, Kakinada, E 350A, M40)
# =========================================================================
print("\n" + "="*70)
print("STARTING RUN 1: Baseline (30m, Kakinada, E 350A, M40)")
print("="*70)

backend = PlateGirderBridge()
input_dict = dict(BASIC_INPUT_DICT)

input_dict[KEY_PROJECT_LOCATION] = get_kakinada_location()
input_dict[KEY_SPAN] = 30.0
input_dict[KEY_CARRIAGEWAY_WIDTH] = 15.0
input_dict[KEY_INCLUDE_MEDIAN] = 'Yes'
input_dict[KEY_FOOTPATH] = 'Both Sides'
input_dict[KEY_SKEW_ANGLE] = 10.0
input_dict[KEY_GIRDER] = 'E 350A'
input_dict[KEY_CROSS_BRACING] = 'E 350A'
input_dict[KEY_END_DIAPHRAGM] = 'E 350A'
input_dict[KEY_DECK_CONCRETE_GRADE_BASIC] = 'M40'

prime_material(input_dict, KEY_GIRDER, 'E 350A')
prime_material(input_dict, KEY_CROSS_BRACING, 'E 350A')
prime_material(input_dict, KEY_END_DIAPHRAGM, 'E 350A')
prime_material(input_dict, KEY_DECK_CONCRETE_GRADE_BASIC, 'M40')

solve_extend_basic_input_dict(input_dict)

with open(os.path.join(OUTPUT_DIR, "run1_input_before_design.json"), "w") as f:
    json.dump(serialize_dict(input_dict), f, indent=2)

backend.set_input(input_dict)
backend.design()

out1 = backend.output_dict
with open(os.path.join(OUTPUT_DIR, "run1_output_dict.json"), "w") as f:
    json.dump(serialize_dict(out1), f, indent=2)

dcr1 = backend.get_dcr_for_selection("All", "Envelope")
with open(os.path.join(OUTPUT_DIR, "run1_dcr.json"), "w") as f:
    json.dump(dcr1, f, indent=2)

cad1 = test_cad(backend, "run1")
plots1 = test_plots(backend, "run1")
rep1 = test_report(backend, "run1")

session_log.append({
    "run": 1,
    "title": "Baseline (30m, Kakinada, E 350A, M40)",
    "span": 30.0,
    "girders": input_dict.get(KEY_TS_NO_OF_GIRDERS),
    "spacing": input_dict.get(KEY_TS_GIRDER_SPACING),
    "overall_width": input_dict.get(KEY_TS_OVERALL_WIDTH),
    "dcr": dcr1,
    "cad": cad1,
    "plots": plots1,
    "report": rep1
})
print("Run 1 Completed! DCR:", dcr1)

# =========================================================================
# RUN 2: Consecutive Run in Same Session (Span 30m -> 32m)
# =========================================================================
print("\n" + "="*70)
print("STARTING RUN 2: Consecutive Run with Span Change (30m -> 32m)")
print("="*70)

# Simulate GUI Unlock:
backend.reset()

# Check what happened to input_dict after Run 1:
print("Inspecting state of input_dict after Run 1 and reset:")
print("  Span in input_dict before update:", input_dict.get(KEY_SPAN))
print("  Segment table G1 before update:", input_dict.get(f'{KEY_MP_GD_SEGMENT_TABLE}.G1'))
print("  Girder depth G1.M1 before update:", input_dict.get(f'{KEY_MP_GIRDER_DEPTH}.G1.M1'))

# User updates Span in GUI from 30.0 to 32.0:
input_dict[KEY_SPAN] = 32.0

# When user changes span, solve_extend_basic_input_dict is triggered:
solve_extend_basic_input_dict(input_dict)

print("Inspecting state after span changed to 32.0 and solve_extend_basic_input_dict:")
print("  Span in input_dict:", input_dict.get(KEY_SPAN))
print("  Segment table G1:", input_dict.get(f'{KEY_MP_GD_SEGMENT_TABLE}.G1'))
print("  Girder depth G1.M1:", input_dict.get(f'{KEY_MP_GIRDER_DEPTH}.G1.M1'))
print("  No of Girders:", input_dict.get(KEY_TS_NO_OF_GIRDERS))

with open(os.path.join(OUTPUT_DIR, "run2_input_before_design.json"), "w") as f:
    json.dump(serialize_dict(input_dict), f, indent=2)

backend.set_input(input_dict)
backend.design()

out2 = backend.output_dict
with open(os.path.join(OUTPUT_DIR, "run2_output_dict.json"), "w") as f:
    json.dump(serialize_dict(out2), f, indent=2)

dcr2 = backend.get_dcr_for_selection("All", "Envelope")
with open(os.path.join(OUTPUT_DIR, "run2_dcr.json"), "w") as f:
    json.dump(dcr2, f, indent=2)

cad2 = test_cad(backend, "run2")
plots2 = test_plots(backend, "run2")
rep2 = test_report(backend, "run2")

session_log.append({
    "run": 2,
    "title": "Span Change (30m -> 32m)",
    "span": 32.0,
    "girders": input_dict.get(KEY_TS_NO_OF_GIRDERS),
    "spacing": input_dict.get(KEY_TS_GIRDER_SPACING),
    "overall_width": input_dict.get(KEY_TS_OVERALL_WIDTH),
    "dcr": dcr2,
    "cad": cad2,
    "plots": plots2,
    "report": rep2
})
print("Run 2 Completed! DCR:", dcr2)

# =========================================================================
# RUN 3: Consecutive Run with Custom Materials (Custom Steel + Custom Concrete)
# =========================================================================
print("\n" + "="*70)
print("STARTING RUN 3: Consecutive Run with Custom Steel & Custom Deck Concrete")
print("="*70)

backend.reset()

# User sets custom steel properties:
custom_steel_fields = {
    'material.girder.density': '78.5',
    'material.girder.fy': '450.0',
    'material.girder.fu': '570.0',
    'material.girder.e': '210.0',
    'material.girder.g': '80.77',
    'material.girder.poisson': '0.30',
    'material.girder.thermal': '12.0'
}
prime_material(input_dict, KEY_GIRDER, 'Custom_Steel_E450', custom_fields=custom_steel_fields)
prime_material(input_dict, KEY_CROSS_BRACING, 'Custom_Steel_E450', custom_fields=custom_steel_fields)
prime_material(input_dict, KEY_END_DIAPHRAGM, 'Custom_Steel_E450', custom_fields=custom_steel_fields)

# User sets custom deck concrete:
custom_concrete_fields = {
    'material.deck.density': '25.0',
    'material.deck.fck': '50.0',
    'material.deck.fctm': '3.5',
    'material.deck.ecm': '35.0',
    'material.deck.thermal': '10.0'
}
prime_material(input_dict, KEY_DECK_CONCRETE_GRADE_BASIC, 'Custom_Deck_M50', custom_fields=custom_concrete_fields)

solve_extend_basic_input_dict(input_dict)

with open(os.path.join(OUTPUT_DIR, "run3_input_before_design.json"), "w") as f:
    json.dump(serialize_dict(input_dict), f, indent=2)

backend.set_input(input_dict)
backend.design()

out3 = backend.output_dict
with open(os.path.join(OUTPUT_DIR, "run3_output_dict.json"), "w") as f:
    json.dump(serialize_dict(out3), f, indent=2)

dcr3 = backend.get_dcr_for_selection("All", "Envelope")
with open(os.path.join(OUTPUT_DIR, "run3_dcr.json"), "w") as f:
    json.dump(dcr3, f, indent=2)

cad3 = test_cad(backend, "run3")
plots3 = test_plots(backend, "run3")
rep3 = test_report(backend, "run3")

session_log.append({
    "run": 3,
    "title": "Custom Steel (450 MPa) & Custom Deck Concrete (M50)",
    "span": 32.0,
    "girders": input_dict.get(KEY_TS_NO_OF_GIRDERS),
    "spacing": input_dict.get(KEY_TS_GIRDER_SPACING),
    "overall_width": input_dict.get(KEY_TS_OVERALL_WIDTH),
    "dcr": dcr3,
    "cad": cad3,
    "plots": plots3,
    "report": rep3
})
print("Run 3 Completed! DCR:", dcr3)

# Save overall session summary:
with open(os.path.join(OUTPUT_DIR, "session_summary.json"), "w") as f:
    json.dump(session_log, f, indent=2)

print("\nAll 3 consecutive runs completed successfully! Results written to:", OUTPUT_DIR)
