const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');
const recognized = document.getElementById('recognized');
const feedback = document.getElementById('feedback');
const listEl = document.getElementById('list');
const suggEl = document.getElementById('suggestions');

let recognition, listening=false;

function supportsSpeech(){
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

async function fetchList(){
    const res = await fetch('/api/list');
    const items = await res.json();
    listEl.innerHTML = '';
    items.forEach(it => {
        const li = document.createElement('li');
        li.className='item';
        li.innerHTML = `<span>${it.item}<span class="qty">×${it.quantity}</span></span><span>${it.category}</span>`;
        listEl.appendChild(li);
    });
}

async function fetchSuggestions(){
    const res = await fetch('/api/suggestions');
    const items = await res.json();
    suggEl.innerHTML = '';
    items.forEach(s => {
        const li = document.createElement('li');
        li.className = 'item';
        li.innerHTML = `<span>${s.item}</span><small style="opacity:.8">${s.reason}</small>`;
        suggEl.appendChild(li);
    });
}

async function sendCommand(command){
    feedback.innerText = 'Processing...';
    const res = await fetch('/api/voice', {
        method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({command})
    });
    const data = await res.json();
    recognized.innerText = 'Heard: ' + command;
    feedback.innerText = data.message || JSON.stringify(data);
    await fetchList();
}

startBtn.addEventListener('click', ()=>{
    if(!supportsSpeech()){ status.innerText = 'Speech recognition not supported in this browser.'; return; }
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        listening = true;
        status.innerText = 'Listening...';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    };
    recognition.onresult = (ev) => {
        const text = ev.results[0][0].transcript;
        sendCommand(text);
    };
    recognition.onerror = (ev) => {
        status.innerText = 'Error: ' + ev.error;
    };
    recognition.onend = () => {
        listening = false;
        status.innerText = 'Idle';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    };
    recognition.start();
});

stopBtn.addEventListener('click', ()=>{
    if(recognition && listening) recognition.stop();
});

// init
fetchList();
fetchSuggestions();
