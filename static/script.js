const input = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const messages = document.getElementById("messages");

function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = `${type} msg`;
    div.textContent = (type === "bot" ? "🤖 " : "👤 ") + text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: text})
        });
        const data = await response.json();
        addMessage(data.answer, "bot");
        speak(data.answer);
    } catch (error) {
        addMessage("Server connection error. Please try again.", "bot");
    }
}

function ask(text) {
    input.value = text;
    sendMessage();
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
});

// Browser voice input
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;

    micBtn.addEventListener("click", () => {
        recognition.start();
        micBtn.textContent = "🔴";
    });

    recognition.onresult = event => {
        input.value = event.results[0][0].transcript;
        micBtn.textContent = "🎤";
        sendMessage();
    };

    recognition.onerror = () => micBtn.textContent = "🎤";
    recognition.onend = () => micBtn.textContent = "🎤";
} else {
    micBtn.addEventListener("click", () => {
        alert("Voice input is not supported in this browser. Try Chrome.");
    });
}

// Optional text-to-speech
function speak(text) {
    if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-IN";
        speechSynthesis.cancel();
        speechSynthesis.speak(utterance);
    }
}
