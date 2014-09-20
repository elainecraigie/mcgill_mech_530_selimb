@echo off
::http://superuser.com/questions/246837/how-do-i-add-text-to-the-beginning-of-a-file-in-bash
::START FROM mech_530
::Use %1 to refer to command line argument (the html)
::Use %~n1 to strip extension
set str=%~n1
echo %str%
set assnum=%str:~-1%
echo %assnum%
ipython nbconvert --to html --template html_nocode.tpl %1
set notebookfile=notebook_%assnum%
wkhtmltopdf --image-quality 300 %str%.html docs/%notebookfile%.pdf
del %str%.html
cd docs
set /P thedate=Enter due date without year.
set titlefile=titlepage_%assnum%
PAUSE
echo \def\assnum{%assnum%}\def\thedate{%thedate%, 2014} | cat - composites_template.tex > %titlefile%.tex
PAUSE
pdflatex %titlefile%.tex
pdftk %titlefile%.pdf %notebookfile%.pdf cat output composites_%assnum%.pdf
del %titlefile%*.*
del %notebookfile%*.*