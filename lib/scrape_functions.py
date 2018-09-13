import re
import json
import requests
import random

from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path

def main():
    fn_names = get_fn_filenames()
    fn_urls = ['https://www.stata.com/help.cgi?' + x for x in fn_names]

    i = 0
    all_fns = []
    for fn_url in fn_urls:
        i += 1
        sleep(random.uniform(1, 4))
        print(i, ' ', fn_url)
        res = scrape_fn_page(fn_url)
        if res is not None:
            all_fns.extend(res)

    with open('functions.json', 'w') as f:
        json.dump(all_fns, f, indent=4)


def get_fn_filenames(basepath='/home/kyle/local/stata/ado/base'):
    """Get function filenames without suffix

    Args:
        basepath: Ado basepath, currently ~/local/stata/ado/base
    """
    basepath = Path(basepath)
    f_basepath = basepath / 'f'
    files = [x for x in f_basepath.iterdir()]
    files = [x for x in files if x.name.startswith('f_')]

    names = sorted([x.name for x in files])
    names = [re.sub(r'\.(i|st)hlp$', '', x) for x in names]
    names = sorted(list(set(names)))
    return names


def scrape_fn_page(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    ps = soup.find_all('p')
    ps = ps[3:]
    ps = ps[:-1]

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
    ps = soup.find_all('p')
    fn_signature = ps[0].text.strip().split('\n')[0]
    fn_name = re.search(r'^(\w+)\(', fn_signature).group(1)
    html = ''.join([str(x) for x in ps])
    return {fn_name: html}


if __name__ == '__main__':
    main()
