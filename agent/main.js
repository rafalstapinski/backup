const electron = require('electron')
const {app, Menu, Tray} = electron
const {ipcMain} = electron
const {BrowserWindow} = electron
const path = require('path')

let win

function createWindow() {
  win = new BrowserWindow({width: 800, height: 600})
  win.loadURL(`file://${__dirname}/index.html`)
  win.webContents.openDevTools()
  win.on('closed', () => {
    win = null
  })
}

function hideWindow() {
  win.hide()
}

ipcMain.on('hideWindow', (event, arg) => {
  console.log(arg)
  win.hide()
  event.returnValue = "return val"
})

const iconPath = path.join(__dirname, 'icon.png');

app.on('ready', () => {

  startServer()

  createWindow()
  win.hide()
  // tray = new Tray(iconPath)
  // const contextMenu = Menu.buildFromTemplate([
  //   {
  //     label: 'Item1',
  //     type: 'radio',
  //     icon: iconPath
  //   },
  //   {
  //     label: 'Item2',
  //     submenu: [
  //       { label: 'submenu1' },
  //       { label: 'submenu2' }
  //     ]
  //   },
  //   {
  //     label: 'Item3',
  //     type: 'radio',
  //     checked: true
  //   },
  //   {
  //     label: 'Toggle DevTools',
  //     accelerator: 'Alt+Command+I',
  //     click: function() {
  //       win.show();
  //       win.toggleDevTools();
  //     }
  //   },
  //   { label: 'Quit',
  //     accelerator: 'Command+Q',
  //     selector: 'terminate:',
  //   }
  // ])
  // tray.setToolTip('sample app tray')
  // tray.setContextMenu(contextMenu)
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
})

app.on('activate', () => {
  if (win === null) {
    createWindow();
  }
})
