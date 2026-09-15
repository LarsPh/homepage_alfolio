# Public CV

`cv_en.tex` and `cv_ja.tex` are the public CV sources. Build with XeLaTeX and Python packages `pypdf` and `PyYAML`:

```sh
python3 _cv/build.py
```

The script writes `assets/pdf/zhaorong_wang_resume.pdf` (English, then Japanese, two pages each) and `_data/public_cv.yml`, which supplies both website CV pages.

Install Noto Serif CJK JP and Noto Sans CJK JP fonts, or put `NotoSerifCJKjp-Regular.otf` and `NotoSansCJKjp-Bold.otf` in `_cv/fonts/`. English uses Latin Modern Roman.
