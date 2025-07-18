let isSignup = false;
let ws;

const usernameInput = document.getElementById("username-input");
const passwordInput = document.getElementById("password-input");
const errorDisplay = document.getElementById("error-msg");
const togglePassword = document.getElementById("toggle-password");
const authBtn = document.getElementById("auth-btn");
const switchLink = document.getElementById("switch-link");

// Toggle password visibility
togglePassword.onclick = () => {
  passwordInput.type = passwordInput.type === "password" ? "text" : "password";
  togglePassword.textContent = passwordInput.type === "password" ? "👁️" : "🙈";
};

// Switch login/signup mode
switchLink.onclick = () => {
  isSignup = !isSignup;
  authBtn.textContent = isSignup ? "Sign Up" : "Login";
  document.getElementById("switch-auth-text").innerHTML = isSignup
    ? 'Already have an account? <span id="switch-link">Log in</span>'
    : 'Don\'t have an account? <span id="switch-link">Sign up</span>';
  document.getElementById("switch-link").onclick = arguments.callee;
};

// Handle auth button click
authBtn.onclick = () => {
  const username = usernameInput.value.trim();
  const password = passwordInput.value.trim();
  if (!username || !password) {
    errorDisplay.textContent = "Please enter both username and password.";
    return;
  }

  ws = new WebSocket("ws://localhost:8081");

  ws.onopen = () => {
    ws.send(isSignup ? "signup" : "login");
  };

  ws.onmessage = (event) => {
    const msg = event.data.toLowerCase();
    console.log("Server:", msg);

    if (msg.includes("username:")) {
      ws.send(username);
    } else if (msg.includes("password:")) {
      ws.send(password);
    } else if (msg.includes("welcome")) {
      localStorage.setItem("chatbox_username", username);
      localStorage.setItem("chatbox_password", password);
      window.location.href = "chat.html";
    } else {
      errorDisplay.textContent = msg;
    }
  };

  ws.onerror = (err) => {
    errorDisplay.textContent = "WebSocket error";
    console.error(err);
  };
};
