from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.services.resume_parser import ResumeParser

p = ResumeParser(upload_dir='uploads')
path = Path('uploads') / 'jahnavi_vulava_resume.pdf'
print('Parsing:', path)
try:
    txt = p.parse_file(str(path))
    print('Parsed length:', len(txt))
    print(txt[:1000])
except Exception as e:
    import traceback
    traceback.print_exc()
    print('ERROR:', e)
