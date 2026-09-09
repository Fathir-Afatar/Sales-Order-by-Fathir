# Standard Library
import json
import os
import sys

class TranslationManager:
  """Manages application internationalization (i18n) by loading and retrieving

    translated strings from JSON locale files.

    Attributes:
        current_lang (str): The active language code (e.g., 'id', 'en').
        translations (Dict[str, Dict[str, Any]]): Dictionary holding loaded
          locale data mapped by language code.
    """
  def __init__(self, default_lang='id'):
    """Initialize the TranslationManager with a default language.

      Args:
          default_lang (str, optional): Initial language code to use. Defaults to
            'id'.
    """
    self.current_lang = default_lang
    self.translations = {}
    self.load_translations()

  def _get_base_path(self):
    """Determine the root base directory path of the application.

      Handles environment detection to resolve correct paths for both standard
      Python source execution and PyInstaller bundled executables.

      Returns:
          str: Absolute path to the base directory.
    """
    if getattr(sys, 'frozen', False):

      return sys._MEIPASS
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

  def load_translations(self):
    """Load JSON translation files for supported languages into memory.

    Scans the 'app/locales' directory relative to the base path and reads
    locale files for predefined language codes ('id', 'en').
    """
    base_dir = self._get_base_path()
    locales_dir = os.path.join(base_dir, 'app', 'locales')

    for lang in ['id', 'en']:
      file_path = os.path.join(locales_dir, f'{lang}.json')
      if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
          self.translations[lang] = json.load(f)
      else:
        print(f"[DEBUG] File bahasa tidak ditemukan di: {file_path}")

  def set_language(self, lang):
    """Switch the current active language if translations exist.

    Args:
        lang (str): Language code to set (e.g., 'id', 'en').
    """
    if lang in self.translations:
      self.current_lang = lang

  def get(self, key_path, default=''):
    """Retrieve a localized translation string using dot-notation syntax.

    Traverses nested JSON structures based on a key path (e.g.,
    'penjualan.msg_transaksi_sukses').

    Args:
        key_path (str): Dot-separated string representing the key hierarchy.
        default (str, optional): Fallback string returned if the key path is not
          found. Defaults to empty string, which falls back to returning the
          `key_path` itself.

    Returns:
        Union[str, Dict[str, Any]]: The localized string value or nested
        dictionary if found; otherwise the fallback string or original key
        path.
    """
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
  """Global alias function for quick translation lookups.

  Provides a concise wrapper around `i18n.get()` similar to standard gettext
  conventions.

  Args:
      key (str): Dot-separated key path for the desired translation string.

  Returns:
      Union[str, Dict[str, Any]]: Translated text matching the active language,
      or the input key if untranslated.
  """
  return i18n.get(key, key)