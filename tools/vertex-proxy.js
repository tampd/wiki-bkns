/**
 * Vertex AI Auth Proxy for OpenClaw
 *
 * Handles:
 * 1. Auto-refresh GCP access token from service account
 * 2. Forwards /chat/completions directly to Vertex AI
 * 3. Converts OpenAI Responses API (/responses) → /chat/completions
 *    then re-emits response as SSE streaming events in Responses API format
 *    (OpenClaw uses openai-responses transport which expects SSE streaming)
 *
 * @version 1.2.0
 * @date 2026-04-16
 * @changelog
 *   v1.2.0 - Fix: return SSE streaming events for /responses (fixes payloads=0 / incomplete turn)
 *   v1.1.0 - Add /responses → /chat/completions conversion (fix 400 error)
 *   v1.0.0 - Initial proxy with token auto-refresh
 */

const http = require('http');
const https = require('https');
const { execSync } = require('child_process');

// --- Configuration ---
const PORT = 19010;
const SA_PATH = process.env.GOOGLE_APPLICATION_CREDENTIALS || '/wiki/service-account.json';
const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || 'ai-test-491016';
const LOCATION = process.env.GOOGLE_CLOUD_LOCATION || 'us-central1';
const TARGET_BASE = `https://${LOCATION}-aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/endpoints/openapi`;

// --- Token Cache ---
let cachedToken = null;
let tokenExpiry = 0;

function getAccessToken() {
  const now = Date.now();
  if (cachedToken && now < tokenExpiry - 300000) return cachedToken;

  try {
    const token = execSync(
      `python3 -c "
from google.oauth2 import service_account
import google.auth.transport.requests
creds = service_account.Credentials.from_service_account_file(
    '${SA_PATH}',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
request = google.auth.transport.requests.Request()
creds.refresh(request)
print(creds.token)
"`,
      { encoding: 'utf-8', timeout: 10000 }
    ).trim();
    cachedToken = token;
    tokenExpiry = now + 3600000;
    console.log(`[vertex-proxy] Token refreshed at ${new Date().toISOString()}`);
    return token;
  } catch (err) {
    console.error('[vertex-proxy] Token refresh failed:', err.message);
    return cachedToken;
  }
}

// --- Responses API → Chat Completions Converter ---
// OpenClaw uses OpenAI Responses API format; Vertex AI only supports Chat Completions.

function responsesToChatRequest(body) {
  // input can be a string or array of {role, content} items
  let messages = [];

  // system prompt from instructions field
  if (body.instructions) {
    messages.push({ role: 'system', content: body.instructions });
  }

  if (typeof body.input === 'string') {
    messages.push({ role: 'user', content: body.input });
  } else if (Array.isArray(body.input)) {
    for (const item of body.input) {
      if (item.type === 'message' || item.role) {
        const role = item.role || 'user';
        let content = '';
        if (typeof item.content === 'string') {
          content = item.content;
        } else if (Array.isArray(item.content)) {
          // content parts array
          content = item.content
            .filter(p => p.type === 'input_text' || p.type === 'text' || p.type === 'output_text')
            .map(p => p.text || p.value || '')
            .join('');
        }
        messages.push({ role, content });
      }
    }
  }

  const chatReq = {
    model: body.model,
    messages,
    stream: false, // Vertex AI requires explicit stream:false to return full response
  };
  if (body.max_output_tokens) chatReq.max_tokens = body.max_output_tokens;
  if (body.temperature !== undefined) chatReq.temperature = body.temperature;
  if (body.top_p !== undefined) chatReq.top_p = body.top_p;
  return chatReq;
}

// Emit SSE streaming events for /responses
// OpenClaw uses openai-responses transport which calls client.responses.create() with stream:true,
// so it expects SSE events — NOT a plain JSON response object.
function emitResponsesSSE(res, chatData, originalId) {
  const choice = chatData.choices?.[0];
  const text = choice?.message?.content || '';
  const responseId = originalId || `resp_${Date.now()}`;
  const msgId = `msg_${Date.now()}`;

  const sse = (obj) => `data: ${JSON.stringify(obj)}\n\n`;

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });

  // 1. response.created
  res.write(sse({
    type: 'response.created',
    response: {
      id: responseId,
      object: 'response',
      status: 'in_progress',
      model: chatData.model || '',
      output: [],
    },
  }));

  // 2. response.output_item.added (message item)
  res.write(sse({
    type: 'response.output_item.added',
    output_index: 0,
    item: {
      id: msgId,
      type: 'message',
      role: 'assistant',
      status: 'in_progress',
      content: [],
    },
  }));

  // 3. response.output_text.delta (full text as single delta)
  if (text) {
    res.write(sse({
      type: 'response.output_text.delta',
      item_id: msgId,
      output_index: 0,
      content_index: 0,
      delta: text,
    }));
  }

  // 4. response.output_item.done
  res.write(sse({
    type: 'response.output_item.done',
    output_index: 0,
    item: {
      id: msgId,
      type: 'message',
      role: 'assistant',
      status: 'completed',
      content: [{ type: 'output_text', text }],
    },
  }));

  // 5. response.completed
  res.write(sse({
    type: 'response.completed',
    response: {
      id: responseId,
      object: 'response',
      status: 'completed',
      model: chatData.model || '',
      output: [{
        id: msgId,
        type: 'message',
        role: 'assistant',
        status: 'completed',
        content: [{ type: 'output_text', text }],
      }],
      usage: {
        input_tokens: chatData.usage?.prompt_tokens || 0,
        output_tokens: chatData.usage?.completion_tokens || 0,
        total_tokens: chatData.usage?.total_tokens || 0,
      },
    },
  }));

  res.end();
}

// --- Forward request to Vertex AI ---
function forwardToVertex(targetPath, method, bodyStr, token) {
  return new Promise((resolve, reject) => {
    const targetUrl = new URL(TARGET_BASE + targetPath);
    const bodyBuf = Buffer.from(bodyStr, 'utf-8');
    const options = {
      hostname: targetUrl.hostname,
      port: 443,
      path: targetUrl.pathname + targetUrl.search,
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Content-Length': bodyBuf.length,
      },
    };

    const req = https.request(options, (res) => {
      let data = [];
      res.on('data', c => data.push(c));
      res.on('end', () => resolve({ status: res.statusCode, body: Buffer.concat(data).toString() }));
    });
    req.on('error', reject);
    req.write(bodyBuf);
    req.end();
  });
}

// --- Main Server ---
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', target: TARGET_BASE, version: '1.2.0' }));
    return;
  }

  let chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', async () => {
    const rawBody = Buffer.concat(chunks).toString();
    const token = getAccessToken();

    if (!token) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Failed to get GCP access token' }));
      return;
    }

    let parsedBody;
    try { parsedBody = JSON.parse(rawBody); } catch { parsedBody = {}; }
    const model = parsedBody.model || '?';

    try {
      // --- /responses → /chat/completions conversion ---
      // OpenClaw uses openai-responses transport (stream:true) expecting SSE events.
      // Vertex AI only supports /chat/completions (non-streaming). We bridge the gap:
      // receive /responses → forward as /chat/completions with stream:false → re-emit as SSE.
      if (req.url === '/responses' || req.url.endsWith('/responses')) {
        console.log(`[vertex-proxy] CONVERT /responses -> /chat/completions model=${model}`);

        const chatReqBody = JSON.stringify(responsesToChatRequest(parsedBody));
        const result = await forwardToVertex('/chat/completions', req.method, chatReqBody, token);

        console.log(`[vertex-proxy] /responses model=${model} -> ${result.status}`);

        if (result.status === 200) {
          let chatData;
          try { chatData = JSON.parse(result.body); } catch { chatData = {}; }
          console.log(`[vertex-proxy] /responses emitting SSE, text_len=${chatData.choices?.[0]?.message?.content?.length || 0}`);
          emitResponsesSSE(res, chatData, parsedBody.id);
        } else {
          // Pass through error as-is
          res.writeHead(result.status, { 'Content-Type': 'application/json' });
          res.end(result.body);
        }
        return;
      }

      // --- Direct proxy for /chat/completions and others ---
      // Ensure stream:false so Vertex AI returns the full response body
      if ((req.url === '/chat/completions' || req.url.endsWith('/chat/completions')) && parsedBody) {
        parsedBody.stream = false;
      }
      const targetUrl = new URL(TARGET_BASE + req.url);
      const bodyBuf = Buffer.from(JSON.stringify(parsedBody), 'utf-8');
      const options = {
        hostname: targetUrl.hostname,
        port: 443,
        path: targetUrl.pathname + targetUrl.search,
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Content-Length': Buffer.byteLength(bodyBuf),
        },
      };

      const proxyReq = https.request(options, (proxyRes) => {
        console.log(`[vertex-proxy] ${req.method} ${req.url} model=${model} -> ${proxyRes.statusCode}`);
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
      });

      proxyReq.on('error', (err) => {
        console.error(`[vertex-proxy] ${req.method} ${req.url} model=${model} -> ERROR: ${err.message}`);
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      });

      proxyReq.write(bodyBuf);
      proxyReq.end();

    } catch (err) {
      console.error(`[vertex-proxy] Unhandled error: ${err.message}`);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[vertex-proxy] v1.2.0 Listening on http://127.0.0.1:${PORT}`);
  console.log(`[vertex-proxy] Target: ${TARGET_BASE}`);
  console.log(`[vertex-proxy] SA: ${SA_PATH}`);
  getAccessToken();
});
