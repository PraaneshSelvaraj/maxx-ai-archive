const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  updateJsonFile: (jsonData) => ipcRenderer.invoke('updateJsonFile', jsonData),
  getConfigFile: () => ipcRenderer.invoke("getConfigFile", ),
});
