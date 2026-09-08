# Standard Library
import json
import os
import sys

class TranslationManager:

  def __init__(self, default_lang='id'):
    self.current_lang = default_lang
    self.translations = {}
    self.load_translations()

  def _get_base_path(self):
    if getattr(sys, 'frozen', False):
      return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

  def load_translations(self):
    base_dir = self._get_base_path()
    locales_dir = os.path.join(base_dir, 'locales')

    for lang in ['id', 'en']:
      file_path = os.path.join(locales_dir, f'{lang}.json')
      if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
          self.translations[lang] = json.load(f)

  def set_language(self, lang):
    if lang in self.translations:
      self.current_lang = lang

  def get(self, key_path, default=''):
    """Mengambil teks berdasarkan key."""
    keys = key_path.split('.')
    data = self.translations.get(self.current_lang, {})

    for k in keys:
      if isinstance(data, dict) and k in data:
        data = data[k]
      else:
        return default if default else key_path

    return data
# Inisialisasi Singleton Instance
i18n = TranslationManager()

# Alias fungsi pembantu agar pemanggilan singkat seperti di framework standar
def _(key):
  return i18n.get(key, key)