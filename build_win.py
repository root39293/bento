import PyInstaller.__main__
import os
import sys

static_path = os.path.abspath('static')

PyInstaller.__main__.run([
    'src/desktop.py',
    '--name=Bento_Assistant',
    '--onefile',
    '--windowed',
    '--add-data=static;static',
    '--clean',
    '--noconfirm',
    '--hidden-import=webview.platforms.winforms',
    '--hidden-import=asyncio',
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.asyncio',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.h11_impl',
    '--collect-all=uvicorn',
    '--hidden-import=os',
    '--hidden-import=sys',
    '--hidden-import=resource',
    '--debug=all',
]) 