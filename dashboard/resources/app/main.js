const {app, BrowserWindow, ipcMain} = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow()
{
    const win = new BrowserWindow(
        {
            width : 1290,
            height: 780,
            webPreferences: {
                preload: path.join(__dirname, 'preload.js')
            }
        }
    );
    win.loadFile('home.html')
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {app.quit();} )

ipcMain.handle('getConfigFile', () => {
    return path.join(process.env.maxxaipath, 'assets', 'config.json');
})
ipcMain.handle('updateJsonFile', (event, jsonData) => {

    const maxxpath = process.env.maxxaipath;
    const filePath = path.join(maxxpath, 'assets', 'config.json');
    fs.writeFile(filePath, JSON.stringify(jsonData, null, 2), (err) => {
      if (err) {
        event.returnValue = { success: false, error: err.message };
      } else {
        event.returnValue = { success: true };
      }
    });
  });
  
  