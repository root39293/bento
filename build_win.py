import PyInstaller.__main__
import os
import sys

static_path = os.path.abspath('static')
config_path = os.path.abspath('config')

PyInstaller.__main__.run([
    'src/desktop.py',
    '--name=Bento_Assistant',
    '--onefile',
    '--windowed',
    '--add-data=static;static',
    '--add-data=config;config',
    '--clean',
    '--noconfirm',
    '--hidden-import=webview',
    '--hidden-import=webview.platforms.winforms',
    '--hidden-import=clr',
    '--hidden-import=pythonnet',
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
    '--hidden-import=tqdm',
    '--hidden-import=tqdm.auto',
    '--collect-all=tqdm',
    '--collect-all=chromadb',
    '--debug=all',
]) 