// CONFIGURATION
const API_OCR = "/api/extract-text";
const API_CHECK = "https://interlacustrine-candace-pleasedly.ngrok-free.dev/webhook/factcheck";
const API_NEWSLETTER = "https://interlacustrine-candace-pleasedly.ngrok-free.dev/webhook/subscribe";


// --- THEME TOGGLE ---
const themeToggle = document.getElementById('themeToggle');
const htmlEl = document.documentElement;
// iconEl is derived inside updateThemeIcon or we check it

function updateThemeIcon() {
    if (!themeToggle) return;
    const iconEl = themeToggle.querySelector('i');
    if (!iconEl) return;

    const theme = htmlEl.getAttribute('data-theme');
    if (theme === 'dark') {
        iconEl.classList.replace('ph-moon', 'ph-sun');
    } else {
        iconEl.classList.replace('ph-sun', 'ph-moon');
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = htmlEl.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        htmlEl.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon();
    });
}
// Init icon
updateThemeIcon();

// --- MOBILE MENU ---
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        const icon = mobileMenuBtn.querySelector('i');
        if (navLinks.classList.contains('active')) {
            icon.classList.replace('ph-list', 'ph-x');
        } else {
            icon.classList.replace('ph-x', 'ph-list');
        }
    });
}


// --- VOICE SEARCH ---
const voiceBtn = document.getElementById('voiceBtn');
const claimInput = document.getElementById('claimInput');
let recognition;

// 1. Voice Initialization
function initVoice() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            voiceBtn.classList.add('text-red-500'); // Tailwind color for active
            voiceBtn.style.color = 'red';
        };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            claimInput.value += transcript + " ";
            voiceBtn.classList.remove('text-red-500');
            voiceBtn.style.color = '';
        };
        recognition.onerror = (event) => {
            console.error("Voice Error:", event.error);
            voiceBtn.classList.remove('text-red-500');
            voiceBtn.style.color = '';
            alert("Voice Error: " + event.error);
        };
        recognition.onend = () => {
            voiceBtn.classList.remove('text-red-500');
            voiceBtn.style.color = '';
        };
        return true;
    }
    console.warn("Speech Recognition API not supported in this browser.");
    return false;
}

const hasVoice = initVoice();



if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
        if (!hasVoice) {
            alert("Voice typing is not supported in this browser.");
            return;
        }
        try { recognition.start(); } catch (e) { recognition.stop(); }
    });
}


// --- GLOBAL DRAG & DROP OVERLAY ---
const dragOverlay = document.getElementById('dragOverlay');
// const uploadClickTarget = document.getElementById('uploadClickTarget'); // Removed in new UI? No, kept in HTML maybe? Checks...
// If uploadClickTarget exists in HTML, keep it. If not, ignore.
// The new UI uses a label for file input, so we don't strictly need button click listeners, but existing one is fine.

const imageInput = document.getElementById('imageInput');

// 1. Global Drag Detection
let dragCounter = 0;

if (dragOverlay) {
    window.addEventListener('dragenter', (e) => {
        e.preventDefault();
        dragCounter++;
        dragOverlay.style.display = 'flex'; // Show overlay
    });

    window.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dragCounter--;
        if (dragCounter === 0) {
            dragOverlay.style.display = 'none'; // Hide overlay
        }
    });

    window.addEventListener('dragover', (e) => {
        e.preventDefault(); // Necessary to allow dropping
    });

    window.addEventListener('drop', (e) => {
        e.preventDefault();
        dragCounter = 0;
        dragOverlay.style.display = 'none';

        if (e.dataTransfer && e.dataTransfer.files.length > 0) {
            handleFiles(e.dataTransfer.files);
        }
    });
}

// 2. Click to Upload (Overlay & Button)
const uploadClickTarget = document.getElementById('uploadClickTarget');
if (uploadClickTarget) {
    uploadClickTarget.addEventListener('click', () => imageInput.click());
}

if (imageInput) {
    imageInput.addEventListener('change', () => {
        handleFiles(imageInput.files);
    });
}

// 3. File Handler
async function handleFiles(files) {
    if (files.length === 0) return;
    const file = files[0];

    // OCR Logic
    const loader = document.getElementById('loadingSection');
    const loadingText = document.getElementById('loadingText');
    const inputSection = document.getElementById('inputSection');

    if (inputSection) inputSection.style.display = 'none';
    if (loader) loader.style.display = 'block';
    if (loadingText) loadingText.innerText = "Extracting text from image...";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(API_OCR, { method: "POST", body: formData });
        const data = await response.json();

        if (loader) loader.style.display = 'none';
        if (inputSection) inputSection.style.display = 'block'; // Show Search Bar again

        if (data.text) {
            claimInput.value = data.text;
        } else {
            alert("Could not extract text. Please try a clearer image.");
        }
    } catch (e) {
        if (loader) loader.style.display = 'none';
        if (inputSection) inputSection.style.display = 'block';
        console.error("OCR Error", e);
        alert("Error uploading image.");
    }
}


// --- CAMERA LOGIC ---
const cameraBtn = document.getElementById('cameraBtn');
const cameraModal = document.getElementById('cameraModal');
const cameraVideo = document.getElementById('cameraVideo');
const cameraCanvas = document.getElementById('cameraCanvas');
const closeCameraBtn = document.getElementById('closeCameraBtn');
const captureBtn = document.getElementById('captureBtn');
let stream = null;

if (cameraBtn) {
    cameraBtn.addEventListener('click', async () => {
        cameraModal.style.display = 'flex';
        cameraModal.classList.remove('hidden');
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: "environment"
                }
            });
            cameraVideo.srcObject = stream;
        } catch (err) {
            console.error("Error accessing camera: ", err);
            alert("Could not access camera. Please allow permissions.");
            cameraModal.style.display = 'none';
            cameraModal.classList.add('hidden');
        }
    });
}

if (closeCameraBtn) {
    closeCameraBtn.addEventListener('click', () => {
        stopCamera();
        cameraModal.style.display = 'none';
        cameraModal.classList.add('hidden');
    });
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

if (captureBtn) {
    captureBtn.addEventListener('click', () => {
        const context = cameraCanvas.getContext('2d');
        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);

        // Convert to blob and send to handleFiles
        cameraCanvas.toBlob(blob => {
            const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
            handleFiles([file]);

            stopCamera();
            cameraModal.style.display = 'none';
            cameraModal.classList.add('hidden');
        }, 'image/jpeg');
    });
}


// --- HELPER FORMATTERS ---
function formatText(text) {
    if (!text) return "No analysis provided.";
    if (text.includes("JUSTIFICATION:")) text = text.split("JUSTIFICATION:")[1];
    if (text.includes("PRIMARY SOURCE:")) text = text.split("PRIMARY SOURCE:")[0];
    return text.replace(/(VERDICT:|REPORT DATA:)/gi, '').replace(/\s?[\-\*]\s/g, '<br>• ').trim();
}

function renderSources(data) {
    let list = [];
    if (data.source && typeof data.source === 'string') list = data.source.split(',').map(s => s.trim());
    else if (data.sources && Array.isArray(data.sources)) list = data.sources;
    else if (data.source) list = [String(data.source)];

    // Filter valid links
    list = list.filter(url => url && url.length > 10 && url.startsWith("http"));

    if (list.length > 0) {
        return list.map(url => {
            try {
                let domain = new URL(url).hostname.replace('www.', '');
                let favicon = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
                return `<a href="${url}" target="_blank" class="source-pill">
                    <img src="${favicon}" alt=""> ${domain} <i class="ph-bold ph-arrow-up-right"></i>
                </a>`;
            } catch (e) { return ""; }
        }).join("");
    }
    return `<span style="color:#94a3b8; font-style:italic;">No direct links found</span>`;
}


// --- VERIFY CLAIM (MAIN LOGIC) ---
async function verifyClaim() {
    const text = claimInput.value.trim();
    if (!text) {

        return;
    }

    const inputSection = document.getElementById('inputSection');
    const loader = document.getElementById('loadingSection');
    const resultSection = document.getElementById('resultSection');
    const resultTitle = document.getElementById('resultTitle'); // We might not need this ID anymore if we replace innerHTML
    const resultContent = document.getElementById('resultContent'); // Same here
    const loadingText = document.getElementById('loadingText');
    const userClaimText = document.getElementById('userClaimText');

    if (userClaimText) {
        userClaimText.innerText = `"${text}"`;
    }

    inputSection.style.display = 'none';
    resultSection.style.display = 'none';
    loader.style.display = 'block';

    // Dynamic Loading Text Steps
    const steps = ["Analyzing claim...", "Searching evidence...", "Checking logic...", "Verifying sources..."];
    let stepIdx = 0;
    loadingText.innerText = steps[0];

    const interval = setInterval(() => {
        stepIdx = (stepIdx + 1) % steps.length;
        if (stepIdx < steps.length) {
            loadingText.innerText = steps[stepIdx];
        }
    }, 1500);

    try {
        const response = await fetch(API_CHECK, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        clearInterval(interval);

        if (!response.ok) throw new Error("API Error");
        const data = await response.json();

        // RENDER RESULT
        const verdict = data.verdict || "INSUFFICIENT";
        const explanation = data.justification || "No details provided.";

        // Update Result Content
        const badge = document.getElementById('verdictBadge');
        const icon = document.getElementById('verdictIcon');
        const title = document.getElementById('resultTitle');
        const content = document.getElementById('resultContent');

        // Reset classes
        badge.className = "verdict-tag";

        let isTrue = false;
        let isFalse = false;

        if (verdict.toUpperCase().includes('TRUE')) {
            badge.classList.add('true');
            badge.innerText = "VERIFIED REAL";
            icon.className = "ph-duotone ph-check-circle";
            icon.style.color = "var(--green)";
            isTrue = true;
        } else if (verdict.toUpperCase().includes('FALSE')) {
            badge.classList.add('false');
            badge.innerText = "FAKE NEWS / MISLEADING";
            icon.className = "ph-duotone ph-warning-circle";
            isFalse = true;
        } else {
            badge.classList.add('unverified');
            badge.innerText = "INSUFFICIENT EVIDENCE";
            icon.className = "ph-duotone ph-question";
        }

        content.innerHTML = `
            <div class="result-header" style="border:none; padding:0; margin:0;"></div> <!-- Spacer -->
            
            <div class="meta-grid">
                <div><div class="meta-label">Date</div><div class="meta-value">${data.news_date || "Unknown"}</div></div>
                <div><div class="meta-label">Speaker</div><div class="meta-value">${data.speaker || "Unknown"}</div></div>
                <div><div class="meta-label">Platform</div><div class="meta-value">${data.platform || "Unknown"}</div></div>
                <div><div class="meta-label">Context</div><div class="meta-value">${data.subject || "General"}</div></div>
            </div>

            <div class="summary">
                <div class="meta-label">AI Analysis</div>
                <p style="color: var(--text-color);">${formatText(explanation)}</p>
            </div>

            <div class="sources-container">
                    <div class="meta-label" style="margin-bottom:12px;">Evidence Sources</div>
                    <div>${renderSources(data)}</div>
            </div>
        `;

        loader.style.display = 'none';
        resultSection.style.display = 'block';

        // Play Result Video
        const resultPenguinContainer = document.getElementById('resultPenguinContainer');
        if (resultPenguinContainer) {
            resultPenguinContainer.innerHTML = ''; // Clear previous
            let videoSrc = "";
            if (isTrue) videoSrc = "assets/penguine_true.webm";
            else if (isFalse) videoSrc = "assets/penguine_false.webm";

            if (videoSrc) {
                const videoEl = document.createElement('video');
                videoEl.src = videoSrc;
                videoEl.autoplay = true;
                videoEl.loop = true;
                videoEl.muted = true;
                videoEl.playsInline = true;
                videoEl.className = "result-penguin-video";
                resultPenguinContainer.appendChild(videoEl);
            }
        }



    } catch (e) {
        clearInterval(interval);
        loader.style.display = 'none';
        inputSection.style.display = 'block';
        console.error(e);
        alert("Error connecting to FactCheck Agent. Please try again.");
    }
}


// Removed displayResult as it is now inlined in verifyClaim

// --- NEWSLETTER ---
async function subscribeNewsletter() {
    const email = document.getElementById("emailInput").value;
    const msg = document.getElementById("newsletterMsg");
    if (!email.includes("@")) { msg.innerHTML = "<span style='color:red'>Invalid email</span>"; return; }

    msg.innerText = "Subscribing...";
    try {
        const response = await fetch(API_NEWSLETTER, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });

        if (!response.ok) throw new Error("Server Error");

        msg.innerHTML = "<span style='color:var(--text-color)'>Subscribed successfully!</span>";
        document.getElementById("emailInput").value = "";
    } catch (e) {
        console.error(e);
        msg.innerHTML = "<span style='color:red'>Connection Failed.</span>";
    }
}