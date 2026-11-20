// gui_server.js – kleiner lokaler Server für tool.html (nur auf diesem Computer erreichbar).
// Start: node gui_server.js   → http://localhost:8080
// Kann: tool.html/model.js/params.json ausliefern, params.json speichern (mit Backup), das Deck neu bauen.
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execFile } = require("child_process");

const DIR = __dirname;
const PORT = Number(process.env.PORT) || 8080;
const FILES = { "/": "tool.html", "/tool.html": "tool.html", "/model.js": "model.js", "/params.json": "params.json" };
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8" };

function send(res, code, body, type) {
  res.writeHead(code, { "Content-Type": type || "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(typeof body === "string" ? body : JSON.stringify(body));
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (c) => { data += c; if (data.length > 2e6) reject(new Error("zu gross")); });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

http.createServer(async (req, res) => {
  try {
    const url = req.url.split("?")[0];
    if (req.method === "GET" && FILES[url]) {
      const file = path.join(DIR, FILES[url]);
      return send(res, 200, fs.readFileSync(file, "utf8"), TYPES[path.extname(file)]);
    }
    if (req.method === "GET" && url === "/api/status") return send(res, 200, { server: true });
    if (req.method === "POST" && url === "/api/params") {
      const text = await readBody(req);
      const parsed = JSON.parse(text);                      // nur gültiges JSON speichern
      const neu = Object.assign({}, require("./params.json"), {});
      for (const k of Object.keys(parsed)) if (!(k in neu)) throw new Error("Unbekannter Parameter: " + k);
      require("./model.js").berechne(parsed);               // muss durchrechenbar sein
      fs.copyFileSync(path.join(DIR, "params.json"), path.join(DIR, "params.backup.json"));
      fs.writeFileSync(path.join(DIR, "params.json"), JSON.stringify(parsed, null, 2) + "\n");
      delete require.cache[require.resolve("./params.json")];
      return send(res, 200, { ok: true, backup: "params.backup.json" });
    }
    if (req.method === "POST" && url === "/api/build") {
      return execFile(process.execPath, [path.join(DIR, "build_v2.js")], { cwd: DIR, timeout: 120000 }, (err, stdout, stderr) =>
        send(res, err ? 500 : 200, { ok: !err, stdout, stderr: stderr || (err && err.message) || "" }));
    }
    send(res, 404, { error: "nicht gefunden" });
  } catch (e) {
    send(res, 400, { ok: false, error: e.message });
  }
}).listen(PORT, "127.0.0.1", () => console.log(`Parameter-Tool läuft: http://localhost:${PORT}  (Beenden mit Ctrl+C)`));
