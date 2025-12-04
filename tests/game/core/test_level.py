import unittest
import pathlib
import tempfile

from src.game.core.level import Level, _char_to_target


class LevelTest(unittest.TestCase):
    def setUp(self):
        self.path = pathlib.Path("tents-2025-11-27-3x2-easy.txt")

    # ======== FUNZIONI ========
    def test_char_to_target_dot_and_digit(self):
        """_char_to_target deve convertire '.' in 0 e una cifra nel suo int."""
        self.assertEqual(_char_to_target("."), 0)
        self.assertEqual(_char_to_target("7"), 7)

    def test_char_to_target_invalid_raises(self):
        """_char_to_target con caratteri strani deve lanciare ValueError."""
        with self.assertRaises(ValueError):
            _char_to_target("x")

    # ======== INIT / BASE ========
    def test_init_sets_fields_and_defaults(self):
        """Level deve salvare i campi e usare set vuoti se trees/correct_tents sono None."""
        lvl = Level(
            path=self.path,
            columns=3,
            lines=2,
            columns_targets=[0, 1, 2],
            rows_targets=[1, 0],
            trees=None,
            correct_tents=None
        )

        self.assertEqual(lvl.path, self.path)
        self.assertEqual(lvl.columns, 3)
        self.assertEqual(lvl.lines, 2)
        self.assertEqual(lvl.columns_targets, [0, 1, 2])
        self.assertEqual(lvl.rows_targets, [1, 0])
        self.assertEqual(lvl.trees, set())
        self.assertEqual(lvl.correct_tents, set())

    def test_difficulty_parsing(self):
        """difficulty deve leggere l'ultima parte del nome file dopo '-'."""
        lvl = Level(
            path=self.path,
            columns=3,
            lines=2,
            columns_targets=[0, 0, 0],
            rows_targets=[0, 0]
        )
        self.assertEqual(lvl.difficulty, "easy")

    def test_str_contains_basic_info(self):
        """__str__ deve contenere nome file, difficulty e dimensioni."""
        lvl = Level(
            path=self.path,
            columns=3,
            lines=2,
            columns_targets=[0, 0, 0],
            rows_targets=[0, 0]
        )
        s = str(lvl)
        self.assertIn(self.path.name, s)
        self.assertIn("easy", s)
        self.assertIn("3x2", s)

    # ======== FROM_FILE ========
    def test_from_file_parses_simple_level(self):
        """from_file deve creare un Level coerente con un file semplice."""
        # Formato:
        # header: X + target colonne (3 colonne)
        # righe: target riga + 3 celle
        content = "\n".join([
            "X012",
            "1T..",
            "0.^.",
        ])

        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "tents-2025-11-27-3x2-easy.txt"
            p.write_text(content, encoding="utf-8")

            lvl = Level.from_file(p)

            self.assertEqual(lvl.columns, 3)
            self.assertEqual(lvl.lines, 2)
            self.assertEqual(lvl.columns_targets, [0, 1, 2])
            self.assertEqual(lvl.rows_targets, [1, 0])

            self.assertIn((0, 0), lvl.trees)
            self.assertIn((1, 1), lvl.correct_tents)

    def test_from_file_invalid_cell_char_raises(self):
        """from_file con char cella non valido deve lanciare ValueError."""
        content = "\n".join([
            "X0",
            "0Z",   # Z non valido
        ])

        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "bad-level.txt"
            p.write_text(content, encoding="utf-8")

            with self.assertRaises(ValueError):
                Level.from_file(p)


if __name__ == "__main__":
    unittest.main()
