// ============================================================
//  API CONFIG — change this ONE file when you deploy
//  Local dev:   const API = "http://127.0.0.1:5000"
//  Production:  const API = "https://your-api.onrender.com"
// ============================================================
const API = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:5000"
  : "https://your-api.onrender.com";   // ← REPLACE with your Render URL after deploying