const http = require('http');

const PORT = 8011;
const TARGET_HOST = '127.0.0.1';
const TARGET_PORT = 80;

const server = http.createServer((req, res) => {
    // Enable CORS for the local browser frontend
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Target-Host');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Default to sklearn-iris, but allow an override via headers
    const customHost = req.headers['target-host'] || 'sklearn-iris.kserve-test.example.com';

    const options = {
        hostname: TARGET_HOST,
        port: TARGET_PORT,
        path: req.url,
        method: req.method,
        headers: {
            ...req.headers,
            'host': customHost,
            'content-type': req.headers['content-type'] || 'application/json'
        }
    };

    // Clean headers before sending to Istio Envoy
    delete options.headers['target-host'];
    delete options.headers['origin'];
    delete options.headers['referer'];
    delete options.headers['host']; // delete old host (localhost:8011)

    // Explicitly set the host expected by Istio
    options.headers['Host'] = customHost;

    const proxyReq = http.request(options, (proxyRes) => {
        // Forward response headers back to browser
        Object.keys(proxyRes.headers).forEach(key => {
            res.setHeader(key, proxyRes.headers[key]);
        });
        res.writeHead(proxyRes.statusCode);
        proxyRes.pipe(res, { end: true });
    });

    req.pipe(proxyReq, { end: true });

    proxyReq.on('error', (err) => {
        res.writeHead(500);
        res.end(`Proxy Error: ${err.message}`);
    });
});

server.listen(PORT, () => {
    console.log(`CORS Proxy running on http://localhost:${PORT}`);
    console.log(`Forwarding all requests to Minikube KServe Ingress at http://${TARGET_HOST}:${TARGET_PORT}`);
    console.log(`Injecting required Istio Host header.`);
});
