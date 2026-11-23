# GitHub Issue 4: PDF Report Generation Fails on macOS Due to Unchecked pdflatex Binary Dependency

**Repository:** `https://github.com/Nidhikhare12/OsdagBridge.git` (or upstream fork)  
**Issue Title:** `[Bug / Robustness] PDF report generation fails with FileNotFoundError when pdflatex is not installed in the host OS`  
**Labels:** `enhancement`, `reports`, `cross-platform`, `macOS`  
**Severity:** Medium  

---

### Description
On systems where a native TeX distribution (such as MacTeX on macOS or TeX Live on Linux) is not installed, clicking **Generate / Preview Design Report** generates the `.tex` LaTeX calculation document but fails to produce the final `.pdf` document, resulting in a critical error dialog.

While the LaTeX source is generated properly (~33.5 KB across 10 chapters), the application relies on invoking `pdflatex` directly via `subprocess.run()`. If `pdflatex` is missing, an unhandled exception or failed process execution occurs without providing the user an option to export the raw `.tex` file or using an open-source Python-native fallback (such as ReportLab or WeasyPrint).

### Steps to Reproduce
1. In a clean conda environment on macOS (where `which pdflatex` returns nothing).
2. Execute a bridge design in OsdagBridge.
3. Click the **Design Report** icon in the toolbar.
4. Select report options and click **Generate**.
5. Observe error:
   ```text
   pdflatex run failed: [Errno 2] No such file or directory: 'pdflatex'
   pdflatex ran but no PDF was produced.
   ```
   A popup appears stating: "Report Generation Failed. Possible causes: pdflatex not installed".

### Root Cause Analysis
In `src/osdagbridge/core/reports/report_generator.py` (`generate_report`):
```python
# Lines 842-855:
compiler = 'pdflatex'
try:
    import importlib
    module = importlib.import_module('osdag_latex_env.__main__')
    latex_env = getattr(module, 'OsdagLatexEnv')()
    if latex_env.pdflatex:
        compiler = str(latex_env.pdflatex)
except Exception as e:
    logger.info("osdag_latex_env not found or failed to load. (%s)", e)

# Lines 969-974:
res = subprocess.run(
    [compiler, '-interaction=nonstopmode', request.file_stem + '.tex'],
    **kwargs
)
```
When `osdag_latex_env` is not bundled and `pdflatex` is not in the system `$PATH`, `shutil.which(compiler)` is `None`. The code still proceeds to `subprocess.run([compiler, ...])`, triggering `FileNotFoundError`.

### Proposed Fix
1. Perform pre-flight verification with `shutil.which(compiler)`.
2. If `compiler` is not found, copy the generated `.tex` file to the destination directory and inform the user that LaTeX source was saved, offering instructions to install MacTeX / TeX Live.
3. Example snippet for `src/osdagbridge/core/reports/report_generator.py`:

```python
import shutil

compiler_path = shutil.which(compiler)
if not compiler_path:
    logger.warning("LaTeX compiler '%s' is not installed or not in PATH.", compiler)
    # Save .tex file to target directory so user does not lose calculations
    if os.path.exists(tmp_tex):
        shutil.copy2(tmp_tex, tex_path)
    return ReportResult(
        pdf_path=None, 
        tex_path=tex_path, 
        error_message=f"'{compiler}' was not found in system PATH. Install TeX Live or MacTeX to compile PDF."
    )
```
