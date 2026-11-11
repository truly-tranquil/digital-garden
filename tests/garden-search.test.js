const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'my-garden-theme', 'garden-search.js'),
  'utf8'
);

function createSearch(index, notes, options = {}) {
  const calls = [];
  class TestDOMParser {
    parseFromString(markup) {
      return {
        body: {
          textContent: String(markup)
            .replace(/<[^>]*>/g, '')
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>'),
        },
      };
    }
  }

  const context = {
    DOMParser: TestDOMParser,
    base_url: '',
    document: { getElementById: () => null },
    fetch(url) {
      calls.push(url);
      if (url.endsWith('/search/search_index.json')) {
        return Promise.resolve({
          ok: !options.failIndex,
          json: () => Promise.resolve({ docs: index }),
        });
      }
      return Promise.resolve({
        ok: !options.failNotes,
        json: () => Promise.resolve(notes),
      });
    },
    window: {},
  };
  vm.runInNewContext(source, context);
  return { search: context.window.gardenSearch, calls };
}

test('normalizes the search index once and returns only the best result per page', async () => {
  const docs = [
    { title: '<b>Alpha &amp; beta</b>', text: 'An alpha beta note.', location: 'buds/book/' },
    { title: 'Alpha beta details', text: 'alpha beta details', location: 'buds/book/#details' },
    { title: 'Alpha beta elsewhere', text: 'alpha beta elsewhere', location: 'buds/other/' },
  ];
  const { search, calls } = createSearch(docs, []);

  const first = await search('alpha beta', 5);
  const second = await search('alpha beta', 5);
  const bookHits = first.filter((hit) => hit.url.split('#')[0] === 'buds/book/');

  assert.equal(first.length, 2);
  assert.equal(bookHits.length, 1);
  assert.equal(bookHits[0].url, 'buds/book/');
  assert.equal(bookHits[0].title, 'Alpha & beta');
  assert.equal(second.length, 2);
  assert.deepEqual(calls, ['/search/search_index.json']);
});

test('treats a multiword hashtag as one tag slug and filters private notes', async () => {
  const notes = [
    {
      title: 'Book notes',
      url: 'buds/book/',
      tag_slugs: ['book-notes'],
      tags: ['Book Notes'],
      excerpt: 'A tagged note.',
    },
    { title: 'Book', url: 'buds/private/', tag_slugs: ['book-notes'], unlisted: true },
    { title: 'Draft', url: 'buds/draft/', tag_slugs: ['book-notes'], draft: true },
    { title: 'Other', url: 'buds/other/', tag_slugs: ['book'], tags: ['book'] },
  ];
  const { search, calls } = createSearch([], notes);

  const hits = await search('#book notes', 5);
  assert.equal(hits.length, 1);
  assert.equal(hits[0].url, 'buds/book/');
  assert.equal(hits[0].snippet, 'A tagged note.');
  assert.deepEqual(calls, ['/notes.json']);
});

test('rejects a failed index request instead of returning empty results', async () => {
  const { search } = createSearch([], [], { failIndex: true });
  await assert.rejects(search('garden'), /Search index request failed/);
});

test('rejects a failed notes request for tag searches', async () => {
  const { search } = createSearch([], [], { failNotes: true });
  await assert.rejects(search('#garden'), /Notes index request failed/);
});
