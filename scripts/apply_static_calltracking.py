"""Keep the calltracking component in sync on every published page."""

import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
START = '<!-- static-calltracking:start -->'
END = '<!-- static-calltracking:end -->'
BLOCK = re.compile(re.escape(START) + '.*?' + re.escape(END) + '\n?', re.S)
COMPONENT = (ROOT / 'components/static-calltracking.html').read_text().strip()


def insert_calltracking(html):
    html = BLOCK.sub('', html)
    end = html.index('</head>')
    return html[:end] + f'{START}\n{COMPONENT}\n{END}\n' + html[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    urls = ElementTree.parse(ROOT / 'sitemap.xml').findall('.//{*}loc')
    changed = []
    for url in urls:
        page = ROOT / urlsplit(url.text).path.strip('/') / 'index.html'
        original = page.read_text()
        updated = insert_calltracking(original)
        if updated != original:
            changed.append(str(page.relative_to(ROOT)))
            if not args.check:
                page.write_text(updated)
    if args.check and changed:
        raise SystemExit('Out of date: ' + ', '.join(changed))
    print(f'{len(urls)} pages, {len(changed)} updated')


if __name__ == '__main__':
    main()
