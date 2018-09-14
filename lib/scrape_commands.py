import re
import json
import requests
import random

from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
from html2text import html2text

HELP_WORDS = [r'\[', r'\{',
 'constraints',
 'depvar',
 'exp',
 'extvarlist',
 'filename',
 'if',
 'in',
 'indepvars',
 'macroname',
 'newvar',
 'options',
 'termlist',
 'type',
 'using',
 'varlist',
 'varname',
 'weight']
HELP_WORDS_RE = r' (' + '|'.join(HELP_WORDS) + ')'

def main():
    names = get_filenames('b')
    urls = ['https://www.stata.com/help.cgi?' + x for x in names]

    i = 0
    all_names = []
    all_ps = []
    for url in urls:
        i += 1
        sleep(random.uniform(1, 3))
        print(i, ' ', url)
        res = scrape_page(url)
        if res is not None:
            all_names.extend(res[0])
            all_ps.extend(res[1])

    all_names
    all_ps[3]
    sorted(list(set(all_names)))

    # Combine list of dicts into a single dict
    d = { k: v for d in all_fns for k, v in d.items() }

    # Convert HTML to Markdown
    d = {k: html2text(v) for k, v in d.items()}

    # Undo Stata's line wrapping
    regex = r'(?<!\n)\n(?!\n)'
    d = {k: re.sub(regex, ' ', v) for k, v in d.items()}

    with open('functions.json', 'w') as f:
        json.dump(d, f, indent=4)


def get_filenames(subfolder, basepath='/home/kyle/local/stata/ado/base'):
    """Get function filenames without suffix

    Args:
        subfolder: letter subfolder to get names of
        basepath: Ado basepath, currently ~/local/stata/ado/base
    """
    basepath = Path(basepath) / subfolder
    files = [x for x in basepath.iterdir() if x.name.endswith('.sthlp')]
    names = sorted([x.name[:-6] for x in files])

    if subfolder == 'f':
        names = [x for x in names if not x.startswith('f_')]

    return names


url = 'https://www.stata.com/help.cgi?arch'
url = 'https://www.stata.com/help.cgi?arch_postestimation'
url = 'https://www.stata.com/help.cgi?asmprobit'
url = 'https://www.stata.com/help.cgi?reg'
url = 'https://www.stata.com/help.cgi?ap'
url = 'https://www.stata.com/help.cgi?export_excel'
url = 'https://www.stata.com/help.cgi?axis_title_options'

def scrape_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    ps = soup.find_all('p')
    ps = ps[1:-1]

    page_data = {}

    # Get command title and short description
    try:
        p = ps[0].find('b').text
        match = re.search(r'^\[(\w+)\]\s+([\w\s]+)$', p)
        page_data['docs_book'] = match.group(1)
        page_data['cmd_name'] = match.group(2)
    except AttributeError:
        pass

    page_html = ''.join([str(x) for x in ps])
    # Split </p><p> onto separate lines
    page_html = re.sub(r'^</p><p>$', '</p>\n<p>', page_html, flags=re.MULTILINE)


    # Find indices of top-level sections from text
    i = -1
    section_indices = []
    for p in ps:
        i += 1
        # Is it a secion header?
        contents = p.contents
        try:
            assert contents[0] == '\n'
            assert contents[1].name == 'a'
            assert contents[-2].name == 'b'
            assert contents[-2].find('u')
            assert contents[-1] == '\n'

            section_indices.append(i)
        except (AssertionError, IndexError):
            pass

    sections = {}
    for i in range(len(section_indices)):
        start_ind = section_indices[i]
        try:
            end_ind = section_indices[i + 1]
        except IndexError:
            end_ind = len(ps)

        section_name = ps[start_ind].find('a')['name']
        sections[section_name] = ps[start_ind:end_ind]

    # Parse syntax section
    cmd_names = []
    cmd_ps = []
    if sections.get('syntax'):
        section = sections.get('syntax')
        for s in section:
            # If you've hit the options table, you've gone too far
            try:
                i_text = s.find('i').text
                if 'options' in i_text:
                    break
            except AttributeError:
                pass

            if not s.text.startswith('\n        '):
                continue

            if not s.contents[0] == '\n        ':
                continue

            if not s.contents[1].name == 'b':
                continue

            # Need to use `re.sub` in case cmd spans multiple lines
            cmd_full_text = re.sub(r'\s+', ' ', s.text).strip()
            match = re.search(HELP_WORDS_RE, cmd_full_text)
            if match:
                cmd_name = cmd_full_text[:match.span()[0]]
                cmd_names.append(cmd_name)
                cmd_ps.append(s)
            else:
                print('No syntax name match')
                print('url: ', url)
                print('s: ', s)

    return cmd_names, cmd_ps











    cmd_names
    if ps[0].text.strip() == 'Function':
        ps = ps[1:]
        ps_html = ''.join([str(x) for x in ps])

        return [parse_function_html(ps_html)]

    elif ps[0].text.strip() == 'Functions':
        ps = ps[1:]

        # Combine text, then separate into individual functions, then put back
        # into BeautifulSoup
        html = ''.join([str(x) for x in ps])
        # Split </p><p> onto separate lines
        html = re.sub(r'^</p><p>$', '</p>\n<p>', html, flags=re.MULTILINE)
        html_lines = html.split('\n')

        inds = [ind - 1 for ind, x in enumerate(html_lines) if re.search(r'^    <b>\w+\(', x)]

        all_fn_html = []
        for i in range(len(inds)):
            start_ind = inds[i]
            try:
                end_ind = inds[i + 1]
            except IndexError:
                end_ind = len(html_lines)

            all_fn_html.append('\n'.join(html_lines[start_ind:end_ind]))

        fn_dicts = []
        for fn_html in all_fn_html:
            fn_dicts.append(parse_function_html(fn_html))

        return fn_dicts

    else:
        return None

def parse_function_html(html):
    soup = BeautifulSoup(html, 'lxml')
    for a in soup.find_all('a', href=True):
        a['href'] = 'https://www.stata.com' + a['href']
    ps = soup.find_all('p')
    fn_signature = ps[0].text.strip().split('\n')[0]
    fn_name = re.search(r'^(\w+)\(', fn_signature).group(1)
    html = ''.join([str(x) for x in ps])
    return {fn_name: html}


if __name__ == '__main__':
    main()
