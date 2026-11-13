# Preview vs. Live Differences Analysis

## 1. Git dates skipped when serving
- **Status**: Confirmed
- **File/Line**: `hooks.py`, Line 150
- **Explanation**: The `serving` flag in `hooks.py` is set to `True` during serve mode, which forces `_git_dates_for_files` to return empty dictionaries. This affects "note of the day", recently tended, and the Atom feed.

## 2. Different build modes
- **Status**: Confirmed
- **File/Line**: `garden_build.py`, Lines 330, 350
- **Explanation**: `build()` calls `zensical build --strict`. `serve()` calls `zensical build` (without `--strict`). Strict mode can cause build failures or prune data that `serve` might tolerate.

## 3. Draft/unlisted handling
- **Status**: Can't tell
- **File/Line**: `garden_build.py`, Line 349 (prepare call)
- **Explanation**: Need to verify if `prepare(serving=True)` behaves differently regarding unlisted notes.

## 4. Search index path
- **Status**: Confirmed
- **File/Line**: `garden_build.py`, Line 309
- **Explanation**: `_write_search_index` is hard-coded to `output_dir / 'search' / 'search_index.json'`. When `build` uses `site` and `serve` uses `.garden-preview`, the search index is written to the build output. This seems correct for `build`, but might be misconfigured for `serve` if it expects it in `site/search.json` (which it does, see line 357).

## 5. Base path
- **Status**: Can't tell
- **Explanation**: Need to check if `zensical` config injection handles the `/digital-garden/` path prefix correctly.

## 6. Stale caches
- **Status**: Ruled out
- **Explanation**: I have manually cleared `.garden-build` and `site` during Phase 1.
