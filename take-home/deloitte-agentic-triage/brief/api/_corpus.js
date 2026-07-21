// Server-side view of the shared corpus — single source of truth lives in ../data.js
const { BRIEF_DATA } = require("../data.js");
module.exports = { CORPUS: BRIEF_DATA.corpus };
