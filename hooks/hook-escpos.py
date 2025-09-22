from PyInstaller.utils.hooks import collect_submodules

# Ambil semua submodul escpos, kecuali capabilities
hiddenimports = [mod for mod in collect_submodules('escpos') if not mod.startswith('escpos.capabilities')]