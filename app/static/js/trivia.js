// Trivia Game Controller
document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".trivia-choice-card");
    const nextBtn = document.getElementById("next-trivia-btn");
    const streakVal = document.getElementById("streak-value");
    const bestStreakVal = document.getElementById("best-streak-value");
    const funFactContainer = document.getElementById("trivia-fact-container");
    const funFactText = document.getElementById("trivia-fact-text");
    const shareContainer = document.getElementById("share-streak-container");
    const shareText = document.getElementById("share-streak-text");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (cards.length === 0) return; // Only execute on trivia pages

    let canPlay = true;

    cards.forEach(card => {
        card.addEventListener("click", function () {
            if (!canPlay) return;
            
            const selectedId = this.dataset.id;
            
            canPlay = false;
            
            // Post selection to answer checker
            fetch("/trivia/answer", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({ selected_id: selectedId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    canPlay = true;
                    return;
                }

                // Show visual feedback classes on cards
                cards.forEach(c => {
                    const id = parseInt(c.dataset.id);
                    const calBadge = c.querySelector(".calorie-reveal-badge");
                    
                    if (id === data.correct_id) {
                        c.classList.add("correct-ans");
                    } else {
                        // Mark wrong card if user selected it
                        if (id === parseInt(selectedId)) {
                            c.classList.add("incorrect-ans");
                        }
                    }

                    // Reveal actual calories
                    if (calBadge) {
                        const calVal = (id === data.correct_id) ? 
                            (id === parseInt(selectedId) ? Math.min(data.calories_item1, data.calories_item2) : Math.min(data.calories_item1, data.calories_item2)) : 
                            (id === parseInt(selectedId) ? Math.max(data.calories_item1, data.calories_item2) : Math.max(data.calories_item1, data.calories_item2));
                        
                        // We map them accurately
                        if (c.id === "item-card-1") {
                            calBadge.innerText = `${parseInt(data.calories_item1)} kcal/100g`;
                        } else {
                            calBadge.innerText = `${parseInt(data.calories_item2)} kcal/100g`;
                        }
                        calBadge.style.display = "block";
                    }
                });

                // Update streaks UI
                streakVal.innerText = data.streak;
                bestStreakVal.innerText = data.best_streak;

                // Show fun fact details
                funFactText.innerText = data.fun_fact;
                funFactContainer.style.display = "block";

                // Setup share text if streak is > 2
                if (data.streak >= 3) {
                    const text = `I got ${data.streak} in a row on Nutriq Trivia! 🥗 How well do you know your calories? Track with Nutriq!`;
                    shareText.innerText = text;
                    shareContainer.style.display = "block";
                }

                // Show Next Question button
                nextBtn.style.display = "inline-block";
            })
            .catch(err => {
                console.error("Trivia answer submission error:", err);
                canPlay = true;
            });
        });
    });

    nextBtn.addEventListener("click", function () {
        // Fetch next surprising pairing
        fetch("/trivia/next", {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Reset game states
            canPlay = true;
            nextBtn.style.display = "none";
            funFactContainer.style.display = "none";
            shareContainer.style.display = "none";

            // Update card elements
            const card1 = document.getElementById("item-card-1");
            const card2 = document.getElementById("item-card-2");

            card1.dataset.id = data.item1.id;
            card1.querySelector("h3").innerText = data.item1.name;
            card1.querySelector("p").innerText = data.item1.name_hindi || "";
            card1.classList.remove("correct-ans", "incorrect-ans");
            card1.querySelector(".calorie-reveal-badge").style.display = "none";

            card2.dataset.id = data.item2.id;
            card2.querySelector("h3").innerText = data.item2.name;
            card2.querySelector("p").innerText = data.item2.name_hindi || "";
            card2.classList.remove("correct-ans", "incorrect-ans");
            card2.querySelector(".calorie-reveal-badge").style.display = "none";
        })
        .catch(err => console.error("Error loading next question:", err));
    });
});
