# OpenSYE

## What is it ?

This program generates Operating-System level exercises.

Created for the 2020 confined edition of the 'Nuit de l'Info',
and more specifically for the UEVE IT dept task.
Authors : L. Becquey & S. Besse.
Distributed under CC 4.0 Licence BY-SA.

## Dependencies

Run this tool on any system (Linux, Mac OS, Windows) that has this prerequisities installed:
- Python3.8+
- A LaTeX distribution installed (typically, texlive-core + texlive-science + texlive-latexextra) with the latexmk executable in path.

## How to use

```
./generator.py --title "My first SYE exam" -l [FR|EN] [ --l33t ]
```

Usage:  ./generator.py [ --year <yourYear> --title <SheetTitle> -l EN --l33t ]

-h, --help              Displays this help message
-l, --lang [FR, EN]     Changes the exercice's output language.
--l33t                  Translates the exercices to l33t-5p34k, to facilitate
                         understanding with the students. Using the option
                         several times increases the l33t level.
--title <arg>           Title of the exam sheet.
--year <arg>            Predicts the TD exercices that will be published
                         in scholar year <arg/arg+1>
                         
## Known issues

By nature, the randomness of the generation may result in a very long question and therefore unfeasible or disappearing outside the sheet. 
Such overfull bad boxes are not great, you may just re-run the tool to yield a new topic.
