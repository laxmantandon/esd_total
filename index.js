const {
    app,
    Menu,
    Tray,
    nativeImage,
    BrowserWindow,
    dialog,
    
  } = require('electron');
  const { exec } = require("child_process");  
  const path = require('path');
  let execfile = require("child_process").execFile;
  
  let python_server = path.join(process.cwd(), 'resources/backend/dist/app/app.exe')

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });
  
  const createTray = () => {
    const iconPath = path.join(__dirname, "./icon/icon.png")
    const trayIcon = nativeImage.createFromPath(iconPath).resize({ width: 24, height: 24 })
    const tray = new Tray(trayIcon)
  
    const menuTemplate = [
      {
        label: null,
        enabled: false
      },
      {
        label: 'Start Server',
        enabled: true,
        click: () => {
          // Restart Server here
          execfile(python_server, {
            windowsHide: true
            }, (err, stdout, stderr) => {
                if (err) {
                    console.log("Error: ", err)
                }
                if (stdout) {
                    console.log("StdOut: ", stdout)
                }
                if (stderr) {
                    console.log("StdError: ", stderr)
                }
            })

          menuTemplate[1].enabled = false
          menuTemplate[2].enabled = true
          buildTrayMenu(menuTemplate)
        }
      },
      {
        label: 'Stop Server',
        enabled: false,
        click: () => {        
          // Kill Server Here
          exec('taskkill /f /t /im app.exe', (err, stdout, stderr) => {
            if(err){
                return;
            }
          })

          menuTemplate[1].enabled = true
          menuTemplate[2].enabled = false
          buildTrayMenu(menuTemplate)
        }
      },
      {
        label: 'About',
        click: () => {
          dialog.showMessageBox({
            title: 'ESD',
            message: "ESD 1.03", //1.02
            detail: "Developed and Maintained",
            buttons: ['OK'],
            icon: "./icon/stop.png"
          })
        }
      },
      {
        label: 'Quit',
        click: () => app.quit()
      }
    ]
  
    const buildTrayMenu = menu => {
      let lblStatus = "Inactive"
      let iconStatus = "./icon/stop.png"
      if (!menu[1].enabled) {
        lblStatus = "Active"
        iconStatus = "./icon/start.png"
      }
  
      const iconStatusPath = path.join(__dirname, iconStatus)
  
      menu[0].label = `"Service Status " ${lblStatus}`
      menu[0].icon = nativeImage.createFromPath(iconStatusPath).resize({ width: 24, height: 24 })
  
      const trayMenu = Menu.buildFromTemplate(menu)
      tray.setContextMenu(trayMenu)
    }
  
    buildTrayMenu(menuTemplate)
    menuTemplate[1].enabled = false
    menuTemplate[2].enabled = true
    buildTrayMenu(menuTemplate)
  
    // Start python server here
    execfile(python_server, {
        windowsHide: true,
    }, (err, stdout, stderr) => {
        if (err) {
            console.log("Error: ", err)
        }
        if (stdout) {
            console.log("StdOut: ", stdout)
        }
        if (stderr) {
            console.log("StdError: ", stderr)
        }
    })
  }
  
  app.on('ready', createTray);
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });

  app.on('quit', () => {
    // Kill Server Here
    exec('taskkill /f /t /im app.exe', (err, stdout, stderr) => {
        if(err){
            return;
        }
      })
      try{
        process.kill();
      }catch(err){
        console.log("Error: ", err)
      }
  })
  