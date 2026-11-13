"""Keep required dataset credits visible in README, references and the Book.

The dataset register is human-reviewed. This module renders its marked blocks
and rejects missing file coverage; it does not infer copyright permissions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import nbformat

ROOT=Path(__file__).resolve().parents[1]
START='<!-- DATA_ATTRIBUTIONS:START -->'
END='<!-- DATA_ATTRIBUTIONS:END -->'
DATA_SUFFIXES={'.csv','.tsv','.json','.geojson','.npz','.npy','.zip','.tif','.tiff',
               '.xls','.xlsx','.shp','.dbf','.shx','.prj','.feather','.gpkg',
               '.graphml','.sqlite','.db','.parquet','.nc','.hdf','.h5'}


def render(register):
    clean=lambda value:str(value).replace('|','\\|').replace('\n',' ')
    lines=[START,'## Dataset citations and attribution register ('+register['inspected_on']+')','',
           register['introduction'],'',
           '| Bundled dataset / version | Required creator/source citation | Rights and conditions | Source preparation / Atlas use |',
           '|---|---|---|---|']
    for row in register['datasets']:
        use=row['modifications']+(' '+row['additional_notice'] if row.get('additional_notice') else '')
        lines.append('| '+' | '.join(map(clean,[row['title'],row['credit'],row['rights'],use]))+' |')
    lines+=['']
    for note in register['notes']:
        lines.extend([note,''])
    lines.append(END)
    return '\n'.join(lines)


def replace_block(text, block):
    assert text.count(START)==text.count(END)==1,'Dataset credit block markers missing/duplicated'
    before,rest=text.split(START,1)
    _,after=rest.split(END,1)
    return before+block+after


def validate_data_credits(root=ROOT):
    root=Path(root)
    register=json.loads((root/'catalog/data-attributions.json').read_text(encoding='utf-8'))
    library=json.loads((root/'catalog/source-library.json').read_text(encoding='utf-8'))
    rows=register['datasets']
    assert len({r['id'] for r in rows})==len(rows),'Duplicate dataset credit identifier'
    declared={entry['local_path'] for entry in library['support_files']}
    credited=set()
    for row in rows:
        assert all(row.get(key) for key in ['id','title','credit','rights','modifications','files']),row.get('id')
        assert set(row['files'])<=declared,'Dataset credits refer to an undeclared support file'
        credited.update(row['files'])
    required={path for path in declared if Path(path).suffix.lower() in DATA_SUFFIXES}
    assert required<=credited,'Dataset files missing README attribution: '+str(sorted(required-credited))
    block=render(register)
    for name in ['README.md','REFERENCES.md']:
        text=(root/name).read_text(encoding='utf-8')
        assert replace_block(text,block)==text,'Stale dataset credits: '+name
    text=nbformat.read(root/'content/references.ipynb',as_version=4).cells[0].source
    assert replace_block(text,block)==text,'Stale Book dataset credits'
    return {'dataset_families':len(rows),'credited_placements':len(credited),'required_data_placements':len(required)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Refresh only the marked dataset-credit blocks')
    args=parser.parse_args()
    register=json.loads((ROOT/'catalog/data-attributions.json').read_text(encoding='utf-8'))
    block=render(register)
    if args.write:
        for name in ['README.md','REFERENCES.md']:
            path=ROOT/name
            path.write_text(replace_block(path.read_text(encoding='utf-8'),block),encoding='utf-8')
        path=ROOT/'content/references.ipynb'
        notebook=nbformat.read(path,as_version=4)
        notebook.cells[0].source=replace_block(notebook.cells[0].source,block)
        nbformat.write(notebook,path)
    print(json.dumps(validate_data_credits()))


if __name__=='__main__':
    main()
