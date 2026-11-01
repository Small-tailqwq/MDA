import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import register


class RegisterTest(unittest.TestCase):
    def test_marks_version_as_experimental(self):
        for version in ('v1.12.2', 'v1.12.2-beta.1', 'v1.12.2-ci.685-g56fbd49', 'v1.12.2+build.1'):
            self.assertEqual(register.experimental_version(version), 'v1.12.2-experimental')

    def test_rejects_unknown_version(self):
        for version in (None, '', 'DEBUG_VERSION', '1.2'):
            with self.subTest(version=version), self.assertRaises(SystemExit):
                register.experimental_version(version)

    def test_registers_controller_methods_and_locales(self):
        script = Path(__file__).resolve().parents[1] / 'register.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'locales').mkdir()
            interface = {
                'version': 'v1.12.2',
                'github': 'https://github.com/1204244136/MDA',
                'mirrorchyan_rid': 'MDA',
                'controller': [{'name': 'AAA', 'type': 'Win32',
                                'win32': {'mouse': 'Interception', 'keyboard': 'Seize'}}],
                'languages': {'zh_cn': 'locales/zh.json', 'en_us': 'locales/en.json'},
            }
            (root / 'interface.json').write_text(json.dumps(interface), encoding='utf-8')
            for name in ('zh', 'en'):
                (root / f'locales/{name}.json').write_text('{}', encoding='utf-8')
            subprocess.run([sys.executable, str(script), str(root)], check=True)
            result = json.loads((root / 'interface.json').read_text(encoding='utf-8'))
            self.assertEqual(result['version'], 'v1.12.2-experimental')
            self.assertEqual(result['github'], interface['github'])
            self.assertNotIn('mirrorchyan_rid', result)
            self.assertEqual(result['controller'][0], interface['controller'][0])
            for entry, name in zip(result['controller'][1:], ('Logitech', 'Razer'), strict=True):
                self.assertEqual(entry['name'], name)
                self.assertEqual(entry['win32']['mouse'], name)
                self.assertEqual(entry['win32']['keyboard'], name)
                for lang in ('zh', 'en'):
                    locale = json.loads((root / f'locales/{lang}.json').read_text(encoding='utf-8'))
                    self.assertEqual(locale[f'controller.{name}.label'], name)


if __name__ == '__main__':
    unittest.main()
