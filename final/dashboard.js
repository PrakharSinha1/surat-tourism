const email = localStorage.getItem("userEmail");

if (!email) {
    window.location.href = "login.html";
}

document.getElementById("userInfo").innerText = "Logged in as: " + email;


// 📄 PDF DOWNLOAD (UPGRADE)
function downloadPlanPDF(plan) {

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    let y = 10;

    doc.setFontSize(14);
    doc.text("Travel Itinerary", 10, y);

    y += 10;
    doc.text("Date: " + plan.dates, 10, y);

    y += 10;
    doc.text("Places:", 10, y);
    y += 6;
    plan.places.forEach(p => {
        doc.text("- " + p, 15, y);
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


// 🚀 LOAD PLANS
async function loadPlans() {

    const res = await fetch("http://127.0.0.1:5000/get-plans?email=" + email);
    const plans = await res.json();

    const container = document.getElementById("plans");

    if (plans.length === 0) {
        container.innerHTML = "<p>No plans yet</p>";
        return;
    }

    container.innerHTML = "";

    plans.forEach(p => {

        const card = document.createElement("div");
        card.className = "plan-card";

        card.innerHTML = `
            <h3>${p.dates}</h3>
            <p>📍 ${p.places.join(", ")}</p>
            <p>🍽️ ${p.food.join(", ")}</p>

            <button class="downloadBtn">⬇ Download PDF</button>
        `;

        // ✅ SAFE EVENT LISTENER (NO JSON STRING BUG)
        card.querySelector(".downloadBtn")
            .addEventListener("click", () => downloadPlanPDF(p));

        container.appendChild(card);
    });
}

loadPlans();