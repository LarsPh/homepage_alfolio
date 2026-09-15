"""Build the bilingual PDF and website CV data from the public TeX sources."""
from pathlib import Path
import re
import subprocess
import tempfile
import yaml
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_cv'


def html(text):
    text = re.sub(r'\\(?:href|link)\{([^{}]+)\}\{([^{}]+)\}', r'<a href="\1">\2</a>', text)
    text = re.sub(r'\\(?:textbf|underline)\{([^{}]+)\}', r'\1', text)
    text = text.replace('\\quad', ' ').replace('\\par', '').replace('\\\\', '<br>')
    return text.replace('--', '–').strip()


def website_data(text, lang):
    chunks = re.split(r'\\section\{([^}]+)\}', text)[1:]
    sections = []
    for title, body in zip(chunks[::2], chunks[1::2]):
        body = body.replace('\\newpage', '').replace('\\end{document}', '').strip()
        if '\\begin{tabularx}' in body:
            table = body.split('@{}}', 1)[1].split('\\end{tabularx}')[0]
            rows = []
            for line in table.strip().splitlines():
                left, right = line.split('&', 1)
                rows.append({'date': html(left), 'text': html(right.rstrip().removesuffix('\\\\'))})
            sections.append({'title': title, 'education': rows})
            continue
        # An entry can contain a linked title, so balance braces rather than matching with regex.
        blocks = []
        entry = None
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('\\entry{'):
                values = []
                start = len('\\entry')
                while start < len(line):
                    depth = 0
                    for end in range(start, len(line)):
                        depth += (line[end] == '{') - (line[end] == '}')
                        if depth == 0:
                            values.append(line[start + 1:end])
                            start = end + 1
                            break
                    else:
                        raise ValueError(line)
                entry = {'title': html(values[0]), 'date': html(values[1]), 'paragraphs': []}
                blocks.append(entry)
            else:
                if entry is None:
                    entry = {'paragraphs': []}
                    blocks.append(entry)
                field = re.match(r'\\field\{([^}]+)\}\{(.*)\}$', line)
                entry['paragraphs'].append(('<strong>' + field[1] + '.</strong> ' + html(field[2])) if field and lang == 'en' else (('<strong>' + field[1] + '</strong>　' + html(field[2])) if field else html(line)))
        sections.append({'title': title, 'entries': blocks})
    return sections


def main():
    data = {}
    writer = PdfWriter()
    with tempfile.TemporaryDirectory() as temp:
        for lang in ('en', 'ja'):
            source = SOURCE / f'cv_{lang}.tex'
            data[lang] = website_data(source.read_text(), lang)
            for _ in range(2):
                subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', f'-output-directory={temp}', source.name], cwd=SOURCE, check=True, stdout=subprocess.DEVNULL)
            pdf = PdfReader(Path(temp) / f'cv_{lang}.pdf')
            if len(pdf.pages) != 2:
                raise ValueError(f'{lang}: expected 2 pages, got {len(pdf.pages)}')
            start = len(writer.pages)
            writer.append(pdf, import_outline=False)
            writer.add_outline_item('English' if lang == 'en' else '日本語', start)
        writer.add_metadata({'/Title': 'Wang Zhaorong - CV (English and Japanese)', '/Author': 'Wang Zhaorong'})
        writer.write(ROOT / 'assets/pdf/zhaorong_wang_resume.pdf')
    (ROOT / '_data/public_cv.yml').write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120))
    print('Built 4-page English/Japanese PDF and website CV data.')


if __name__ == '__main__':
    main()
