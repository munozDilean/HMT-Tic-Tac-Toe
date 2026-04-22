const boxes = document.querySelectorAll(".box");
let currentPlayer = "X";
let gameOver = false;
// Frustration Variables
let lastFrustrationTrigger = 0;
let lastMousePos = null;
let lastMouseTime = null;
let hesitationTimer = null;
const mouseData = [];

// Mouse Frustration detection
const FRUSTRATION_CONFIG = {
	velocityThreshold: 0.2,      // px/ms — erratic fast movement (average)
	directionChangeWindow: 50,    // look at last N mouse points
	directionChangeThreshold: 1,  // reversals within that window
	hesitationThreshold: 3500,    // ms idle = hesitation
	cooldown: 15000,              // ms before frustration can trigger again
};

document.addEventListener('mousemove', (e) => {
	const now = Date.now();
	const x = e.clientX;
	const y = e.clientY;

	// Always store
	mouseData.push({ x, y, timestamp: now });

	// Keep buffer small — only need recent points
	if (mouseData.length > 100) mouseData.shift();

	if (lastMousePos) {
		const directionChanges = countRecentDirectionChanges();
		const avgVelocity = getRecentAverageVelocity();
		//console.log(`velocity: ${avgVelocity.toFixed(3)}, dirChanges: ${directionChanges}`); // ← add this
		if (currentTreatment === 1 && isFrustrated(avgVelocity, directionChanges)) {
			onFrustrationDetected('erratic_movement');
		}
	}

	// Reset hesitation timer on every move
	clearTimeout(hesitationTimer);
	hesitationTimer = setTimeout(() => {
		if (currentTreatment === 1 && !gameOver) onFrustrationDetected('hesitation');
	}, FRUSTRATION_CONFIG.hesitationThreshold);

	lastMousePos = { x, y };
	lastMouseTime = now;
});

function countRecentDirectionChanges() {
	const recent = mouseData.slice(-FRUSTRATION_CONFIG.directionChangeWindow);
	let changes = 0;
	if (recent.length < 3) return 0;
	for (let i = 2; i < recent.length; i++) {
		const prevDx = recent[i - 1].x - recent[i - 2].x;
		const currDx = recent[i].x - recent[i - 1].x;
		if (prevDx !== 0 && currDx !== 0 && (prevDx > 0) !== (currDx > 0)) changes++;

		const prevDy = recent[i - 1].y - recent[i - 2].y;
		const currDy = recent[i].y - recent[i - 1].y;
		if (prevDy !== 0 && currDy !== 0 && (prevDy > 0) !== (currDy > 0)) changes++;
	}
	return changes;
}

function getRecentAverageVelocity() {
	const recent = mouseData.slice(-FRUSTRATION_CONFIG.directionChangeWindow);
	if (recent.length < 2) return 0;
	let distance = 0;
	for (let i = 1; i < recent.length; i++) {
		const dx = recent[i].x - recent[i - 1].x;
		const dy = recent[i].y - recent[i - 1].y;
		distance += Math.sqrt(dx * dx + dy * dy);
	}
	const dt = recent[recent.length - 1].timestamp - recent[0].timestamp;
	return dt > 0 ? distance / dt : 0;
}

function isFrustrated(velocity, directionChanges) {
	return (
		velocity > FRUSTRATION_CONFIG.velocityThreshold &&
		directionChanges >= FRUSTRATION_CONFIG.directionChangeThreshold
	);
}

function onFrustrationDetected(reason) {
	const now = Date.now();

	// Cooldown — don't spam the chatbot
	if (now - lastFrustrationTrigger < FRUSTRATION_CONFIG.cooldown) return;

	// Don't trigger if game is over or it's not the human's turn
	if (gameOver || currentPlayer !== 'X') return;

	lastFrustrationTrigger = now;
	console.log(`Frustration detected: ${reason}`);

	// Log it for research
	mouseData.push({ event: 'frustration', reason, timestamp: now });

	// Trigger the chatbot hint
	triggerSuggestion();
}

// Experiment State
let roundCount = 1;
let currentTreatment = window.startTreatment !== undefined ? window.startTreatment : 0; // 0 = 10 sec interval, 1 = Frustration
console.log("Current Treatment: " + currentTreatment);
let intervalTimer = null;
let emptyClickCount = 0; // For tracking frustration

const winConditions = [
	[0, 1, 2], [3, 4, 5], [6, 7, 8],
	[0, 3, 6], [1, 4, 7], [2, 5, 8],
	[0, 4, 8], [2, 4, 6]
];

function checkWin() {
	for (const [a, b, c] of winConditions) {
		if (
			boxes[a].textContent &&
			boxes[a].textContent === boxes[b].textContent &&
			boxes[a].textContent === boxes[c].textContent
		) {
			return boxes[a].textContent;
		}
	}
	if (Array.from(boxes).every((box) => box.textContent !== "")) {
		return "draw";
	}
	return null;
}

function handleTurnEnd() {
	let result = checkWin();
	if (result === "draw") {
		document.querySelector(".winner-indicator").textContent = "It's a draw!";
		document.querySelector("#nextRoundBtn").style.display = "inline-block";
		gameOver = true;
		return true;
	}
	if (result) {
		document.querySelector(".winner-indicator").textContent = `${result} wins!`;
		document.querySelector("#nextRoundBtn").style.display = "inline-block";
		gameOver = true;
		return true;
	}
	return false;
}

// Start Human Turn Logic
function startHumanTurn() {
    currentPlayer = "X";
    document.querySelector("#round-indicator").textContent = `Round ${roundCount} / 6`;
    document.querySelector("#nextRoundBtn").style.display = "none";
    emptyClickCount = 0;
    mouseData.length = 0;

    // Treatment 0: only start interval if not already running
    if (currentTreatment === 0 && !intervalTimer) {
        intervalTimer = setInterval(() => {
            if (!gameOver && currentPlayer === "X") {
                console.log("5 Second Interval Triggered");
                triggerSuggestion();
            }
        }, 5000);
    }
}

boxes.forEach((box) => {
	box.addEventListener("click", () => {
		if (gameOver) return;

		// Frustration Tracking (Treatment 1)
		if (box.textContent !== "") {
			if (currentTreatment === 1) {
				emptyClickCount++;
				if (emptyClickCount >= 3) {
					// Rage click detected! Provide suggestion.
					triggerSuggestion();
					emptyClickCount = 0; // reset
				}
			}
			return; // Cannot play here
		}

		// Valid Move
		//clearInterval(intervalTimer); // Cancel suggestions since human moved
		box.textContent = "X"; // Human is always X

		if (handleTurnEnd()) return;
		currentPlayer = "O";
		fetchAI_Move();
	});
});

function resetGame() {
	clearInterval(intervalTimer);
    intervalTimer = null;  // ← allows startHumanTurn to restart it for the new round
	if (roundCount >= 6) {
		alert("Experiment Complete! Thank you.");
		return;
	}

	gameOver = false;
	boxes.forEach((box) => (box.textContent = ""));
	document.querySelector(".winner-indicator").textContent = '';

	// Advance Round
	roundCount++;
	if (roundCount === 4) {
		// Switch to Midpoint Screen
		document.getElementById("main-game-wrapper").style.display = "none";
		document.getElementById("midpoint-screen").style.display = "flex";
		return; // Halt round start until Next is clicked
	}

	document.querySelector(".chat-messages").innerHTML = ""; // Clear chat for new round
	startHumanTurn();
}

document.querySelector("#midpointNextBtn").addEventListener("click", () => {
	document.getElementById("midpoint-screen").style.display = "none";
	document.getElementById("main-game-wrapper").style.display = "flex";

	// Switch treatments
	currentTreatment = currentTreatment === 0 ? 1 : 0;

	document.querySelector(".chat-messages").innerHTML = "";
	startHumanTurn();
});

document.querySelector("#nextRoundBtn").addEventListener("click", resetGame);

async function fetchAI_Move() {
	const currentBoard = Array.from(boxes).map((b) => b.textContent === "" ? null : b.textContent);

	try {
		const response = await fetch("/api/move/", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ board: currentBoard, player: "O" })
		});

		const data = await response.json();

		if (data.move !== undefined) {
			boxes[data.move].textContent = "O";
			if (!handleTurnEnd()) {
				startHumanTurn(); // Back to human
			}
		}
	} catch (e) {
		console.error("AI move failed:", e);
		document.querySelector(".winner-indicator").textContent = "Error communicating with AI";
	}
}

// Chat message logic
document.getElementById("sendBtn").addEventListener("click", () => sendMessageFromInput());
document.getElementById("userInput").addEventListener("keypress", function (e) {
	if (e.key === "Enter") sendMessageFromInput();
});

function sendMessageFromInput() {
	const input = document.getElementById("userInput");
	const message = input.value.trim();
	if (message) {
		appendMessage("user", message);
		input.value = "";
		sendPayloadToChatbot(message, false);
	}
}

function triggerSuggestion() {
	// Only trigger if we aren't currently waiting on the bot
	const lastMessage = document.querySelector(".chat-messages").lastElementChild;
	if (lastMessage && lastMessage.textContent === "...") return;

	// Send empty message but flagged as suggestion
	sendPayloadToChatbot("", true);
}

async function sendPayloadToChatbot(messageText, isSuggestion) {
	appendMessage("bot", "...");

	const boardState = Array.from(boxes).map((box) => box.textContent);

	const messageElements = document.querySelectorAll(".message");
	const chatHistory = [];
	messageElements.forEach(msg => {
		if (msg.textContent !== "...") {
			const role = msg.classList.contains("user-message") ? "user" : "assistant";
			chatHistory.push({ role: role, content: msg.textContent });
		}
	});

	const payload = {
		message: messageText,
		board: boardState,
		history: chatHistory,
		is_suggestion: isSuggestion
	};

	console.log("Sending payload to /api/chat/:", payload);

	try {
		const response = await fetch("/api/chat/", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify(payload)
		});
		const data = await response.json();

		const messagesContainer = document.querySelector(".chat-messages");
		if (messagesContainer.lastChild && messagesContainer.lastChild.textContent === "...") {
			messagesContainer.removeChild(messagesContainer.lastChild);
		}

		if (data.response !== undefined) {
			appendMessage("bot", data.response || "(Empty response from AI)");
		} else if (data.error) {
			appendMessage("bot", "Error: " + JSON.stringify(data.error));
		} else {
			appendMessage("bot", "Error: " + JSON.stringify(data));
		}
	} catch (e) {
		const messagesContainer = document.querySelector(".chat-messages");
		if (messagesContainer.lastChild && messagesContainer.lastChild.textContent === "...") {
			messagesContainer.removeChild(messagesContainer.lastChild);
		}
		appendMessage("bot", "Network error occurred.");
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

// Initialize the first human turn
startHumanTurn();