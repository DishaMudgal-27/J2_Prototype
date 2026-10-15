// Browser-free render of j2_ui.html for tests: node j2_ui_render.js <j2_ui.html> <state.json> [previews.json]
// Runs the page's script against a stub DOM and prints {simple, sprog, cards: {workflow id: html}} as JSON.
const fs = require("fs"), vm = require("vm");
const [html, statePath, previewPath] = process.argv.slice(2);
const noop = () => noop;
const el = () => new Proxy({innerHTML: "", textContent: "", value: "", style: {}, dataset: {}, disabled: false, open: false,
  classList: {toggle: noop, add: noop, remove: noop, contains: () => false}, children: [], scrollHeight: 0},
  {get: (t, k) => k in t ? t[k] : k === "querySelectorAll" ? () => [] : noop, set: (t, k, v) => (t[k] = v, true)});
const els = {};
const ctx = vm.createContext({
  document: {getElementById: id => els[id] || (els[id] = el()), querySelector: () => el(), querySelectorAll: () => [],
             body: el(), addEventListener: noop, createElement: el},
  location: {search: "", href: ""}, localStorage: {getItem: () => null, setItem: noop}, CSS: {escape: x => x},
  fetch: () => Promise.reject(new Error("no network")), setTimeout: noop, setInterval: noop, requestAnimationFrame: noop,
  console, URLSearchParams, Date, JSON, Math, Set, Map, Promise});
const src = fs.readFileSync(html, "utf8"), scripts = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)];
vm.runInContext(scripts[scripts.length - 1][1], ctx);
const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
state.allChat = state.chat;
const previews = previewPath ? JSON.parse(fs.readFileSync(previewPath, "utf8")) : {};
const out = vm.runInContext(`(s, p) => { if (typeof PREVIEWS !== "undefined") Object.assign(PREVIEWS, p); renderSimple(s);
  return {simple: $("smsgs").innerHTML, sprog: $("sprog").innerHTML,
          cards: Object.fromEntries(s.workflows.map(w => [w.id, atomCards(s, w)]))}; }`, ctx)(state, previews);
console.log(JSON.stringify(out));
