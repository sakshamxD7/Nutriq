// Chat Assistant stream reader and renderer
document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const clearChatBtn = document.getElementById("clear-chat-btn");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (!chatForm) return; // Only execute on chat assistant page

    // Auto-scroll chat to bottom
    scrollToBottom();

    chatForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        
        const messageText = chatInput.value.trim();
        if (!messageText) return;

        // Clear input field
        chatInput.value = "";
        chatInput.disabled = true;

        // Render user message bubble
        appendMessageBubble(messageText, "user");
        scrollToBottom();

        // Render loading/bot response bubble
        const botBubble = appendMessageBubble("Thinking...", "bot");
        scrollToBottom();

        // Prepare POST request with Form Data
        const formData = new FormData();
        formData.append("message", messageText);

        try {
            const response = await fetch("/ai/chat/message", {
                method: "POST",
                headers: {
                    "X-CSRF-Token": csrfToken
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error("Failed to connect to assistant");
            }

            // Stream reader loop
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";
            let responseStarted = false;
            let fullBotText = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                
                // Process lines from stream buffer
                const lines = buffer.split("\n");
                // Save last partial line back to buffer
                buffer = lines.pop();

                for (const line of lines) {
                    const cleanLine = line.trim();
                    if (!cleanLine || !cleanLine.startsWith("data:")) continue;
                    
                    const dataPayload = cleanLine.substring(5).trim();
                    
                    if (dataPayload === "[DONE]") {
                        break;
                    }
                    
                    try {
                        const parsed = JSON.parse(dataPayload);
                        if (parsed.chunk) {
                            if (!responseStarted) {
                                botBubble.innerHTML = ""; // Clear "Thinking..."
                                responseStarted = true;
                            }
                            botBubble.innerHTML += parsed.chunk;
                            fullBotText += parsed.chunk;
                            scrollToBottom();
                        } else if (parsed.error) {
                            botBubble.innerHTML = `<span style="color: red;">${parsed.error}</span>`;
                        }
                    } catch (err) {
                        // Skip non-JSON payloads
                    }
                }
            }

            // Save history session after successful stream load
            if (responseStarted && fullBotText) {
                const historyData = new FormData();
                historyData.append("user", messageText);
                historyData.append("bot", fullBotText);
                fetch("/ai/chat/history/add", {
                    method: "POST",
                    headers: {
                        "X-CSRF-Token": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: historyData
                }).catch(err => console.error("Error updating history:", err));
            }
        } catch (error) {
            console.error("Chat streaming error:", error);
            botBubble.innerHTML = `<span style="color: red;">Unable to reach Nutriq Assistant. Please try again.</span>`;
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
        }
    });

    if (clearChatBtn) {
        clearChatBtn.addEventListener("click", function () {
            if (confirm("Are you sure you want to clear the conversation history?")) {
                fetch("/ai/chat/clear", {
                    method: "POST",
                    headers: {
                        "X-CSRF-Token": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        chatMessages.innerHTML = `
                            <div class="chat-bubble chat-bubble-bot">
                                Hi! I am your Nutriq Assistant. Ask me anything about Indian food calories, macros, or nutrition tips!
                            </div>
                        `;
                    }
                })
                .catch(err => console.error("Error clearing chat:", err));
            }
        });
    }

    function appendMessageBubble(text, sender) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble chat-bubble-${sender}`;
        bubble.innerText = text;
        chatMessages.appendChild(bubble);
        return bubble;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
