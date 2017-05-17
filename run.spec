# -*- mode: python -*-

block_cipher = None


a = Analysis(['run.py'],
             pathex=['G:\\Projects\\Python\\StellarisProfiles'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

ui_files = [
    ('ui/main.ui', 'G:\\Projects\Python\\StellarisProfiles\\ui\\main.ui', 'DATA'),
    ('ui/dialog.ui', 'G:\\Projects\Python\\StellarisProfiles\\ui\\dialog.ui', 'DATA')
    ]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='run',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas + ui_files,
               strip=False,
               upx=True,
               name='run')
