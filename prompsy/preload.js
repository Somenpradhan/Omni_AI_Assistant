const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('prompsyAPI', {
    onInitData: (callback) => ipcRenderer.on('init-data', (event, data) => callback(data)),
    getSettings: () => ipcRenderer.invoke('get-settings'),
    saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
    closeWindow: () => ipcRenderer.invoke('close-window'),
    pasteBack: (text) => ipcRenderer.invoke('paste-back', text),
    writeClipboard: (text) => ipcRenderer.invoke('write-clipboard', text)
});
