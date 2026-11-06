import json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from demo import results
class CatalogTests(unittest.TestCase):
    def test_location_targets_exist(self):
        seed=json.loads((ROOT/'catalog-info.yaml').read_text())
        for name in seed['spec']['targets']:self.assertTrue((ROOT/name).is_file(),name)
    def test_catalog_refs_are_unique(self):
        refs=[]
        for p in (ROOT/'catalog').glob('*.yaml'):
            obj=json.loads(p.read_text());refs.append((obj['kind'],obj['metadata']['name']))
        self.assertEqual(len(refs),len(set(refs)))
    def test_services_have_ownership(self):
        for p in (ROOT/'catalog').glob('*.yaml'):
            obj=json.loads(p.read_text())
            if obj['kind']=='Component':self.assertTrue(obj['spec'].get('owner'))
    def test_preview_evidence_is_explicit(self):
        self.assertEqual([row['state'] for row in results()],['verified','unknown','conflict','stale'])
    def test_no_guest_provider_in_hosted_config(self):
        text=(ROOT/'reference/config/app-config.production.yaml').read_text()
        self.assertIn('userIdMatchingUserEntityAnnotation',text)
        self.assertNotIn('guest:',text)
