const chat = document.getElementById("chat");
const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

const langItBtn = document.getElementById("lang-it");
const langEnBtn = document.getElementById("lang-en");

let conversationId = null;

// ✅ FastAPI conversation endpoint
const CHAT_API_URL = "http://127.0.0.1:8000/chat/";

let currentLang = "it";

// --- Texts ---
const TEXTS = {
  it: {
    greeting: "Ciao 👋 Dimmi che prodotto stai cercando.",
    placeholder: "Es. bicchieri da vino per ristorante",
    send: "Invia",
    error: "❌ Errore di connessione al server",
    noProducts: "Nessun prodotto trovato.",
    introProducts: "Ecco alcuni prodotti consigliati:"
  },
  en: {
    greeting: "Hello 👋 Tell me what product you are looking for.",
    placeholder: "e.g. wine glasses for restaurant",
    send: "Send",
    error: "❌ Error connecting to server",
    noProducts: "No products found.",
    introProducts: "Here are some suggested products:"
  }
};

// --- Init ---
function initChat() {
  chat.innerHTML = "";
  addMessage(TEXTS[currentLang].greeting, "bot");
  input.placeholder = TEXTS[currentLang].placeholder;
  sendBtn.innerText = TEXTS[currentLang].send;
}

initChat();

// --- Language switch ---
langItBtn.onclick = () => setLanguage("it");
langEnBtn.onclick = () => setLanguage("en");

function setLanguage(lang) {
  currentLang = lang;
  langItBtn.classList.toggle("active", lang === "it");
  langEnBtn.classList.toggle("active", lang === "en");
  initChat();
}

// --- Events ---
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

// --- UI helpers ---
function addMessage(text, sender = "bot") {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.innerText = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function addProducts(products) {
  products.forEach((p) => {
    const div = document.createElement("div");
    div.className = "message bot product";

    const category = p.metadata?.category || "Prodotto";
    const url = p.metadata?.url || "#";

    div.innerHTML = `
      • <strong>${category}</strong><br>
      <a href="${url}" target="_blank">Vedi prodotto</a>
    `;

    chat.appendChild(div);
  });

  chat.scrollTop = chat.scrollHeight;
}

// --- Send message ---
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  // show user message
  addMessage(text, "user");
  input.value = "";

  try {
    const res = await fetch(CHAT_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: text,          
        language: currentLang,
        top_k: 5
      })
    });


    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    // ✅ conversation id را ذخیره کن
    if (data.conversation_id) {
      conversationId = data.conversation_id;
    }

    // ✅ پیام متنی بات (سلام، سوال، توضیح…)
    if (data.message) {
      addMessage(data.message, "bot");
    }

    // ✅ اگر محصولی بود، نشان بده
    if (data.products && data.products.length > 0) {
      addProducts(data.products);
    }

    // ✅ سوال follow-up (در Version 3 خیلی مهم می‌شه)
    if (data.follow_up) {
      addMessage(data.follow_up, "bot");
    }

  } catch (err) {
    addMessage(TEXTS[currentLang].error, "bot");
    console.error(err);
  }
}
