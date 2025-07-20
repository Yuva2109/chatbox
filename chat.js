/* chat.js */
const username = localStorage.getItem("chatbox_username");
const password = localStorage.getItem("chatbox_password");

if (!username || !password) {
  alert("You must log in first.");
  window.location.href = "index.html";
}

document.getElementById("username-label").textContent = username;
const wsChat = new WebSocket("ws://localhost:8081");

wsChat.onopen = () => {
  
};

wsChat.onmessage = (event) => {
  const msg = event.data.toLowerCase();
  console.log("[Server]:", msg);

  if (msg.includes("do you want to")) {
    wsChat.send("login");
  } else if (msg.includes("username:")) {
    wsChat.send(username);
  } else if (msg.includes("password:")) {
    wsChat.send(password);
  }  else if (msg.includes("welcome")) {
    loggedIn = true;
    displayMessage(event.data);
    console.log("[Login Success] Waiting for any offline messages...");
  } else if (loggedIn) {
    console.log("📩 Offline/Other message:", event.data);  
    displayMessage(event.data);  
  }
};

function sendMessage() {
  const msg = document.getElementById("message-input").value.trim();
  const toUser = document.getElementById("to-user").value.trim();

  if (msg && wsChat.readyState === WebSocket.OPEN) {
    if (toUser) {
      wsChat.send(`@${toUser} ${msg}`);
      displayMessage(`[To @${toUser}] ${msg}`);
    } else {
      alert("Please enter a recipient username.");
    }
    document.getElementById("message-input").value = "";
  }
}

function displayMessage(msg) {
  const container = document.getElementById("messages");
  const div = document.createElement("div");
  div.textContent = msg;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

document.getElementById("send-btn").onclick = sendMessage;
document.getElementById("message-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
