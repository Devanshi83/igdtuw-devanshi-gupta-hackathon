"""Export the editable seven-slide PowerPoint to PDF using LibreOffice.

Install LibreOffice separately, then: python scripts/build_presentation.py
The checked-in PDF needs no extra software to view. Edit presentation.pptx first.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_pdf():
    executable = shutil.which('soffice')
    if not executable:
        raise SystemExit('Install LibreOffice and add soffice to PATH, or export presentation.pptx to PDF from PowerPoint.')
    with tempfile.TemporaryDirectory(prefix='signal-shock-slides-') as folder:
        temp = Path(folder)
        profile = (temp / 'profile').as_uri()
        subprocess.run([executable, f'-env:UserInstallation={profile}', '--headless',
                        '--convert-to', 'pdf', '--outdir', str(temp),
                        str(ROOT / 'docs/presentation.pptx')], check=True)
        output = temp / 'presentation.pdf'
        if not output.is_file():
            raise SystemExit('LibreOffice did not produce the PDF')
        shutil.copyfile(output, ROOT / 'docs/presentation.pdf')
    print('Exported docs/presentation.pdf. Visually review all seven pages before submission.')

if __name__ == '__main__':
    build_pdf()
