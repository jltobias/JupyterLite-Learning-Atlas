"""The README metadata chart must track the growing catalog without clipping."""
from collections import Counter
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


class CatalogArtworkTests(unittest.TestCase):
    def test_current_chart_counts_date_and_bars_match_catalog(self):
        records=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))['repositories']
        tree=ET.fromstring((ROOT/'assets/repository-overview.svg').read_text(encoding='utf-8'))
        ns={'s':'http://www.w3.org/2000/svg'}
        labels=[n.text for n in tree.findall('.//s:text',ns)]
        counts=Counter(r['theme'] for r in records)
        self.assertEqual(labels[1:-1:2],list(counts))
        self.assertEqual([int(n) for n in labels[2:-1:2]],list(counts.values()))
        self.assertIn(str(len(records))+' public project chapters',labels[-1])
        self.assertIn(max(r['inspected_on'] for r in records),labels[-1])
        _,_,width,height=map(float,tree.attrib['viewBox'].split())
        for rect in tree.findall('.//s:rect',ns):
            self.assertLessEqual(float(rect.get('x',0))+float(rect.attrib['width']),width)
            self.assertLessEqual(float(rect.get('y',0))+float(rect.attrib['height']),height)


if __name__=='__main__':unittest.main()
