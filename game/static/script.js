const boxes = document.querySelectorAll(".box");
let currentPlayer = "X";
let gameOver = false;

const winConditions = [
	[0, 1, 2], // top row
	[3, 4, 5], // middle row
	[6, 7, 8], // bottom row
	[0, 3, 6], // left col
	[1, 4, 7], // middle col
	[2, 5, 8], // right col
	[0, 4, 8], // diagonal
	[2, 4, 6], // diagonal
];

function checkWin() {
	for (const [a, b, c] of winConditions) {
		if (
			boxes[a].textContent &&
			boxes[a].textContent === boxes[b].textContent &&
			boxes[a].textContent === boxes[c].textContent
		) {
			return boxes[a].textContent; // returns 'X' or 'O'
		}
	}
	// Check draw — all cells filled, no winner
	if (Array.from(boxes).every((box) => box.textContent !== "")) {
		return "draw";
	}
	return null;
}

boxes.forEach((box) => {
	box.addEventListener("click", () => {
		if (gameOver || box.textContent !== "") return;

		box.textContent = currentPlayer;

		const result = checkWin();
		if (result === "draw") {
			document.querySelector(".turn-indicator").textContent = "It's a draw!";
			gameOver = true;
			return;
		}
		if (result) {
			document.querySelector(".turn-indicator").textContent = `${result} wins!`;
			gameOver = true;
			return;
		}

		currentPlayer = currentPlayer === "X" ? "O" : "X";
		document.querySelector(".turn-indicator").textContent =
			`${currentPlayer}'s turn`;
	});
});

function resetGame() {
	gameOver = false;
	currentPlayer = "X";
	boxes.forEach((box) => (box.textContent = ""));
	document.querySelector(".turn-indicator").textContent = "X's turn";
}

document.querySelector("#restartBtn").addEventListener("click", resetGame);

// Chat message logic
document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("userInput").addEventListener("keypress", function (e) {
	if (e.key === "Enter") sendMessage();
});

function sendMessage() {
	const input = document.getElementById("userInput");
	const message = input.value.trim();
	if (message) {
		appendMessage("user", message);
		// Simulate AI response after a short delay
		setTimeout(() => {
			appendMessage("bot", "I am an AI assistant. How can I help you?");
		}, 500);
		input.value = "";
	}
}

function appendMessage(sender, text) {
	const messagesContainer = document.querySelector(".chat-messages");
	const messageElement = document.createElement("div");
	messageElement.classList.add("message", sender + "-message");
	messageElement.textContent = text;
	messagesContainer.appendChild(messageElement);
	messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
