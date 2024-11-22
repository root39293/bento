import PyInstaller.__main__

PyInstaller.__main__.run([
    'src/desktop.py',
    '--name=Bento_Assistant',
    '--onefile',
    '--windowed',
    '--add-data=static:static',
    '--clean',
    '--noconfirm',
    '--target-architecture=arm64',
]) 
