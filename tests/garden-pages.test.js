const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

function inlineScript(file, blockName) {
  const source = fs.readFileSync(
    path.join(__dirname, '..', 'my-garden-theme', file),
    'utf8'
  );
  const block = source.slice(source.indexOf(blockName));
  const start = block.indexOf('<script>') + '<script>'.length;
  return block.slice(start, block.indexOf('</script>', start));
}

class Element {
  constructor() {
    this.children = [];
    this.attributes = {};
    this.hidden = false;
    this.style = {};
    this._textContent = '';
  }

  get textContent() {
    return this._textContent + this.children.map((child) => child.textContent || '').join('');
  }

  set textContent(value) {
    this._textContent = String(value);
    this.children = [];
  }

  get firstChild() {
    return this.children[0] || null;
  }

  appendChild(child) {
    this.children.push(child);
    return child;
  }
}

function makeDocument(ids) {
  return {
    title: 'digital garden',
    getElementById(id) { return ids[id]; },
    createElement(tagName) {
      const element = new Element();
      element.tagName = tagName;
      return element;
    },
    createTextNode(text) { return { textContent: text }; },
  };
}

test('search page marks results, announces the result count, and updates the title', async () => {
  const box = new Element();
  const count = new Element();
  const input = new Element();
  const document = makeDocument({
    'search-results': box,
    'search-count': count,
    'mkdocs-search-query': input,
  });
  const marked = [];
  const context = {
    URLSearchParams,
    base_url: 'https://example.test/garden',
    document,
    gardenMark(element, text, terms) {
      marked.push({ text, terms });
      element.textContent = text;
    },
    gardenSearch: async () => [{
      title: 'Book notes',
      url: 'buds/book/',
      snippet: 'Notes about books.',
      terms: ['book'],
    }],
    location: { search: '?q=book' },
  };

  vm.runInNewContext(inlineScript('search.html', '{% block extra_scripts %}'), context);
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(document.title, 'book | digital garden');
  assert.equal(count.textContent, '1 result for "book".');
  assert.deepEqual(marked.map((entry) => entry.text), ['Book notes', 'Notes about books.']);
  assert.deepEqual(marked[0].terms, ['book']);
});

test('404 suggestions compare the full site-relative path and omit private notes', async () => {
  const section = new Element();
  section.hidden = true;
  const list = new Element();
  const document = makeDocument({
    'did-you-mean': section,
    suggestions: list,
  });
  const notes = [
    { title: 'Test note 1', url: 'seedlings/test-note-1/', stage: 'seedling' },
    { title: 'Private test note', url: 'seedlings/test-note-11/', stage: 'seedling', unlisted: true },
    { title: 'Draft test note', url: 'seedlings/test-note-11/', stage: 'seedling', draft: true },
    { title: 'Stage index', url: 'seedlings/', stage: 'seedling', is_index: true },
  ];
  const context = {
    URL,
    base_url: 'https://example.test/garden',
    console,
    document,
    fetch: async (url) => ({
      ok: url === 'https://example.test/garden/notes.json',
      json: async () => notes,
    }),
    location: {
      href: 'https://example.test/garden/seedlings/test-note-11/',
      pathname: '/garden/seedlings/test-note-11/',
    },
  };

  vm.runInNewContext(
    inlineScript('404.html', '{% block extra_scripts %}'),
    context
  );
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(section.hidden, false);
  assert.equal(list.children.length, 1);
  assert.equal(list.children[0].children[0].textContent, 'Test note 1');
});

test('homepage note excerpt turns mentions of other notes into links', async () => {
  const today = new Element();
  const ids = {
    today,
    'clock-time': new Element(),
    'clock-date': new Element(),
  };
  const document = makeDocument(ids);
  document.hidden = true;
  document.addEventListener = () => {};
  const notes = [
    {
      title: 'First note',
      url: 'buds/first-note/',
      excerpt: 'Read The Second Note for more.',
      stage: 'bud',
    },
    {
      title: 'The Second Note',
      url: 'buds/second-note/',
      excerpt: 'Follow up.',
      stage: 'bud',
    },
  ];
  class FixedDate extends Date {
    static now() { return 0; }
  }
  const context = {
    Date: FixedDate,
    Intl,
    Math,
    base_url: 'https://example.test/garden',
    clearInterval() {},
    document,
    fetch: async () => ({
      ok: true,
      json: async () => vm.runInNewContext(JSON.stringify(notes)),
    }),
    setInterval() { return 1; },
  };

  vm.runInNewContext(
    inlineScript('home.html', '{% block extra_scripts %}'),
    context
  );
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(today.children.length, 2, today.textContent);
  const excerpt = today.children[1];
  assert.equal(excerpt.style.textAlign, 'center');
  const mention = excerpt.children.find((child) => child.tagName === 'a');
  assert.ok(mention);
  assert.equal(mention.textContent, 'The Second Note');
  assert.equal(mention.href, 'https://example.test/garden/buds/second-note/');
});
