import unittest
from unittest.mock import Mock, patch

from src.game.core.game import Game
from src.game.state import Action, CellState


class GameTest(unittest.TestCase):
    def setUp(self):
        # Board 2x2 valida come livello:
        # tree (0,0); tent soluzione (1,0)
        self.columns = 2
        self.rows = 2

        self.trees = {(0, 0)}
        self.solution_tents = {(1, 0)}

        self.columns_targets = [0, 1]
        self.rows_targets = [1, 0]

        self.game = Game(
            columns=self.columns,
            rows=self.rows,
            trees=self.trees,
            tents=self.solution_tents,
            columns_targets=self.columns_targets,
            rows_targets=self.rows_targets,
        )

    # ======== INIT ========
    @staticmethod
    def test_init_calls_generate_board_when_trees_none():
        """Se trees è None, __init__ deve chiamare generate_board()."""
        with patch.object(Game, "generate_board") as mock_gen:
            Game(columns=5, rows=5, trees=None, tents=None)
        mock_gen.assert_called_once_with()

    @staticmethod
    def test_init_calls_generate_board_when_board_invalid():
        """Se trees/tents sono presenti ma non validi, __init__ deve rigenerare la board."""
        with patch.object(Game, "is_valid_board", return_value=False) as mock_valid:
            with patch.object(Game, "generate_board") as mock_gen:
                Game(
                    columns=2,
                    rows=2,
                    trees={(0, 0)},
                    tents={(1, 0)},
                    columns_targets=[0, 1],
                    rows_targets=[1, 0],
                )
        mock_valid.assert_called()
        mock_gen.assert_called_once_with()

    # ======== READ / CELL STATE ========
    def test_read_returns_correct_state(self):
        """read deve dare priorità: TREE > TENT > GRASS > EMPTY."""
        self.game.tents = {(1, 1)}
        self.game.grass = {(0, 1)}

        self.assertEqual(self.game.read(0, 0), str(CellState.TREE))
        self.assertEqual(self.game.read(1, 1), str(CellState.TENT))
        self.assertEqual(self.game.read(0, 1), str(CellState.GRASS))
        self.assertEqual(self.game.read(1, 0), str(CellState.EMPTY))

    def test_get_cell_state_outside(self):
        """get_cell_state fuori board deve tornare OUT."""
        self.assertEqual(self.game.get_cell_state(-1, 0), CellState.OUT)
        self.assertEqual(self.game.get_cell_state(0, -1), CellState.OUT)
        self.assertEqual(self.game.get_cell_state(self.columns, 0), CellState.OUT)
        self.assertEqual(self.game.get_cell_state(0, self.rows), CellState.OUT)

    # ======== PLAY ========
    def test_play_click_does_nothing_on_tree(self):
        """Click su un albero non deve fare nulla."""
        self.game.play(0, 0, None)
        self.assertNotIn((0, 0), self.game.tents)
        self.assertNotIn((0, 0), self.game.grass)

    def test_play_click_toggle_cycle(self):
        """Click su cella libera: EMPTY -> TENT -> GRASS -> EMPTY."""
        pos = (1, 1)

        self.game.play(*pos, None) # type: ignore
        self.assertIn(pos, self.game.tents)
        self.assertNotIn(pos, self.game.grass)

        self.game.play(*pos, None) # type: ignore
        self.assertNotIn(pos, self.game.tents)
        self.assertIn(pos, self.game.grass)

        self.game.play(*pos, None) # type: ignore
        self.assertNotIn(pos, self.game.tents)
        self.assertNotIn(pos, self.game.grass)

    def test_play_skip_does_nothing(self):
        """Action.SKIP non deve cambiare lo stato."""
        self.game.tents = {(1, 1)}
        self.game.grass = {(0, 1)}

        before_tents = set(self.game.tents)
        before_grass = set(self.game.grass)

        self.game.play(1, 1, Action.SKIP)

        self.assertEqual(self.game.tents, before_tents)
        self.assertEqual(self.game.grass, before_grass)

    def test_play_place_grass(self):
        """Action.PLACE_GRASS deve chiamare _auto_grass()."""
        self.game._auto_grass = Mock()
        self.game.play(0, 0, Action.PLACE_GRASS)
        self.game._auto_grass.assert_called_once_with()

    def test_play_place_tent(self):
        """Action.PLACE_TENT deve chiamare _auto_tents()."""
        self.game._auto_tents = Mock()
        self.game.play(0, 0, Action.PLACE_TENT)
        self.game._auto_tents.assert_called_once_with()

    def test_play_place_solution(self):
        """Action.PLACE_SOLUTION deve piazzare soluzione e riempire il resto di prato."""
        self.game.grass = set()
        self.game.tents = set()

        self.game.play(0, 0, Action.PLACE_SOLUTION)

        self.assertEqual(set(self.game.tents), set(self.game.correct_tents))

        expected_grass = {(0, 1), (1, 1)}
        self.assertEqual(set(self.game.grass), expected_grass)

    # ======== FINISHED / PROGRESS / STATUS ========
    def test_finished_true_on_solved_board(self):
        """finished deve essere True quando tende e target combaciano e la board è valida."""
        self.game.tents = {(1, 0)}  # soluzione
        self.assertTrue(self.game.finished())

    def test_finished_false_when_targets_dont_match(self):
        """finished deve essere False se i target non corrispondono."""
        self.game.tents = {(1, 0)}  # soluzione, ma target cambiati
        self.game.columns_targets = [1, 0]
        self.assertFalse(self.game.finished())

    def test_progress_none_when_no_solution_known(self):
        """progress deve tornare None se non c'è una soluzione (correct_tents vuoto)."""
        self.game.correct_tents = set()
        self.assertIsNone(self.game.progress())

    def test_progress_full_when_all_correct(self):
        """progress deve valere 1.0 se tutte le tende sono corrette."""
        self.game.tents = {(1, 0)}
        self.assertEqual(self.game.progress(), 1.0)

    def test_progress_penalizes_incorrect_tents(self):
        """progress deve scendere se metto tende sbagliate."""
        self.game.tents = {(1, 0), (1, 1)}  # una giusta, una sbagliata
        self.assertEqual(self.game.progress(), 0.5)

    def test_status_includes_solution_when_available(self):
        """status deve includere Solution se progress è disponibile."""
        self.game.tents = {(1, 0)}
        s = self.game.status()
        self.assertIn("Solution:", s)
        self.assertIn("Tents placed:", s)

    def test_status_without_solution_percent_when_not_available(self):
        """status non deve includere Solution se progress è None."""
        self.game.correct_tents = set()
        s = self.game.status()
        self.assertNotIn("Solution:", s)
        self.assertIn("Tents placed:", s)

    # ======== N4 / N8 ========
    def test_n4_neighbors_corner(self):
        """n4 su un angolo deve dare solo 2 vicini."""
        ns = set(self.game.n4(0, 0))
        self.assertEqual(ns, {(1, 0), (0, 1)})

    def test_n8_neighbors_center_like(self):
        """n8 su (1,1) in una 3x3 deve dare 8 vicini."""
        g = Game(
            columns=3,
            rows=3,
            trees={(0, 0), (2, 2)},
            tents={(1, 0), (1, 2)},
            columns_targets=[0, 2, 0],
            rows_targets=[1, 0, 1],
        )
        ns = set(g.n8(1, 1))
        self.assertEqual(len(ns), 8)
        self.assertIn((0, 0), ns)
        self.assertIn((2, 2), ns)

    # ======== VALIDAZIONE BOARD ========
    def test_is_valid_board_true_on_valid_solution(self):
        """is_valid_board deve tornare True su una configurazione valida."""
        g = Game(
            columns=3,
            rows=3,
            trees={(0, 0), (2, 2)},
            tents={(1, 0), (1, 2)},
            columns_targets=[0, 2, 0],
            rows_targets=[1, 0, 1],
        )
        self.assertTrue(g.is_valid_board())

    def test_is_valid_board_false_on_diagonal_n8_tents(self):
        """Due tende che si toccano in diagonale rendono la board non valida."""
        g = Game(
            columns=3,
            rows=3,
            trees={(0, 0), (2, 2)},
            tents={(1, 0), (1, 2)},
            columns_targets=[0, 2, 0],
            rows_targets=[1, 0, 1],
        )
        bad_tents = {(1, 0), (2, 1)}  # diagonale: (1,0) tocca (2,1)
        self.assertFalse(g.is_valid_board(g.trees, bad_tents))

    def test_is_valid_board_false_when_tent_has_no_n4_tree(self):
        """Una tenda senza alberi adiacenti in n4 rende la board non valida."""
        g = Game(
            columns=3,
            rows=3,
            trees={(0, 0), (2, 2)},
            tents={(1, 0), (1, 2)},
            columns_targets=[0, 2, 0],
            rows_targets=[1, 0, 1],
        )
        bad_tents = {(0, 2)}  # non è adiacente né a (0,0) né a (2,2)
        self.assertFalse(g.is_valid_board(g.trees, bad_tents))

    # ======== TARGET LAZY + RESET ========
    def test_reset_targets_forces_recompute(self):
        """reset_targets deve forzare il ricalcolo di rows_targets/columns_targets."""
        g = Game(
            columns=3,
            rows=3,
            trees={(0, 0), (2, 2)},
            tents={(1, 0), (1, 2)},
            columns_targets=[0, 2, 0],
            rows_targets=[1, 0, 1],
        )

        old_cols = g.columns_targets
        self.assertEqual(old_cols, [0, 2, 0])

        g.correct_tents = {(1, 0)}  # cambia soluzione ma la cache resta
        self.assertEqual(g.columns_targets, [0, 2, 0])

        g.reset_targets()
        self.assertEqual(g.columns_targets, [0, 1, 0])
        self.assertEqual(g.rows_targets, [1, 0, 0])

    # ======== GENERAZIONE ========
    def test_generate_board_creates_valid_board_and_targets(self):
        """generate_board(seed) deve produrre una board valida e target coerenti."""
        g = Game(
            columns=6,
            rows=6,
            trees={(0, 0)},
            tents={(1, 0)},
            columns_targets=[0, 1, 0, 0, 0, 0],
            rows_targets=[1, 0, 0, 0, 0, 0],
        )

        g.generate_board(seed=123)

        self.assertIsInstance(g.trees, set)
        self.assertIsInstance(g.correct_tents, set)

        self.assertEqual(len(g.trees), len(g.correct_tents))
        self.assertTrue(g.is_valid_board(g.trees, g.correct_tents))

        self.assertEqual(len(g.columns_targets), g.columns)
        self.assertEqual(len(g.rows_targets), g.lines)

        self.assertEqual(sum(g.columns_targets), len(g.correct_tents))
        self.assertEqual(sum(g.rows_targets), len(g.correct_tents))


if __name__ == "__main__":
    unittest.main()
