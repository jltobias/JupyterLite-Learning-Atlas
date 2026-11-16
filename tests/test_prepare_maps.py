"""Offline reconciliation rejects corrupt gauge derivatives and source captures."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_maps import GAUGES, verify_gauges


class GaugePreparationTests(unittest.TestCase):
    def fixture(self, folder):
        destination=Path(folder)
        for name in GAUGES: shutil.copyfile(ROOT/'site/data'/name,destination/name)
        return destination

    def test_complete_bundle_reconciles_all_source_rows(self):
        data=verify_gauges(ROOT/'site/data')
        self.assertEqual(len(data['time_utc']),672)
        self.assertEqual([s['window_mean_sea_level_mm'] for s in data['stations']],[1745.2276785714287,2901.65625])
        self.assertIn('1993\u20132021',data['selection_note'])
        self.assertEqual([s['sea_level_mm'][123] for s in data['stations']],[1966,2683])

    def test_derived_metadata_and_numerical_mutations_are_rejected(self):
        mutations=[
            ('timestamps',lambda d:d['time_utc'].__setitem__(123,'1994-07-06T04:00:00Z')),
            ('window bounds',lambda d:d.__setitem__('window_start_utc','1994-07-02T00:00:00Z')),
            ('sample interval',lambda d:d.__setitem__('sample_interval_seconds',7200)),
            ('metadata hash',lambda d:d.__setitem__('source_metadata_sha256','0'*64)),
            ('producer license',lambda d:d.__setitem__('source_license_statement','CC0')),
            ('station identity',lambda d:d['stations'][0].__setitem__('latitude',6.0)),
            ('source hash',lambda d:d['stations'][0].__setitem__('source_sha256','0'*64)),
            ('source query',lambda d:d['stations'][0].__setitem__('source_url','https://example.invalid')),
            ('CSV units',lambda d:d['stations'][0].__setitem__('source_units','metres')),
            ('station datum',lambda d:d['stations'][0].__setitem__('reference_datum','MSL')),
            ('quality array',lambda d:d['stations'][0].__setitem__('source_quality_values',[3])),
            ('derived quality array',lambda d:d['stations'][0].__setitem__('quality',[4]*671)),
            ('raw readings',lambda d:d['stations'][0]['sea_level_mm'].__setitem__(123,1967)),
            ('raw readings',lambda d:d['stations'][0]['sea_level_mm'].__setitem__(123,None)),
            ('counts/missingness',lambda d:d['stations'][0].__setitem__('missing_count',1)),
            ('raw range',lambda d:d['stations'][0].__setitem__('source_range_mm',[1000,2330])),
            ('window mean',lambda d:d['stations'][0].__setitem__('window_mean_sea_level_mm',1745)),
            ('derived anomalies',lambda d:d['stations'][0]['observed_anomaly_m'].__setitem__(123,.220773)),
        ]
        with tempfile.TemporaryDirectory() as folder:
            destination=self.fixture(folder)
            original=json.loads((destination/GAUGES[0]).read_text(encoding='utf-8'))
            for message, mutate in mutations:
                with self.subTest(message=message):
                    data=copy.deepcopy(original);mutate(data)
                    (destination/GAUGES[0]).write_text(json.dumps(data),encoding='utf-8')
                    with self.assertRaisesRegex(AssertionError,message):verify_gauges(destination)

    def test_original_response_and_metadata_bytes_are_pinned(self):
        for name in GAUGES[1:]:
            with self.subTest(source=name), tempfile.TemporaryDirectory() as folder:
                destination=self.fixture(folder)
                with (destination/name).open('ab') as stream:stream.write(b'\n')
                with self.assertRaisesRegex(AssertionError,'source response hash'):verify_gauges(destination)

    def test_gallery_keeps_external_entries_and_local_self_coverage(self):
        catalog=json.loads((ROOT/'catalog/map-resources.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['resources']),100)
        self.assertEqual(len(catalog['repository_coverage']),68)
        coverage=next(r for r in catalog['repository_coverage'] if r['repository']=='JupyterLite-Learning-Atlas')
        self.assertIn('local Map and Scene Atlas studio',coverage['map_status'])
        self.assertEqual((ROOT/'catalog/map-resources.json').read_bytes(),(ROOT/'site/data/map-resources.json').read_bytes())


if __name__=='__main__':unittest.main()
