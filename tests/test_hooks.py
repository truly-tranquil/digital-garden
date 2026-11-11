import json
import os
import subprocess
import tempfile
import unittest
from urllib.parse import unquote
from xml.etree import ElementTree
from pathlib import Path
from unittest.mock import patch

import hooks


def make_note(title, body='', stage='bud', tags=None, is_index=False):
    return {
        'title': title,
        'url': title.lower().replace(' ', '-') + '/',
        'section': 'buds',
        'stage': stage,
        'tags': tags or [],
        'tag_slugs': [],
        'planted': None,
        'tended': '2026-01-01',
        'excerpt': '',
        'is_index': is_index,
        'unlisted': False,
        '_body': body,
        '_stem': title.lower().replace(' ', '-'),
        '_headings': hooks._heading_map(body),
        '_manual': [],
    }


class OutsideCodeTests(unittest.TestCase):
    def test_only_transforms_outside_protected_regions(self):
        source = (
            '[[link]]\n'
            '```md\n[[fenced]]\n```\n'
            '<!-- [[comment]] -->\n'
            '<pre><code>[[html code]]</code></pre>\n'
            '%% [[percent code]] %%\n'
            '`[[inline]]` [[visible]]'
        )
        transformed = hooks._outside_code(source, lambda text: text.replace('[[', 'LINK['))
        self.assertIn('LINK[link]]', transformed)
        self.assertIn('[[fenced]]', transformed)
        self.assertIn('[[comment]]', transformed)
        self.assertIn('[[html code]]', transformed)
        self.assertIn('[[percent code]]', transformed)
        self.assertIn('[[inline]]', transformed)
        self.assertIn('LINK[visible]]', transformed)

    def test_fence_with_language_is_not_a_closer(self):
        source = '```md\n[[hidden]]\n```python\n[[still hidden]]\n```\n[[visible]]'
        result = hooks._outside_code(source, lambda text: text.replace('[[', 'LINK['))
        self.assertIn('[[hidden]]', result)
        self.assertIn('[[still hidden]]', result)
        self.assertIn('LINK[visible]]', result)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.saved = (hooks.notes.copy(), hooks.lookup.copy(), hooks.media_lookup.copy())
        hooks.notes.clear()
        hooks.lookup.clear()
        hooks.media_lookup.clear()
        note = make_note('A target', '# A target\n\n## Named heading { #custom-anchor }\n')
        note['url'] = 'notes/a target.md'
        hooks.notes['notes/a target.md'] = note
        hooks.lookup['a target'] = 'notes/a target.md'
        hooks.lookup['a-target'] = 'notes/a target.md'
        hooks.notes['notes/current.md'] = make_note(
            'Current',
            '# Current\n\n## Local heading\n',
        )
        hooks.notes['notes/current.md']['_headings'] = {'current': 'current', 'local heading': 'local-heading'}
        hooks.media_lookup['picture.png'] = 'assets/picture name.png'

    def tearDown(self):
        hooks.notes.clear()
        hooks.notes.update(self.saved[0])
        hooks.lookup.clear()
        hooks.lookup.update(self.saved[1])
        hooks.media_lookup.clear()
        hooks.media_lookup.update(self.saved[2])

    def test_link_paths_are_encoded_and_heading_ids_are_respected(self):
        rendered = hooks._links(
            '[[a target]] [[a target#Named heading]] [[#Local heading]]',
            'notes/current.md',
        )
        self.assertIn('(a%20target.md)', rendered)
        self.assertIn('(a%20target.md#custom-anchor)', rendered)
        self.assertIn('(current.md#local-heading)', rendered)

    def test_escaped_pipes_and_image_dimensions(self):
        hooks.notes['notes/a|target.md'] = make_note('A|target')
        hooks.lookup['a|target'] = 'notes/a|target.md'
        rendered = hooks._links(
            r'[[a\|target]] ![[picture.png|100x200]]',
            'notes/current.md',
        )
        self.assertIn('(a%7Ctarget.md)', rendered)
        self.assertIn('![picture.png](../assets/picture%20name.png) { width="100" height="200" }', rendered)

    def test_markdown_extraction_matches_encoded_and_parenthesized_paths(self):
        self.assertEqual(
            hooks.MDLINK.findall('[one](folder/a%20note.md) [two](folder/file(name).md)'),
            ['folder/a%20note.md', 'folder/file(name).md'],
        )
        self.assertEqual(
            os.path.normpath(os.path.join('folder', unquote('a%20note.md'))),
            os.path.normpath('folder/a note.md'),
        )


class FileCollectionTests(unittest.TestCase):
    def setUp(self):
        self.saved = (hooks.notes.copy(), hooks.lookup.copy(), hooks.outgoing.copy(), hooks.backlinks.copy())

    def tearDown(self):
        hooks.notes.clear()
        hooks.notes.update(self.saved[0])
        hooks.lookup.clear()
        hooks.lookup.update(self.saved[1])
        hooks.outgoing.clear()
        hooks.outgoing.update(self.saved[2])
        hooks.backlinks.clear()
        hooks.backlinks.update(self.saved[3])

    def test_outgoing_links_ignore_examples_and_index_destinations(self):
        class File:
            def __init__(self, root, src_uri):
                self.src_uri = src_uri
                self.abs_src_path = os.path.join(root, *src_uri.split('/'))
                self.url = src_uri[:-3] + '/'

            def is_documentation_page(self):
                return True

        class Files(list):
            def documentation_pages(self):
                return self

        with tempfile.TemporaryDirectory() as root:
            sources = {
                'notes/source.md': (
                    '---\ntitle: Source\n---\n'
                    '[[Target]] [another](file(name).md) [encoded](space%20note.md) [index](index.md)\n'
                    '```md\n[[Code only]]\n```\n'
                    '<!-- [[Comment only]] -->\n'
                ),
                'notes/target.md': '# Target\n',
                'notes/file(name).md': '# Parenthesized file\n',
                'notes/space note.md': '# Encoded file\n',
                'notes/index.md': '# index\n',
                'notes/code-only.md': '# Code only\n',
            }
            files = Files()
            for src, body in sources.items():
                path = os.path.join(root, *src.split('/'))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                Path(path).write_text(body, encoding='utf-8')
                files.append(File(root, src))
            with patch.object(hooks, '_git_dates_for_files', return_value={}):
                hooks.on_files(files, {'config_file_path': os.path.join(root, 'mkdocs.yml')})
            titles = {link['title'] for link in hooks.outgoing['notes/source.md']}
            self.assertEqual(titles, {'Target', 'Parenthesized file', 'Encoded file'})
            self.assertEqual(hooks.outgoing['notes/index.md'], [])
            self.assertEqual(
                {link['title'] for link in hooks.backlinks['notes/target.md']},
                {'Source'},
            )


class SectionAndEmbedTests(unittest.TestCase):
    def setUp(self):
        self.saved = (hooks.notes.copy(), hooks.lookup.copy(), hooks.media_lookup.copy())
        hooks.notes.clear()
        hooks.lookup.clear()
        hooks.media_lookup.clear()
        body = (
            '# Target\n\n'
            '## Intro { #intro-custom }\n\n'
            '![photo](../assets/photo%20name.png)\n\n'
            '[another](../buds/bud%20note.md)\n\n'
            'A footnote[^a].\n\n[^a]: Footnote text\n\n'
            '## Next\n'
        )
        hooks.notes['library/target.md'] = make_note('Target', body)
        hooks.notes['library/target.md']['url'] = 'library/target/'
        hooks.lookup['target'] = 'library/target.md'

    def tearDown(self):
        hooks.notes.clear()
        hooks.notes.update(self.saved[0])
        hooks.lookup.clear()
        hooks.lookup.update(self.saved[1])
        hooks.media_lookup.clear()
        hooks.media_lookup.update(self.saved[2])

    def test_section_skips_code_headings_and_returns_custom_anchor(self):
        section, anchor = hooks._section(
            '## Intro { #intro-custom }\n```md\n## Next\n```\ntext\n## Next\n',
            'Intro',
        )
        self.assertEqual(anchor, 'intro-custom')
        self.assertIn('## Next', section)
        self.assertNotIn('\ntext\n', section)

    def test_embed_rewrites_paths_footnotes_and_heading_level(self):
        expanded = hooks._expand('![[Target]]', 'pages/host.md', ('pages/host.md',), 0)
        self.assertIn('../assets/photo%20name.png', expanded)
        self.assertIn('../buds/bud%20note.md', expanded)
        self.assertIn('### Intro { #embed-pages-host-library-target-1-intro-custom }', expanded)
        self.assertIn('[^embed-pages-host-library-target-1-a]', expanded)
        self.assertNotIn('\n## Intro', expanded)


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.saved = hooks.notes.copy()

    def tearDown(self):
        hooks.notes.clear()
        hooks.notes.update(self.saved)

    def test_title_and_excerpt_handle_markdown_safely(self):
        self.assertEqual(
            hooks._title_from_body('```md\n# Example\n```\n# **Real** title { #real-title }'),
            'Real title',
        )
        self.assertEqual(
            hooks._excerpt('> [!note] title\n> A *clear* sentence_with_underscores.'),
            'title A clear sentence_with_underscores.',
        )
        self.assertEqual(
            hooks._excerpt('````python\n# code\n````\nA sentence.'),
            'A sentence.',
        )

    def test_related_does_not_fill_with_unrelated_notes(self):
        hooks.notes.clear()
        hooks.notes.update({
            'a.md': make_note('A', stage='bud', tags=['one']),
            'b.md': make_note('B', stage='bud', tags=['two']),
        })
        self.assertEqual(hooks._related('a.md'), [])

    def test_home_context_uses_only_listed_staged_notes(self):
        hooks.notes.clear()
        public = make_note('Public', stage='seedling')
        public['tended'] = '2026-03-01'
        public['url'] = 'seedlings/public/'
        unlisted = make_note('Private', stage='bud')
        unlisted['unlisted'] = True
        draft = make_note('Draft', stage='evergreen')
        draft['draft'] = True
        non_note = make_note('About', stage=None, is_index=True)
        hooks.notes.update({
            'seedlings/public.md': public,
            'buds/private.md': unlisted,
            'evergreens/draft.md': draft,
            'about.md': non_note,
        })

        class File:
            src_uri = 'index.md'

        class Page:
            file = File()

        context = hooks.on_page_context({}, Page(), {}, None)
        self.assertEqual(context['garden_note_total'], 1)
        self.assertEqual(
            [(stat['stage'], stat['count']) for stat in context['garden_stage_stats']],
            [('seedling', 1), ('bud', 0), ('evergreen', 0)],
        )
        self.assertEqual([note['title'] for note in context['garden_recent']], ['Public'])

    def test_feed_alias_graph_and_suggestion_outputs(self):
        note = make_note('Public note', stage='bud', tags=['topic'])
        note.update({
            'url': 'buds/public-note/',
            'aliases': ['old-note', '../outside', 'C:\\outside'],
            'history': [{'date': '2026-01-01', 'hash': 'abc123', 'subject': 'Plant note'}],
        })
        draft = make_note('Draft note', stage='bud')
        draft['draft'] = True
        hooks.notes.update({'buds/public.md': note, 'buds/draft.md': draft})
        hooks.outgoing.clear()
        hooks.outgoing['buds/public.md'] = [{'title': 'Public note', 'url': 'buds/public-note/'}]
        with tempfile.TemporaryDirectory() as root:
            site_dir = os.path.join(root, 'site')
            os.makedirs(site_dir)
            hooks.on_post_build({
                'site_dir': site_dir,
                'site_name': 'Test garden',
                'site_url': 'https://garden.example/',
            })
            feed = ElementTree.parse(os.path.join(site_dir, 'feed.xml')).getroot()
            ns = {'atom': hooks.ATOM_NS}
            entries = feed.findall('atom:entry', ns)
            self.assertEqual(len(entries), 1)
            exported = json.loads(Path(site_dir, 'notes.json').read_text(encoding='utf-8'))
            self.assertEqual([item['title'] for item in exported], ['Public note'])
            self.assertTrue(os.path.isfile(os.path.join(site_dir, 'old-note', 'index.html')))
            self.assertFalse(os.path.exists(os.path.join(root, 'outside')))
            self.assertIn('sitemap.xml', Path(site_dir, 'robots.txt').read_text(encoding='utf-8'))
            graph = json.loads(Path(site_dir, 'graph.json').read_text(encoding='utf-8'))
            self.assertEqual(len(graph['nodes']), 1)
            self.assertEqual(len(graph['edges']), 1)
            graph_page = Path(site_dir, 'graph.html').read_text(encoding='utf-8')
            self.assertIn("*{cursor:url('assets/garden-cursor.svg') 1 1,auto}", graph_page)
            self.assertNotIn('garden-text-cursor', graph_page)
            suggestions = json.loads(Path(site_dir, 'suggestions.json').read_text(encoding='utf-8'))
            self.assertEqual([item['title'] for item in suggestions], ['Public note'])


class GitMetadataTests(unittest.TestCase):
    def test_reads_history_in_one_pass_and_skips_git_while_serving(self):
        class File:
            src_uri = 'notes/a.md'
            abs_src_path = ''

        with tempfile.TemporaryDirectory() as root:
            config_path = os.path.join(root, 'mkdocs.yml')
            Path(config_path).touch()
            file = File()
            file.abs_src_path = os.path.join(root, 'notes', 'a.md')

            class Files:
                def documentation_pages(self):
                    return [file]

            history = subprocess.CompletedProcess(
                'git log', 0,
                'COMMIT\t2025-01-02\tabc123\tFirst commit\nA\tnotes/a.md\n',
                '',
            )
            status = subprocess.CompletedProcess('git status', 0, ' M notes/a.md\0', '')
            with patch.object(hooks.shutil, 'which', return_value='git'), patch.object(
                hooks.subprocess, 'run', side_effect=[history, status],
            ) as run:
                result = hooks._git_dates_for_files(
                    {'config_file_path': config_path}, Files(),
                )
            self.assertEqual(run.call_count, 2)
            self.assertEqual(result['notes/a.md'][0], '2025-01-02')
            self.assertEqual(result['notes/a.md'][1], hooks.date.today().isoformat())
            self.assertEqual(result['notes/a.md'][2][0]['hash'], 'abc123')

            old_serving = hooks.serving
            hooks.serving = True
            try:
                with patch.object(hooks.subprocess, 'run', side_effect=AssertionError):
                    self.assertEqual(
                        hooks._git_dates_for_files({'config_file_path': config_path}, Files()),
                        {},
                    )
            finally:
                hooks.serving = old_serving


if __name__ == '__main__':
    unittest.main()
