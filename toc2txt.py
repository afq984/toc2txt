# example
# \contentsline {chapter}{\numberline {1}Introduction}{1}{chapter.1}%


import argparse
import re
try:
    from wcwidth import wcswidth
except ImportError:
    import traceback
    traceback.print_exc()
    print('Failed importing wcwidth. Using len() instead.')
    wcswidth = len


CONTENTSLINE = r'\contentsline '


def parseline(line: str):
    result = []
    left = 0
    level = 0
    for match in re.finditer('[{}]', line):
        if match.group(0) == '{':
            if level == 0:
                left = match.span()[1]
            level += 1
        else:
            level -= 1
            if level == 0:
                right = match.span()[0]
                result.append(line[left:right])
    return result


def numandtitle(title):
    if '{' in title:
        l, _, r = title.partition('}')
        return l.partition('{')[-1], r
    return '', title


def toc2txt(file, filename):
    entries = []
    numw = 0
    titlepagew = 0
    for lineno, line in enumerate(file, 1):
        def err(msg):
            print(f'{filename}:{lineno}: {msg}')
        line = line.strip()
        if not line.startswith(CONTENTSLINE) or not line.endswith('%'):
            continue
        if r'\{' in line or r'\}' in line:
            err(r'cannot handle \{ or \}')
            continue
        line = line[len(CONTENTSLINE):-1]
        _, title, page, *_ = parseline(line)
        num, title = numandtitle(title)
        entries.append((num, title, page))
        numw = max(numw, wcswidth(num) + bool(num) * 2)
        titlepagew = max(titlepagew, wcswidth(title) + wcswidth(page) + 3)
    for num, title, page in entries:
        print('{}{}{}{}{}'.format(
            num, ' ' * (numw - wcswidth(num)),
            title, '.' * (titlepagew - wcswidth(title) - wcswidth(page)), page
        ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('toc')
    args = parser.parse_args()
    with open(args.toc) as file:
        toc2txt(file, args.toc)


if __name__ == '__main__':
    main()
