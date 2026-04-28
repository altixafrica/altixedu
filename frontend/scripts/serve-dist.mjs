import { createReadStream, existsSync, statSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import http from 'node:http';
import url from 'node:url';

const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 4173);
const root = normalize(join(process.cwd(), 'dist'));

const MIME_TYPES = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
};

const sendFile = (res, filePath) => {
  const contentType = MIME_TYPES[extname(filePath).toLowerCase()] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': contentType });
  createReadStream(filePath).pipe(res);
};

const server = http.createServer((req, res) => {
  const pathname = url.parse(req.url || '/').pathname || '/';
  const requestedPath = normalize(join(root, pathname.replace(/^\/+/, '')));
  const safePath = requestedPath.startsWith(root) ? requestedPath : root;

  if (existsSync(safePath) && statSync(safePath).isFile()) {
    sendFile(res, safePath);
    return;
  }

  const indexPath = join(root, 'index.html');
  if (existsSync(indexPath)) {
    sendFile(res, indexPath);
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('dist/index.html not found');
});

server.listen(port, host, () => {
  process.stdout.write(`Static preview listening on http://${host}:${port}\n`);
});
