const fs = require("fs");
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const html = fs.readFileSync("um_dom.html", "utf8");
const dom = new JSDOM(html);
const document = dom.window.document;

function cleanHTML(html) {
  if (!html) return "";
  return html.replace(/\s+/g, " ").replace(/> </g, "><").trim();
}

console.log("--- HEADER ---");
const header = document.querySelector("header");
console.log(cleanHTML(header ? header.outerHTML : "").substring(0, 1500));

console.log("\n--- MAIN CONTENT SECTIONS ---");
const sections = document.querySelectorAll("section, .section");
sections.forEach((s, i) => {
  console.log(`\nSECTION ${i}: class="${s.className}" id="${s.id}"`);
  console.log(cleanHTML(s.outerHTML).substring(0, 500));
});

console.log("\n--- FOOTER ---");
const footer = document.querySelector("footer");
console.log(cleanHTML(footer ? footer.outerHTML : "").substring(0, 1500));
