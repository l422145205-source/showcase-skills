"""Behavior checks for evidence, readable animations and non-destructive embeds."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/repo-pet/scripts'))
import repopet as rp


class Workspace(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def evidence(self, xml):
        path = self.root / 'junit.xml'
        path.write_text(xml, encoding='utf-8')
        return rp.junit_evidence(path)

    def check(self, data):
        path = self.root / 'check.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return rp.checks_evidence(path)


class EvidenceTests(Workspace):
    def test_nested_suites_are_not_double_counted(self):
        result = self.evidence('<testsuites tests="500"><testsuite tests="500">'
                               '<testcase name="one"/><testcase name="two"/>'
                               '</testsuite></testsuites>')
        self.assertEqual((result['mood'], result['tests'], result['passed']), ('passing', 2, 2))

    def test_namespaces_and_mixed_results(self):
        result = self.evidence('<testsuite xmlns="urn:junit"><testcase/>'
                               '<testcase><failure/></testcase><testcase><error/></testcase>'
                               '<testcase><skipped/></testcase></testsuite>')
        self.assertEqual(result['mood'], 'failing')
        self.assertEqual([result[k] for k in ('tests','passed','failures','errors','skipped')], [4,1,1,1,1])

    def test_all_skipped_is_not_green(self):
        result = self.evidence('<testsuite><testcase><skipped/></testcase></testsuite>')
        self.assertEqual((result['mood'], result['passed']), ('skipped', 0))

    def test_partial_skips_with_executed_passes(self):
        result = self.evidence('<testsuite><testcase/><testcase><skipped/></testcase></testsuite>')
        self.assertEqual((result['mood'], result['passed'], result['skipped']), ('passing',1,1))

    def test_aggregate_only_does_not_claim_passes(self):
        result = self.evidence('<testsuite tests="10" failures="0"/>')
        self.assertEqual((result['mood'], result['tests']), ('unknown',0))

    def test_invalid_and_unrelated_xml_stay_unknown(self):
        for xml in ['<broken', '<inventory><testcase/></inventory>',
                    '<!DOCTYPE x [<!ENTITY x "value">]><testsuite/>',
                    '<testsuite><testcase><failure/><skipped/></testcase></testsuite>']:
            with self.subTest(xml=xml):
                self.assertEqual(self.evidence(xml)['mood'], 'unknown')

    def test_missing_report_is_unknown(self):
        self.assertEqual(rp.junit_evidence(self.root/'missing.xml')['mood'], 'unknown')

    def test_oversized_report_is_rejected(self):
        self.assertEqual(self.evidence('<testsuite>'+(' '*5_000_001)+'</testsuite>')['mood'], 'unknown')

    def test_workflow_states(self):
        cases = [('queued',None,'running'),('in_progress',None,'running'),
                 ('completed','success','passing'),('completed','failure','failing'),
                 ('completed','timed_out','failing'),('completed','skipped','skipped'),
                 ('completed','cancelled','unknown'),('completed','neutral','unknown')]
        for status,conclusion,mood in cases:
            with self.subTest(status=status,conclusion=conclusion):
                result = self.check({'status':status,'conclusion':conclusion})
                self.assertEqual(result['mood'],mood)
                self.assertIsNone(result['tests'])

    def test_workflow_wrapper_discards_other_fields(self):
        result = self.check({'workflow_run':{'status':'completed','conclusion':'success',
                            'actor':{'email':'synthetic@example.invalid'},'html_url':'https://example.invalid'}})
        self.assertEqual(result['mood'],'passing')
        self.assertNotIn('example.invalid',json.dumps(result))

    def test_malformed_workflow_shapes(self):
        for data in [[],None,42,{'workflow_run':[]},{'status':'completed'}]:
            with self.subTest(data=data):
                self.assertEqual(self.check(data)['mood'],'unknown')

    def test_workflow_invalid_json(self):
        p = self.root/'bad.json'; p.write_text('{bad',encoding='utf-8')
        self.assertEqual(rp.checks_evidence(p)['mood'],'unknown')

    def test_auto_discovery_stays_in_target(self):
        (self.root/'reports').mkdir()
        (self.root/'reports/junit.xml').write_text('<testsuite><testcase/></testsuite>',encoding='utf-8')
        with patch.object(rp,'git_count',return_value=None):
            result=rp.make_snapshot(self.root)
        self.assertEqual(result['evidence']['mood'],'passing')
        self.assertEqual(result['stage'],'baby')
        self.assertNotIn(str(self.root),json.dumps(result))

    def test_stages_follow_available_history(self):
        for count,expected in [(0,'egg'),(2,'egg'),(3,'baby'),(24,'baby'),(25,'dragon'),(None,'baby')]:
            with self.subTest(count=count),patch.object(rp,'git_count',return_value=count):
                result=rp.make_snapshot(self.root)
                self.assertEqual(result['stage'],expected)
                self.assertEqual(result['evidence']['mood'],'unknown')

    def test_manual_stage_cannot_change_evidence(self):
        with patch.object(rp,'git_count',return_value=1):
            result=rp.make_snapshot(self.root,stage='dragon')
        self.assertEqual((result['stage'],result['stage_source']),('dragon','cosmetic'))
        self.assertEqual(result['evidence']['mood'],'unknown')

    def test_no_git_does_not_fail(self):
        self.assertIsNone(rp.git_count(self.root))

    def test_conflicting_evidence_requires_choice(self):
        with self.assertRaises(ValueError):rp.make_snapshot(self.root,junit='one',checks='two')


class EmbedTests(Workspace):
    def test_embed_preserves_content_and_is_idempotent(self):
        readme=self.root/'README.md'; readme.write_text('# My project\n\nKeep this.\n',encoding='utf-8')
        asset=self.root/'assets/pet (1).gif'
        rp.update_readme(readme,asset,name='Patch')
        first=readme.read_text(encoding='utf-8')
        rp.update_readme(readme,asset,name='Patch')
        self.assertEqual(readme.read_text(encoding='utf-8'),first)
        self.assertTrue(first.startswith('# My project\n\nKeep this.'))
        self.assertIn('assets/pet%20%281%29.gif',first)

    def test_updates_only_owned_block(self):
        readme=self.root/'README.md'
        original=f'Before\n{rp.START}\nold\n{rp.END}\nAfter\n'
        readme.write_text(original,encoding='utf-8')
        rp.update_readme(readme,self.root/'new.gif',name='Patch')
        value=readme.read_text(encoding='utf-8')
        self.assertTrue(value.startswith('Before\n'))
        self.assertTrue(value.endswith('\nAfter\n'))
        self.assertNotIn('\nold\n',value)

    def test_invalid_markers_leave_readme_unchanged(self):
        for original in [rp.START, rp.END, rp.END+rp.START, (rp.START+rp.END)*2]:
            with self.subTest(original=original):
                readme=self.root/'README.md'; readme.write_text(original,encoding='utf-8')
                with self.assertRaises(ValueError):rp.update_readme(readme,self.root/'pet.gif',name='Patch')
                self.assertEqual(readme.read_text(encoding='utf-8'),original)

    def test_name_cannot_insert_html(self):
        readme=self.root/'README.md'
        rp.update_readme(readme,self.root/'pet.gif',name='<img>[X]')
        self.assertNotIn('<img>',readme.read_text(encoding='utf-8'))


class AnimationTests(Workspace):
    def test_all_moods_animate(self):
        for mood in rp.MOODS:
            with self.subTest(mood=mood):
                frames=[rp.card(rp.demo_snapshot(mood),i) for i in range(24)]
                self.assertEqual(frames[0].size,(600,340))
                self.assertTrue(any(ImageChops.difference(frames[0],f).getbbox() for f in frames[1:]))

    def test_palettes_and_stages_change_art(self):
        base=rp.dragon('passing',0)
        for kwargs in [{'theme':'lilac'},{'theme':'peach'},{'stage':'egg'},{'stage':'dragon'}]:
            # Compare RGB as RGBA difference bounding boxes ignore RGB-only changes with equal alpha.
            alternate=rp.dragon('passing',0,**kwargs)
            self.assertIsNotNone(ImageChops.difference(base.convert('RGB'),alternate.convert('RGB')).getbbox())

    def test_render_exports_real_loop_and_snapshot(self):
        keep=self.root/'keep.txt';keep.write_text('keep',encoding='utf-8')
        snapshot=rp.demo_snapshot('failing')
        asset=rp.render(snapshot,self.root)
        with Image.open(asset) as gif:
            self.assertEqual(gif.size,(600,340))
            self.assertGreater(gif.n_frames,1)
            self.assertEqual(gif.info['loop'],0)
            for i in range(gif.n_frames):gif.seek(i);gif.load()
        with Image.open(self.root/'pet.png') as png:self.assertEqual(png.size,(600,340))
        self.assertEqual(json.loads((self.root/'status.json').read_text(encoding='utf-8')),snapshot)
        self.assertEqual(keep.read_text(encoding='utf-8'),'keep')

    def test_cli_without_evidence_renders_unknown(self):
        result=subprocess.run([sys.executable,str(ROOT/'skills/repo-pet/scripts/repopet.py'),
                               'render','--repo',str(self.root),'--out',str(self.root/'art')],
                               capture_output=True,text=True,check=True,timeout=30)
        self.assertEqual(json.loads(result.stdout)['mood'],'unknown')
        snapshot=json.loads((self.root/'art/status.json').read_text(encoding='utf-8'))
        self.assertFalse(snapshot['demo'])
        self.assertNotIn(str(self.root),json.dumps(snapshot))


if __name__=='__main__':unittest.main()
