document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('userInput').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
  const input = document.getElementById('userInput');
  const message = input.value.trim();
  if (message) {
    appendMessage('user', message);
    // Simulate AI response after a short delay
    setTimeout(() => {
      appendMessage('bot', 'I am an AI assistant. How can I help you?');
    }, 500);
    input.value = '';
  }
}

function appendMessage(sender, text) {
  const messagesContainer = document.querySelector('.chat-messages');
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', sender + '-message');
  messageElement.textContent = text;
  messagesContainer.appendChild(messageElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}