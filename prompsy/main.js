const { app, BrowserWindow, globalShortcut, Tray, Menu, ipcMain, clipboard, screen, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');

let mainWindow = null;
let trayIcon = null;
const settingsPath = path.join(app.getPath('userData'), 'settings.json');

// Default Settings
const defaultSettings = {
    apiKey: '',
    apiProvider: 'gemini', // 'gemini' | 'openai' | 'aether'
    apiModel: 'gemini-1.5-flash',
    globalShortcut: 'Ctrl+Shift+E',
    autoPaste: true,
    systemPrompt: "You are an expert prompt optimizer. Reconstruct the following prompt to make it clearer, more structured, context-rich, and effective for modern LLMs. Retain the original intent but improve formatting, instructions, hierarchy, and token efficiency. Output only the optimized prompt, with no intro, outro, or markdown code-fences (unless they are part of the prompt structure)."
};

function loadSettings() {
    if (!fs.existsSync(settingsPath)) {
        fs.writeFileSync(settingsPath, JSON.stringify(defaultSettings, null, 2), 'utf-8');
        return defaultSettings;
    }
    try {
        const raw = fs.readFileSync(settingsPath, 'utf-8');
        return { ...defaultSettings, ...JSON.parse(raw) };
    } catch (e) {
        return defaultSettings;
    }
}

function saveSettings(settings) {
    fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2), 'utf-8');
}

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 600,
        height: 480,
        show: false,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    mainWindow.loadFile('index.html');

    mainWindow.on('blur', () => {
        mainWindow.hide();
    });
}

function setupTray() {
    const iconDataUrl = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JkfUEAAAG/SURBVHjafJPfS5NhGMfP27mz2z+w0h8gKKhkQghRkCCthxKy6E/QSpM0bSR1ERq10ExNyy0NTS01tTQk2pS2lW5aU0oJzY+5oR76uX3v7vM6RUT0wkvv6/d9n9/nPM8rK5lMhnEcXyFjGMMo/gR2sYt3mEa/hDGMYhSjGMeI+R9hEIM4hAncR/i/QG+o/4sN3EaM+1P8xHn8wDweR2qH+Vl3Zp7P5/N+0+l0Hl7T6XQeXrtuNptNnU6nK5vN5uG1U2o2m+r5fN7V6/UeXrtW1+l0+nw+n+9er5eWl5dprVarcXp6SjKZJJfLceHCBYrFIslkklwuR6fT4eTkBLVa7eG10+l02el0unK5HKVSiampKZrNJvPz83R1dVFfX08ikSCTyTAwMEBXVxedTofP5/u712w2G7lcLheNRiOfz1NbW0tnZyf19fU0NzdTX19PfX09ra2tNDY2UiqVqKurY2hoqG+72Ww2crmcXC5HqVSiqquKyspK6uvraWxsxG63U1dXxzAMU1tbS319PbW1tXfbLZfL5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5XK5d/gD5Z1b2nL2Q1AAAAABJRU5ErkJggg==';
    const trayIconImg = nativeImage.createFromDataURL(iconDataUrl);
    trayIcon = new Tray(trayIconImg);
    trayIcon.setToolTip('Prompsy - AI Prompt Enhancer');
    
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Prompsy Active', enabled: false },
        { type: 'separator' },
        { label: 'Show Window', click: () => { showEnhancementWindow(false); } },
        { label: 'Settings', click: () => { showEnhancementWindow(true); } },
        { type: 'separator' },
        { label: 'Exit', click: () => { app.isQuitting = true; app.quit(); } }
    ]);
    
    trayIcon.setContextMenu(contextMenu);
    trayIcon.on('double-click', () => {
        showEnhancementWindow(false);
    });
}

function registerGlobalKey() {
    const settings = loadSettings();
    globalShortcut.unregisterAll();
    
    try {
        const success = globalShortcut.register(settings.globalShortcut, () => {
            triggerCaptureFlow();
        });
        if (!success) {
            console.error(`Failed to register shortcut: ${settings.globalShortcut}`);
        }
    } catch (e) {
        console.error(`Invalid shortcut format: ${settings.globalShortcut}`);
    }
}

function triggerCaptureFlow() {
    if (mainWindow) {
        mainWindow.hide();
    }
    
    // Execute KeySimulator.exe to copy the active selection
    const exePath = path.join(__dirname, 'KeySimulator.exe');
    execFile(exePath, ['copy'], (error) => {
        if (error) {
            console.error('Failed to trigger copy:', error);
        }
        
        // Read text from clipboard after a tiny timeout to allow clipboard write to complete
        setTimeout(() => {
            const selectedText = clipboard.readText();
            showEnhancementWindow(false, selectedText);
        }, 180);
    });
}

function showEnhancementWindow(showSettingsOnly = false, initialText = '') {
    if (!mainWindow) return;

    // Center window on active screen
    const cursor = screen.getCursorScreenPoint();
    const activeDisplay = screen.getDisplayNearestPoint(cursor);
    const { x, y, width, height } = activeDisplay.bounds;
    
    const winWidth = 600;
    const winHeight = 480;
    const winX = Math.round(x + (width - winWidth) / 2);
    const winY = Math.round(y + (height - winHeight) / 2);
    
    mainWindow.setBounds({ x: winX, y: winY, width: winWidth, height: winHeight });
    mainWindow.show();
    mainWindow.focus();

    // Notify renderer of action
    mainWindow.webContents.send('init-data', {
        showSettingsOnly,
        initialText,
        settings: loadSettings()
    });
}

function handlePasteBack(text) {
    clipboard.writeText(text);
    if (mainWindow) {
        mainWindow.hide();
    }
    
    const exePath = path.join(__dirname, 'KeySimulator.exe');
    execFile(exePath, ['paste'], (error) => {
        if (error) {
            console.error('Failed to trigger paste:', error);
        }
    });
}

// IPC Handlers
ipcMain.handle('get-settings', () => {
    return loadSettings();
});

ipcMain.handle('save-settings', (event, settings) => {
    saveSettings(settings);
    registerGlobalKey(); // Re-register key in case the shortcut changed
    return true;
});

ipcMain.handle('close-window', () => {
    if (mainWindow) {
        mainWindow.hide();
    }
});

ipcMain.handle('paste-back', (event, text) => {
    handlePasteBack(text);
});

ipcMain.handle('write-clipboard', (event, text) => {
    clipboard.writeText(text);
});

// App Lifecycle
app.whenReady().then(() => {
    createMainWindow();
    setupTray();
    registerGlobalKey();
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createMainWindow();
        }
    });
});

app.on('will-quit', () => {
    globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        // Keep active in tray, don't quit
    }
});
