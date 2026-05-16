const fs = require("fs");
const html = fs.readFileSync("um_dom.html", "utf8");

// Find all CSS declarations for background-color within <style> tags
const styleTags = html.match(/<style[^>]*>([\s\S]*?)<\/style>/gi) || [];
const allCss = styleTags.map((tag) => tag.replace(/<\/?style[^>]*>/gi, "")).join("\n");

const colors = new Set();
const bgMatches =
  allCss.match(/background(?:-color)?:\s*(#[0-9a-fA-F]{3,6}|rgba?\([^)]+\))/gi) || [];
bgMatches.forEach((m) => colors.add(m.split(":")[1].trim()));

console.log("Background colors found in <style> tags:");
console.log(Array.from(colors));
