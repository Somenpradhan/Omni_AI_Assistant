// State Variables
let currentSettings = null;
const apiModels = {
    gemini: [
        { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash (Recommended)' },
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
        { value: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash' }
    ],
    openai: [
        { value: 'gpt-4o-mini', label: 'GPT-4o-mini (Recommended)' },
        { value: 'gpt-4o', label: 'GPT-4o' }
    ],
    aether: [
        { value: 'aether-orchestrator', label: 'Aether Orchestrator (Local Agent)' }
    ]
};

// UI Elements
const mainPanel = document.getElementById('mainPanel');
const settingsPanel = document.getElementById('settingsPanel');

const originalPrompt = document.getElementById('originalPrompt');
const optimizedPrompt = document.getElementById('optimizedPrompt');
const optimMode = document.getElementById('optimMode');
const optimizeBtn = document.getElementById('optimizeBtn');
const copyBtn = document.getElementById('copyBtn');
const pasteBackBtn = document.getElementById('pasteBackBtn');
const loader = document.getElementById('loader');

const settingsBtn = document.getElementById('settingsBtn');
const closeBtn = document.getElementById('closeBtn');
const settingsCloseBtn = document.getElementById('settingsCloseBtn');

const providerSelect = document.getElementById('providerSelect');
const apiKeyWrapper = document.getElementById('apiKeyWrapper');
const apiKeyInput = document.getElementById('apiKeyInput');
const toggleApiKey = document.getElementById('toggleApiKey');
const modelSelect = document.getElementById('modelSelect');
const shortcutInput = document.getElementById('shortcutInput');
const systemPromptInput = document.getElementById('systemPromptInput');
const autoPasteCheckbox = document.getElementById('autoPasteCheckbox');

const settingsSaveBtn = document.getElementById('settingsSaveBtn');
const settingsCancelBtn = document.getElementById('settingsCancelBtn');

// Initialize Electron IPC callback
window.prompsyAPI.onInitData((data) => {
    currentSettings = data.settings;
    originalPrompt.value = data.initialText || originalPrompt.value || '';
    
    // Fill settings inputs
    providerSelect.value = currentSettings.providerSelect || currentSettings.apiProvider;
    apiKeyInput.value = currentSettings.apiKey;
    shortcutInput.value = currentSettings.globalShortcut;
    systemPromptInput.value = currentSettings.systemPrompt;
    autoPasteCheckbox.checked = currentSettings.autoPaste;
    
    handleProviderChange(false);
    modelSelect.value = currentSettings.apiModel;

    if (data.showSettingsOnly) {
        showPanel(settingsPanel);
    } else {
        showPanel(mainPanel);
        
        // Auto-optimize if text was captured
        if (data.initialText && data.initialText.trim().length > 0) {
            triggerOptimization();
        }
    }
});

// Panel management
function showPanel(panel) {
    mainPanel.classList.remove('active');
    settingsPanel.classList.remove('active');
    
    panel.style.display = 'flex';
    setTimeout(() => {
        panel.classList.add('active');
    }, 10);
}

// Handle provider dropdown changes
function handleProviderChange(resetModel = true) {
    const provider = providerSelect.value;
    
    // Hide/Show API key for local agent
    if (provider === 'aether') {
        apiKeyWrapper.style.display = 'none';
    } else {
        apiKeyWrapper.style.display = 'flex';
    }
    
    // Update models dropdown
    modelSelect.innerHTML = '';
    const models = apiModels[provider] || [];
    models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.value;
        opt.textContent = m.label;
        modelSelect.appendChild(opt);
    });
    
    if (resetModel && models.length > 0) {
        modelSelect.value = models[0].value;
    }
}

providerSelect.addEventListener('change', () => handleProviderChange(true));

// Show/Hide API Key toggler
toggleApiKey.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        toggleApiKey.textContent = '🙈';
    } else {
        apiKeyInput.type = 'password';
        toggleApiKey.textContent = '👁️';
    }
});

// Settings buttons
settingsBtn.addEventListener('click', () => {
    showPanel(settingsPanel);
});

closeBtn.addEventListener('click', () => {
    window.prompsyAPI.closeWindow();
});

settingsCloseBtn.addEventListener('click', () => {
    showPanel(mainPanel);
});

settingsCancelBtn.addEventListener('click', () => {
    showPanel(mainPanel);
});

settingsSaveBtn.addEventListener('click', async () => {
    const updatedSettings = {
        apiKey: apiKeyInput.value.trim(),
        apiProvider: providerSelect.value,
        apiModel: modelSelect.value,
        globalShortcut: shortcutInput.value.trim(),
        systemPrompt: systemPromptInput.value.trim(),
        autoPaste: autoPasteCheckbox.checked
    };
    
    if (updatedSettings.apiProvider !== 'aether' && !updatedSettings.apiKey) {
        alert('Please enter a valid API Key for the selected provider.');
        return;
    }
    
    await window.prompsyAPI.saveSettings(updatedSettings);
    currentSettings = updatedSettings;
    showPanel(mainPanel);
});

// Copy & Paste buttons
copyBtn.addEventListener('click', async () => {
    const text = optimizedPrompt.value;
    if (text) {
        await window.prompsyAPI.writeClipboard(text);
        window.prompsyAPI.closeWindow();
    }
});

pasteBackBtn.addEventListener('click', async () => {
    const text = optimizedPrompt.value;
    if (text) {
        await window.prompsyAPI.pasteBack(text);
    }
});

// Trigger Enhancement click
optimizeBtn.addEventListener('click', () => {
    triggerOptimization();
});

// Key bindings (Ctrl+Enter to paste back, Esc to close)
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        window.prompsyAPI.closeWindow();
    } else if (e.key === 'Enter' && e.ctrlKey) {
        const text = optimizedPrompt.value;
        if (text) {
            window.prompsyAPI.pasteBack(text);
        }
    }
});

// Main Optimization Logic
async function triggerOptimization() {
    const rawText = originalPrompt.value.trim();
    if (!rawText) return;
    
    if (!currentSettings) {
        // Fetch settings if not loaded
        currentSettings = await window.prompsyAPI.getSettings();
    }
    
    if (currentSettings.apiProvider !== 'aether' && !currentSettings.apiKey) {
        optimizedPrompt.value = "⚠️ Error: API Key is missing. Please click the Gear icon ⚙️ in the top right to configure your API key.";
        return;
    }
    
    optimizedPrompt.value = '';
    loader.classList.add('active');
    optimizeBtn.disabled = true;
    
    // Choose mode override system instructions if applicable
    let targetPrompt = rawText;
    let modeInstruction = "";
    
    switch (optimMode.value) {
        case "structure":
            modeInstruction = " Enhance structural hierarchy, use bullets/numbered lists, and layout clear headings.";
            break;
        case "clarify":
            modeInstruction = " Eliminate vagueness, specify context, and clarify core objective instruction.";
            break;
        case "shorten":
            modeInstruction = " Make it highly concise and token efficient while keeping essential parameters.";
            break;
        default:
            modeInstruction = "";
    }
    
    const combinedSystemPrompt = currentSettings.systemPrompt + modeInstruction;
    
    try {
        if (currentSettings.apiProvider === 'gemini') {
            await runGeminiStreaming(combinedSystemPrompt, targetPrompt);
        } else if (currentSettings.apiProvider === 'openai') {
            await runOpenAIStreaming(combinedSystemPrompt, targetPrompt);
        } else if (currentSettings.apiProvider === 'aether') {
            await runAetherRequest(targetPrompt);
        }
    } catch (err) {
        optimizedPrompt.value = `❌ Error: ${err.message || err}`;
    } finally {
        loader.classList.remove('active');
        optimizeBtn.disabled = false;
    }
}

// 1. Google Gemini Streaming API Integration
async function runGeminiStreaming(systemPrompt, userPrompt) {
    const model = currentSettings.apiModel;
    const key = currentSettings.apiKey;
    
    // Using v1beta streamGenerateContent API with Server-Sent Events
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent?alt=sse&key=${key}`;
    
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contents: [
                {
                    parts: [
                        { text: systemPrompt + "\n\nPrompt to optimize:\n" + userPrompt }
                    ]
                }
            ],
            generationConfig: {
                temperature: 0.5
            }
        })
    });
    
    if (!response.ok) {
        const errorJson = await response.json().catch(() => ({}));
        throw new Error(errorJson.error?.message || `HTTP ${response.status} ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Save the last partial line back to the buffer
        buffer = lines.pop();
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6).trim();
                if (jsonStr === '[DONE]') continue;
                
                try {
                    const parsed = JSON.parse(jsonStr);
                    const chunkText = parsed.candidates?.[0]?.content?.parts?.[0]?.text;
                    if (chunkText) {
                        optimizedPrompt.value += chunkText;
                        optimizedPrompt.scrollTop = optimizedPrompt.scrollHeight;
                    }
                } catch (e) {
                    // Ignore JSON parsing errors for partial stream packets
                }
            }
        }
    }
}

// 2. OpenAI Streaming API Integration
async function runOpenAIStreaming(systemPrompt, userPrompt) {
    const model = currentSettings.apiModel;
    const key = currentSettings.apiKey;
    const url = 'https://api.openai.com/v1/chat/completions';
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${key}`
        },
        body: JSON.stringify({
            model: model,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ],
            temperature: 0.5,
            stream: true
        })
    });
    
    if (!response.ok) {
        const errorJson = await response.json().catch(() => ({}));
        throw new Error(errorJson.error?.message || `HTTP ${response.status} ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();
        
        for (const line of lines) {
            const cleanLine = line.trim();
            if (cleanLine.startsWith('data: ')) {
                const dataPayload = cleanLine.slice(6).trim();
                if (dataPayload === '[DONE]') continue;
                
                try {
                    const parsed = JSON.parse(dataPayload);
                    const chunkText = parsed.choices?.[0]?.delta?.content;
                    if (chunkText) {
                        optimizedPrompt.value += chunkText;
                        optimizedPrompt.scrollTop = optimizedPrompt.scrollHeight;
                    }
                } catch (e) {
                    // Ignore parsing errors for intermediate SSE lines
                }
            }
        }
    }
}

// 3. Local Aether Orchestrator Integration
async function runAetherRequest(userPrompt) {
    const url = 'http://127.0.0.1:8000/chat';
    
    // We send a direct prompt enhancement query to the orchestrator
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: `Optimize and polish the following prompt to make it structured, direct, and effective: \n"${userPrompt}"`,
            thread_id: 'prompsy_session'
        })
    });
    
    if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Aether backend error: ${errText || response.statusText}`);
    }
    
    const result = await response.json();
    if (result && result.final_response) {
        optimizedPrompt.value = result.final_response;
        optimizedPrompt.scrollTop = optimizedPrompt.scrollHeight;
    } else {
        throw new Error("Invalid response schema returned from local Aether orchestrator API.");
    }
}
