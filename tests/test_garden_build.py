import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import garden_build
import hooks


class GardenBuildTests(unittest.TestCase):
    def setUp(self):
        self.saved = {
            'notes': hooks.notes.copy(),
            'backlinks': hooks.backlinks.copy(),
            'outgoing': hooks.outgoing.copy(),
            'lookup': hooks.lookup.copy(),
            'media_lookup': hooks.media_lookup.copy(),
            'serving': hooks.serving,
        }
        hooks.notes.clear()
        hooks.backlinks.clear()
        hooks.outgoing.clear()
        hooks.lookup.clear()
        hooks.media_lookup.clear()

    def tearDown(self):
        for name in ('notes', 'backlinks', 'outgoing', 'lookup', 'media_lookup'):
            target = getattr(hooks, name)
            target.clear()
            target.update(self.saved[name])
        hooks.serving = self.saved['serving']

    def test_prepare_expands_links_and_builds_public_stage_navigation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'docs'
            (source / 'seedlings').mkdir(parents=True)
            (source / 'drafts').mkdir()
            (source / 'templates').mkdir()
            (source / 'seedlings' / 'index.md').write_text('# Seedlings\n', encoding='utf-8')
            (source / 'seedlings' / 'alpha.md').write_text(
                '---\ntags: [garden]\n---\n# Alpha\n\n[[Beta]]\n',
                encoding='utf-8',
            )
            (source / 'seedlings' / 'beta.md').write_text('# Beta\n', encoding='utf-8')
            (source / 'seedlings' / 'private.md').write_text(
                '---\nunlisted: true\n---\n# Private\n',
                encoding='utf-8',
            )
            (source / 'drafts' / 'draft.md').write_text('# Draft\n', encoding='utf-8')
            (source / 'templates' / 'note-template.md').write_text('# Template\n', encoding='utf-8')

            config_file = root / 'mkdocs.yml'
            config_file.write_text(
                'site_name: Garden\n'
                'site_url: https://example.test/garden/\n'
                'docs_dir: docs\n'
                'site_dir: site\n'
                'theme:\n'
                '  name: null\n'
                '  custom_dir: theme\n'
                'hooks: [hooks.py]\n'
                'exclude_docs: |\n'
                '  **/drafts/**\n'
                '  **/templates/**\n'
                'nav:\n'
                '  - home: index.md\n'
                '  - seedlings:\n'
                '      - index: seedlings/index.md\n',
                encoding='utf-8',
            )

            generated_docs = root / '.garden-build' / 'docs'
            generated_config = root / '.garden-zensical.yml'
            site_dir = root / 'site'
            preview_dir = root / '.garden-preview'
            with (
                patch.object(garden_build, 'ROOT', root),
                patch.object(garden_build, 'SOURCE_DIR', source),
                patch.object(garden_build, 'CONFIG_FILE', config_file),
                patch.object(garden_build, 'GENERATED_DOCS', generated_docs),
                patch.object(garden_build, 'GENERATED_CONFIG', generated_config),
                patch.object(garden_build, 'SITE_DIR', site_dir),
                patch.object(garden_build, 'PREVIEW_DIR', preview_dir),
            ):
                garden_build.prepare(serving=True)

            transformed = (generated_docs / 'seedlings' / 'alpha.md').read_text(encoding='utf-8')
            self.assertIn('[Beta](beta.md)', transformed)
            self.assertTrue((generated_docs / 'seedlings' / 'private.md').exists())
            self.assertFalse((generated_docs / 'drafts' / 'draft.md').exists())
            self.assertFalse((generated_docs / 'templates' / 'note-template.md').exists())
            self.assertEqual(
                list(garden_build._nav_paths(
                    garden_build.yaml.safe_load(generated_config.read_text(encoding='utf-8'))['nav']
                )),
                [
                    ('home', 'index.md'),
                    ('index', 'seedlings/index.md'),
                    ('Alpha', 'seedlings/alpha.md'),
                    ('Beta', 'seedlings/beta.md'),
                ],
            )
            generated = garden_build.yaml.safe_load(generated_config.read_text(encoding='utf-8'))
            self.assertNotIn('hooks', generated)
            self.assertNotIn('name', generated['theme'])
            self.assertEqual(generated['draft_docs'], '/seedlings/private.md')
            self.assertEqual(generated['site_dir'], '.garden-preview')

    def test_search_adapter_maps_zensical_items_and_drops_unlisted_notes(self):
        with tempfile.TemporaryDirectory() as temporary:
            site_dir = Path(temporary)
            (site_dir / 'search.json').write_text(json.dumps({
                'items': [
                    {'title': 'Public', 'text': '<p>Visible</p>', 'location': 'buds/public/'},
                    {'title': 'Private', 'text': '<p>Hidden</p>', 'location': 'buds/private/'},
                ],
            }), encoding='utf-8')
            hooks.notes['buds/private.md'] = {
                'url': 'buds/private/',
                'unlisted': True,
                'draft': False,
            }
            with patch.object(garden_build, 'SITE_DIR', site_dir):
                garden_build._write_search_index()

            result = json.loads(
                (site_dir / 'search' / 'search_index.json').read_text(encoding='utf-8')
            )
            zensical = json.loads((site_dir / 'search.json').read_text(encoding='utf-8'))
            self.assertEqual([item['title'] for item in zensical['items']], ['Public'])
            self.assertEqual(result['docs'], [{
                'title': 'Public',
                'text': '<p>Visible</p>',
                'location': 'buds/public/',
            }])

    def test_preview_assets_are_written_to_generated_docs_without_unlisted_notes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site_dir = root / 'site'
            generated_docs = root / 'generated-docs'
            site_dir.mkdir()
            (site_dir / 'search.json').write_text(json.dumps({
                'items': [{'title': 'Public', 'text': 'Visible', 'location': 'buds/public/'}],
            }), encoding='utf-8')
            hooks.notes.update({
                'buds/public.md': {
                    'title': 'Public',
                    'url': 'buds/public/',
                    'stage': 'bud',
                    'is_index': False,
                    'unlisted': False,
                    'draft': False,
                    'tended': '2026-01-01',
                    'excerpt': 'Visible',
                    'aliases': [],
                },
                'buds/private.md': {
                    'title': 'Private',
                    'url': 'buds/private/',
                    'stage': 'bud',
                    'is_index': False,
                    'unlisted': True,
                    'draft': False,
                    'tended': '2026-01-01',
                    'excerpt': 'Hidden',
                    'aliases': [],
                },
            })
            with (
                patch.object(garden_build, 'SITE_DIR', site_dir),
                patch.object(garden_build, 'GENERATED_DOCS', generated_docs),
            ):
                garden_build._write_search_index()
                garden_build._write_preview_assets({
                    'site_name': 'Garden',
                    'site_url': 'https://example.test/garden/',
                })

            preview_notes = json.loads((generated_docs / 'notes.json').read_text(encoding='utf-8'))
            self.assertEqual([note['title'] for note in preview_notes], ['Public'])
            self.assertTrue((generated_docs / 'search' / 'search_index.json').is_file())


if __name__ == '__main__':
    unittest.main()
