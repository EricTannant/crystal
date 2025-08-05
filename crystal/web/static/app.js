// Crystal Personal Assistant - Web Interface JavaScript

class CrystalChat {
  constructor() {
    this.chatContainer = document.getElementById("chat-container");
    this.messageInput = document.getElementById("message-input");
    this.sendButton = document.getElementById("send-button");
    this.ws = null;

    this.initializeEventListeners();
    this.connectWebSocket();
    this.addMessage(
      "system",
      "Welcome to Crystal! Ruby is ready to assist you."
    );
  }

  connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("WebSocket connected");
        this.updateStatus("Connected to Ruby");
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.addMessage("assistant", data.message || "No response received");
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        this.updateStatus("Disconnected - trying to reconnect...");
        setTimeout(() => this.connectWebSocket(), 3000);
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        this.updateStatus("Connection error - using API fallback");
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      this.updateStatus("WebSocket not available - using API fallback");
    }
  }

  initializeEventListeners() {
    this.sendButton.addEventListener("click", () => this.sendMessage());
    this.messageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.sendMessage();
      }
    });
  }

  async sendMessage() {
    const message = this.messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    this.addMessage("user", message);
    this.messageInput.value = "";

    // Show thinking indicator
    const thinkingId = this.addMessage("assistant", "Ruby is thinking...");

    try {
      // Try WebSocket first
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ message: message }));
        this.removeMessage(thinkingId);
        return;
      }

      // Fall back to HTTP API
      const response = await fetch("/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Remove thinking indicator and add response
      this.removeMessage(thinkingId);
      this.addMessage(
        "assistant",
        data.message || "Sorry, I encountered an error processing your request."
      );
    } catch (error) {
      this.removeMessage(thinkingId);
      this.addMessage(
        "assistant",
        "Sorry, I encountered a connection error. Please try again."
      );
      console.error("Chat error:", error);
    }
  }

  updateStatus(status) {
    const statusElement = document.querySelector(".status");
    if (statusElement) {
      statusElement.textContent = status;
    }
  }

  addMessage(sender, content) {
    const messageId = Date.now().toString();
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;
    messageDiv.id = messageId;
    messageDiv.textContent = content;

    this.chatContainer.appendChild(messageDiv);
    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;

    return messageId;
  }

  removeMessage(messageId) {
    const element = document.getElementById(messageId);
    if (element) {
      element.remove();
    }
  }
}

// Initialize chat when page loads
document.addEventListener("DOMContentLoaded", () => {
  new CrystalChat();
});
