const API = "http://127.0.0.1:5000";


// ✅ WAIT FOR DOM
document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("submitBtn");

    if (btn) {
        btn.addEventListener("click", submitItinerary);
    }

    const email = localStorage.getItem("userEmail");

    if (email) {
        document.getElementById("email").value = email;
        loadPlans(email);
    }
});


// 🚀 SUBMIT ITINERARY
async function submitItinerary() {

    console.log("Button clicked ✅");

    const email = document.getElementById("email").value.trim();
    const date = document.getElementById("date").value;

    const places = document.getElementById("places").value
        ? document.getElementById("places").value.split(",").map(i => i.trim()).filter(i => i)
        : [];

    const events = document.getElementById("events").value
        ? document.getElementById("events").value.split(",").map(i => i.trim()).filter(i => i)
        : [];

    const food = document.getElementById("food").value
        ? document.getElementById("food").value.split(",").map(i => i.trim()).filter(i => i)
        : [];

    // ⚠️ VALIDATION
    if (!email || !date) {
        alert("⚠️ Enter email and date");
        return;
    }

    try {
        const res = await fetch(API + "/plan-trip", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                dates: date,
                places,
                events,
                food
            })
        });

        if (!res.ok) {
            alert("❌ Server error");
            return;
        }

        const result = await res.json();

        // 💾 SAVE EMAIL
        localStorage.setItem("userEmail", email);

        // 🔥 SHOW PREVIEW
        showPreview(result.preview);

        // 🔄 LOAD ALL PLANS
        loadPlans(email);

    } catch (err) {
        console.error(err);
        alert("❌ Backend not connected");
    }
}


// 🌍 SHOW PREVIEW WITH PDF BUTTON
function showPreview(data) {

    const preview = document.getElementById("preview");

    preview.innerHTML = `
        <div class="preview-card">
            <h3>🌍 Your Plan Preview</h3>

            <p><b>📅 Date:</b> ${data.dates}</p>
            <p><b>📍 Places:</b> ${data.places.join(", ") || "None"}</p>
            <p><b>🎉 Events:</b> ${data.events.join(", ") || "None"}</p>
            <p><b>🍽 Food:</b> ${data.food.join(", ") || "None"}</p>

            <button id="downloadPdfBtn">
                📄 Download PDF
            </button>
        </div>
    `;

    // 🔥 Attach event (important)
    document.getElementById("downloadPdfBtn")
        .addEventListener("click", () => downloadPlanPDF(data));
}


// 📥 LOAD USER PLANS
async function loadPlans(email) {

    const container = document.getElementById("plansContainer");
    if (!container) return;

    const res = await fetch(`${API}/get-plans?email=${email}`);
    const data = await res.json();

    container.innerHTML = "";

    if (data.length === 0) {
        container.innerHTML = "<p>No plans yet</p>";
        return;
    }

    data.forEach(plan => {

        const card = document.createElement("div");
        card.className = "plan-card";

        card.innerHTML = `
            <h3>📅 ${plan.dates}</h3>
            <p><b>📍 Places:</b> ${plan.places.join(", ")}</p>
            <p><b>🎉 Events:</b> ${plan.events.join(", ")}</p>
            <p><b>🍽 Food:</b> ${plan.food.join(", ")}</p>

            <button class="pdfBtn">📄 PDF</button>
        `;

        // 🔥 attach event properly
        card.querySelector(".pdfBtn")
            .addEventListener("click", () => downloadPlanPDF(plan));

        container.appendChild(card);
    });
}


// 📄 PDF DOWNLOAD FUNCTION
function downloadPlanPDF(plan) {

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    let y = 10;

    doc.setFontSize(16);
    doc.text("Travel Itinerary", 10, y);

    y += 10;
    doc.setFontSize(12);
    doc.text(`Date: ${plan.dates}`, 10, y);

    y += 10;
    doc.text("Places:", 10, y);
    y += 6;
    plan.places.forEach(p => {
        doc.text("- " + p, 15, y);
        y += 6;
    });

    y += 4;
    doc.text("Events:", 10, y);
    y += 6;
    plan.events.forEach(e => {
        doc.text("- " + e, 15, y);
        y += 6;
    });

    y += 4;
    doc.text("Food:", 10, y);
    y += 6;
    plan.food.forEach(f => {
        doc.text("- " + f, 15, y);
        y += 6;
    });

    doc.save("itinerary.pdf");
}