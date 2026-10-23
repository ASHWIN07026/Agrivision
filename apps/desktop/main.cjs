const { app, BrowserWindow, shell, session, Menu } = require('electron');
const path = require('node:path');
const SITE = 'https://agrivision-6o2f.onrender.com';
const isInternal = value => { try { return new URL(value).origin === SITE; } catch { return false; } };
function external(value) {
  try { const url = new URL(value); if (['https:', 'mailto:', 'tel:'].includes(url.protocol)) shell.openExternal(value); } catch {}
}
function createWindow() {
  const win = new BrowserWindow({ width: 1280, height: 860, minWidth: 380, minHeight: 600, title: 'AgriVision', autoHideMenuBar: true, webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true, webSecurity: true, allowRunningInsecureContent: false } });
  win.webContents.setWindowOpenHandler(({ url }) => { external(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (event, url) => {
    if (!isInternal(url)) { event.preventDefault(); external(url); }
  });
  win.webContents.on('did-fail-load', (_event, code, _description, url, isMainFrame) => {
    if (isMainFrame && code !== -3 && isInternal(url)) win.loadFile(path.join(__dirname, 'offline.html'));
  });
  win.webContents.on('will-redirect', (event, url) => { if (!isInternal(url)) { event.preventDefault(); external(url); } });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { label: 'AgriVision', submenu: [{ label: 'Home / Retry connection', click: () => win.loadURL(SITE) }, { label: 'Open in browser', click: () => shell.openExternal(SITE) }, { type: 'separator' }, { role: 'quit' }] },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { role: 'togglefullscreen' }] }
  ]));
  win.loadURL(SITE);
}
app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback, details) => {
    callback(isInternal(webContents.getURL()) && isInternal(details.requestingUrl || webContents.getURL()) && ['media', 'geolocation'].includes(permission));
  });
  session.defaultSession.setPermissionCheckHandler((_webContents, permission, origin) => isInternal(origin) && ['media', 'geolocation'].includes(permission));
  createWindow();
  app.on('activate', () => { if (!BrowserWindow.getAllWindows().length) createWindow(); });
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
