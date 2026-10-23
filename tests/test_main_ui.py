"""Tests for app.main_ui (smoke tests)."""
import unittest


class TestMainUI(unittest.TestCase):
    def test_main_ui_module_imports(self):
        import app.main_ui
        self.assertTrue(hasattr(app.main_ui, "main"))
        self.assertTrue(callable(app.main_ui.main))

    def test_main_is_callable(self):
        from app.main_ui import main
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()
