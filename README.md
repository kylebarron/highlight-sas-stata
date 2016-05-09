Highlight SAS and Stata
=======================

SAS and Stata, while relatively simple to highlight, are not popular enough to be part of most highlighting packages. I use them quite extensively, however, and recently my RA work has required me to document work that uses SAS and Stata. Since I like pretty documentation, I have had to implement SAS and Stata highlghting in a variety of places.

Implementations
---------------

This repo contains SAS and Stata highlighting implementations for
- [Minted](https://github.com/gpoore/minted), a LaTeX code highlighter that uses [Pygments](https://bitbucket.org/birkenfeld/pygments-main), a syntax highlighter written in python.
- [Listings](http://tug.ctan.org/tex-archive/macros/latex/contrib/listings/), a LaTeX implementation of syntax highlighting.
- [Highlight.js](https://github.com/isagalaev/highlight.js), a syntax highlighter written in JavaScript.

This project started with me using `listings` and `minted` from LaTeX. Since I code in `vim`, I also wrote a short script to highlight code in LaTeX using the appropriate `syntax/<lang>.vim`. In this case, simply `:so lib/tex_fenced.vim` from vim.

### [Minted](https://github.com/gpoore/minted) and [Pygments](https://bitbucket.org/birkenfeld/pygments-main)

[Minted](https://github.com/gpoore/minted) is a LaTeX package that uses [pygments](https://bitbucket.org/birkenfeld/pygments-main) to highlight code. Pygments is quite complex and has a lot of options, but this means highlighting here should be free of any issues. I added sas.py and stata.py styles to match the SAS and Stata editors (styles are just a list of types and colors, so defining them is quite easy).

To install, from a bash prompt
```bash
pyg=/path/to/pygments
# pyg=/usr/lib/python3.5/site-packages/pygments
# pyg=/usr/lib/python2.7/site-packages/pygments
cp -s $PWD/pygments/pygments/lexers/sas.py   $pyg/pygments/lexers/sas.py
cp -s $PWD/pygments/pygments/lexers/stata.py $pyg/pygments/lexers/stata.py
cp -s $PWD/pygments/pygments/styles/sas.py   $pyg/pygments/styles/sas.py
cp -s $PWD/pygments/pygments/styles/stata.py $pyg/pygments/styles/stata.py
```

You must add to `$pyg/pygments/lexers/_mappings.py` the following to the LEXERS dict (add them anywhere between `LEXERS = {` and `}`)
```python
'SASLexer': ('pygments.lexers.sas', 'SAS', ('sas', 'SAS'), ('*.sas', '*.SAS'), ('text/x-sas', 'text/sas', 'application/x-sas')),
'StataLexer': ('pygments.lexers.stata', 'Stata', ('stata', 'do', 'Stata'), ('*.do', '*.ado'), ('text/x-stata', 'text/stata', 'application/x-stata')),
```

### [Listings](http://tug.ctan.org/tex-archive/macros/latex/contrib/listings/)

I used to use this before I discovered minted and pygments. Defining a package is extremely hard because the implementation is in TeX and it has all those limitations. I include it here because not everyone can or wants to go through installing pygments, but the drawback is that there will be highlighting quirks and errors I am unsure how to deal with.

To install, from a bash prompt
```bash
localtexmf=`kpsewhich -var-value=TEXMFHOME`/tex/latex/local
mkdir -p $localtexmf
cp -s $PWD/listings/lstsas.tex   $localtexmf/lstsas.tex
cp -s $PWD/listings/lststata.tex $localtexmf/lststata.tex
```

Now add this to your preamble
```tex
\input{lstsas}
\input{lststata}
```

### [Highlight.js](https://github.com/isagalaev/highlight.js)

This already had Stata support. I added SAS support only. I mainly use this in Redmine. Defining the languages was pretty simple, and it should be mostly fine, but I don't think I have as fine-grained control as with Pygments. I did add sas.css and stata.css styles to match the SAS and Stata editors (styles are pretty straightforward CSS files).

To install, from a bash prompt
```bash
hljs=/path/to/highlight.js
cp -s $PWD/highlight.js/test/detect/sas/default.txt $hljs/test/detect/sas/default.txt
cp -s $PWD/highlight.js/src/languages/sas.js $hljs/src/languages/sas.js
cp -s $PWD/highlight.js/src/styles/sas.css   $hljs/src/styles/sas.css
cp -s $PWD/highlight.js/src/styles/stata.css $hljs/src/styles/stata.css
cd $hljs
node tools/build.js -n <list-of-languages>
```
