// Search Food Function
async function searchFood(){
    const foodName = document.getElementById("foodInput").value.trim();
    const loader = document.getElementById("loader");
    const result = document.getElementById("result");
    const errorMsg = document.getElementById("errorMsg");
    const resultsList = document.getElementById("resultsList");

    if (!foodName) {
        errorMsg.classList.remove("hidden");
        errorMsg.textContent = "⚠️ Please enter a food name to search!";
        result.classList.add("hidden");
        resultsList.classList.add("hidden");
        return;
    }

    loader.classList.remove("hidden");
    result.classList.add("hidden");
    errorMsg.classList.add("hidden");
    resultsList.classList.add("hidden");

    try {
        const response = await fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ food: foodName })
        });

        const data = await response.json();

        loader.classList.add("hidden");

        if (response.status === 404) {
            errorMsg.classList.remove("hidden");
            errorMsg.textContent = `❌ "${foodName}" not found! Try searching for other foods.`;
            result.classList.add("hidden");
        } else if (response.ok) {
            displayResult(data);
            result.classList.remove("hidden");
            errorMsg.classList.add("hidden");
        } else {
            errorMsg.classList.remove("hidden");
            errorMsg.textContent = data.error || "⚠️ Error occurred. Please try again.";
        }
    } catch (error) {
        loader.classList.add("hidden");
        errorMsg.classList.remove("hidden");
        errorMsg.textContent = "❌ Network error! Please check your connection.";
        console.error("Error:", error);
    }
}

// Display Result with comprehensive nutrition info
function displayResult(food) {
    const resultContent = document.querySelector(".result-content");

    const nutritionHTML = `
        <h2>🥗 ${food.name}</h2>

        <span class="category-badge">📂 ${food.category}</span>

        <div class="nutrition-grid">
            <div class="nutrition-item">
                <div class="label">Energy</div>
                <div class="value">${food.energy}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Calories</div>
                <div class="value">${food.calories}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Protein</div>
                <div class="value">${food.protein}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Carbs</div>
                <div class="value">${food.carbs}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Sugar</div>
                <div class="value">${food.sugars}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Fat</div>
                <div class="value">${food.fat}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Fiber</div>
                <div class="value">${food.fiber}</div>
            </div>
            <div class="nutrition-item">
                <div class="label">Water</div>
                <div class="value">${food.water}</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">💪 Key Benefits</div>
            <div class="section-content">${food.benefits}</div>
        </div>

        <div class="section">
            <div class="section-title">🍳 How to Use</div>
            <div class="section-content">${food.uses}</div>
        </div>

        <div class="section">
            <div class="section-title">⏰ When to Eat</div>
            <div class="section-content">${food.when_to_eat}</div>
        </div>

        <div class="section">
            <div class="section-title">🧪 Vitamins & Minerals</div>
            <div class="section-content">
                <strong>Vitamins:</strong> ${food.vitamins}<br><br>
                <strong>Minerals:</strong> ${food.minerals}
            </div>
        </div>
    `;

    resultContent.innerHTML = nutritionHTML;
}

// Search by Category
async function searchByCategory(category) {
    document.getElementById("foodInput").value = "";
    const loader = document.getElementById("loader");
    const result = document.getElementById("result");
    const resultsList = document.getElementById("resultsList");
    const errorMsg = document.getElementById("errorMsg");

    loader.classList.remove("hidden");
    result.classList.add("hidden");
    errorMsg.classList.add("hidden");
    resultsList.classList.add("hidden");

    try {
        // Fetch all foods and filter by category
        const response = await fetch("/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ food: "" })
        });

        loader.classList.add("hidden");

        // For now, show a message (implementation would require a category endpoint)
        errorMsg.classList.remove("hidden");
        errorMsg.textContent = `📚 Browsing ${category}s - Use search to find specific items!`;
    } catch (error) {
        loader.classList.add("hidden");
        errorMsg.classList.remove("hidden");
        errorMsg.textContent = "❌ Error loading category. Please try again.";
    }
}

// Enter key support for search
function initializeSearch() {
    const foodInput = document.getElementById("foodInput");
    if (foodInput) {
        foodInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                searchFood();
            }
        });
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeSearch);
} else {
    initializeSearch();
}

/* Voice Search Recognition */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    const voiceBtn = document.getElementById("voiceBtn");

    if (voiceBtn) {
        voiceBtn.addEventListener("click", () => {
            recognition.start();
            voiceBtn.classList.add("listening");
        });

        recognition.onstart = () => {
            voiceBtn.classList.add("listening");
        };

        recognition.onend = () => {
            voiceBtn.classList.remove("listening");
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById("foodInput").value = transcript;
            searchFood();
        };

        recognition.onerror = (event) => {
            console.log("Voice recognition error:", event.error);
            voiceBtn.classList.remove("listening");
        };
    }
} else {
    console.log("Speech Recognition not supported");
}
