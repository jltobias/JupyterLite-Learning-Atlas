"""Exact reviewed optional frontend cells; no substring can authorize a skip."""
import hashlib

WIDGET_CELLS={
 'courses/destination-earth-digital-twin/14-maps.ipynb':('91bc05e1c426ae26','4b0ab1b5e348b180c3fed526c3faf4f1b712709ac00653fdd1d55c3787834aaa'),
 'courses/destination-earth-digital-twin/16-terrain.ipynb':('d71417a946a12101','faa2831634ad8288b267c9b91e13255333752db66670dda334a2a710f69280d0'),
 'courses/destination-earth-digital-twin/17-globe.ipynb':('5044b6ca60f4c515','e1263c655fb575b06b7bac476313b0e3562bfe9bdaf573529f1165f4b753f6e4'),
 'courses/destination-earth-digital-twin/18-time.ipynb':('20e59c303dde708f','4b0ab1b5e348b180c3fed526c3faf4f1b712709ac00653fdd1d55c3787834aaa'),
 'courses/destination-earth-digital-twin/19-dashboard.ipynb':('f7721549aecc8e3e','30c850cf6fb68504c350d09e2434307427a53599b6d37f69fe1bff03913bb03f'),
}


def reviewed_widget_indices(notebook,nb,*,browser=False):
    if browser and notebook!='courses/destination-earth-digital-twin/17-globe.ipynb':
        raise ValueError('Browser widget skip is reviewed only for the DestinE globe')
    expected=WIDGET_CELLS.get(notebook)
    candidates=[i for i,c in enumerate(nb.cells) if c.cell_type=='code' and 'widgets.interactive(' in c.source]
    if expected is None:
        if candidates:raise ValueError('Unreviewed optional widget cell: '+notebook)
        return []
    identity,digest=expected
    matches=[i for i,c in enumerate(nb.cells) if c.get('id')==identity]
    if matches!=[9] or candidates!=[9] or nb.cells[9].cell_type!='code' or hashlib.sha256(nb.cells[9].source.encode()).hexdigest()!=digest:
        raise ValueError('Reviewed optional widget cell changed: '+notebook)
    return matches
