import os
import pathlib

import pygettext_modified as pygettext

# from shiftscheduler.i18n import pygettext 


ROOT_DIRECTORY = '../'
TEMPLATES_DIRECTORY = '../../locales/templates'


#def GetMatchingPotFile


def GeneratePotFiles():
    root_path = os.path.abspath(ROOT_DIRECTORY)
    root_path = pathlib.Path(root_path)
    templates_path = os.path.abspath(TEMPLATES_DIRECTORY)
    templates_path = pathlib.Path(templates_path)

    py_filepaths = list(pathlib.Path(root_path).glob('**/*.py'))
    pot_filepaths = []

    root_path_parts = root_path.parts

    for py_filepath in py_filepaths:
        stem = py_filepath.stem
        parts = list(py_filepath.parts)
        parts = parts[len(root_path_parts):]
        parts[-1] = stem + '.pot'

        outfile_path = templates_path.joinpath(*parts)
        pot_filepaths.append(outfile_path)

    filepaths = zip(py_filepaths, pot_filepaths)
    for py_path, pot_path in filepaths:
        #print(py_path)
        #print(pot_path)
        #print()
        pygettext.main(py_path, pot_path)


    

if __name__ == '__main__':
    GeneratePotFiles()