document.addEventListener("DOMContentLoaded", () => {

  // 🔝 BACK TO TOP BUTTON
  const backToTop = document.getElementById("backToTop");

  window.addEventListener("scroll", () => {
    if (backToTop) {
      backToTop.style.display = window.scrollY > 300 ? "block" : "none";
    }
  });

  // 🔐 NAVBAR LOGIN STATE
  const loginBtn = document.getElementById("loginBtn");
  const email = localStorage.getItem("userEmail");

  if (loginBtn && email) {
    loginBtn.innerText = "Logout";
    loginBtn.href = "#";

    loginBtn.onclick = () => {
      localStorage.removeItem("userEmail");
      location.reload();
    };
  }

});


// 🚀 SUBMIT ITINERARY
async function submitItinerary() {

  const email = localStorage.getItem("userEmail");
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
  if (!email) {
    alert("Please login first 🔐");
    window.location.href = "login.html";
    return;
  }

  if (!date) {
    alert("Select a date 📅");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/plan-trip", {
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
      const err = await res.text();
      console.error(err);
      alert("Server error ❌");
      return;
    }

    const result = await res.json();

    if (!result.preview) {
      alert("No preview returned ⚠️");
      return;
    }

    showPreview(result.preview);

  } catch (err) {
    console.error(err);
    alert("Backend not connected ❌");
  }
}


// 📋 SHOW PREVIEW + DOWNLOAD BUTTON
function showPreview(data) {

  const preview = document.getElementById("preview");
  if (!preview) return;

  preview.innerHTML = `
    <h3>🌍 Your Plan</h3>
    <p><b>Date:</b> ${data.dates || "-"}</p>
    <p><b>Places:</b> ${data.places?.join(", ") || "None"}</p>
    <p><b>Events:</b> ${data.events?.join(", ") || "None"}</p>
    <p><b>Food:</b> ${data.food?.join(", ") || "None"}</p>

    <button onclick="downloadItinerary()" 
      style="margin-top:15px; padding:10px 15px; cursor:pointer;">
      ⬇️ Download Plan
    </button>
  `;

  // 🔥 store current plan globally
  window.currentPlan = data;
}


// 📥 DOWNLOAD FUNCTION
function downloadItinerary() {

  const data = window.currentPlan;

  if (!data) {
    alert("No plan to download ❌");
    return;
  }

  const content = `
🌍 Travel Itinerary

📅 Date: ${data.dates}

📍 Places:
${data.places.join("\n")}

🎉 Events:
${data.events.join("\n")}

🍽️ Food:
${data.food.join("\n")}
`;

  const blob = new Blob([content], { type: "text/plain" });

  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "itinerary.txt";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}