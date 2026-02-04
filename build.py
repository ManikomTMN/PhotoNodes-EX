import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--name=PhotoNodes EX',
    '--onefile',
    '--noconsole',
    '--icon=ICON.ico',
    '--add-data=ICON.ico;.',
])