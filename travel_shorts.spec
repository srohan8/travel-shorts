import sys
block_cipher = None

from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('index.html',   '.'),
        ('ffmpeg/bin',   'ffmpeg/bin'),
        ('.env.example', '.'),
    ] + collect_data_files('cv2'),   # includes haar cascade XMLs
    hiddenimports=[
        # Flask
        'flask',
        'flask.json',
        'flask.templating',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        # Google Gemini
        'google.generativeai',
        'google.api_core',
        'google.api_core.gapic_v1',
        'google.auth',
        'google.auth.transport.requests',
        'google.auth.transport.urllib3',
        # Ollama + its HTTP stack (httpx-based)
        'ollama',
        'httpx',
        'httpx._client',
        'httpx._config',
        'httpx._transports',
        'httpx._transports.default',
        'httpcore',
        'httpcore._async',
        'httpcore._sync',
        'h11',
        'h11._readers',
        'h11._writers',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        'sniffio',
        'certifi',
        'idna',
        # Pillow
        'PIL',
        'PIL.Image',
        'PIL.JpegImagePlugin',
        # dotenv
        'dotenv',
        'dotenv.main',
        # OpenCV + NumPy
        'cv2',
        'cv2.data',
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Travel Shorts AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # no terminal window for end users
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Travel Shorts AI',
)

# Mac .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Travel Shorts AI.app',
        bundle_identifier='io.moonga.travel-shorts',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
