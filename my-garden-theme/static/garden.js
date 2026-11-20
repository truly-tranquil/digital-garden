/* Entry point: loads the page behaviour modules after the DOM is parsed. */

import { initTheme } from "./js/theme.js";
import { initLook } from "./js/look.js";
import { initSearch } from "./js/search.js";
import { initNav } from "./js/nav.js";
import { initHeader } from "./js/header.js";
import { initSprout } from "./js/sprout.js";
import { initReadAloud } from "./js/readaloud.js";
import { initTop } from "./js/top.js";
import { initTrail } from "./js/trail.js";
import { initMap } from "./js/map.js";

initTheme();
initLook();
initSearch();
initNav();
initHeader();
initSprout();
initReadAloud();
initTop();
initTrail();
initMap();
