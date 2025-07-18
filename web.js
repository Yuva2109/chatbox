const WebSocket = require('ws');
const net = require('net');

// Configuration
const WS_PORT = 8081;            // WebSocket port
const TCP_SERVER_HOST = '127.0.0.1'; // Python TCP server address
const TCP_SERVER_PORT = 12345;   // Python TCP server port

// Create WebSocket Server
const wss = new WebSocket.Server({ port: WS_PORT });
console.log(`[Bridge] WebSocket server started on ws://localhost:${WS_PORT}`);

wss.on('connection', (ws) => {
    console.log(`[Bridge] New WebSocket client connected`);

    // Create TCP connection to Python server
    const tcpClient = new net.Socket();
    tcpClient.connect(TCP_SERVER_PORT, TCP_SERVER_HOST, () => {
        console.log(`[Bridge] Connected to TCP server`);
    });

    // WebSocket → TCP
    ws.on('message', (msg) => {
        console.log(`[WS → TCP]: ${msg}`);
        tcpClient.write(msg + '\n');  // Append newline for TCP server compatibility
    });

    // TCP → WebSocket
    tcpClient.on('data', (data) => {
        const message = data.toString();
        console.log(`[TCP → WS]: ${message}`);
        ws.send(message);
    });

    // Handle TCP disconnect
    tcpClient.on('close', () => {
        console.log(`[Bridge] TCP connection closed`);
        ws.close();
    });

    // Handle errors
    tcpClient.on('error', (err) => {
        console.error(`[Bridge] TCP error: ${err.message}`);
        ws.send('[Bridge Error] TCP server unavailable.');
        ws.close();
    });

    ws.on('close', () => {
        console.log(`[Bridge] WebSocket client disconnected`);
        tcpClient.end();
    });
});
