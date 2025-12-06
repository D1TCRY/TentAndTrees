from typing import Iterable, Collection
import random

from ..board_game import BoardGame

from ..state import Action, CellState

class Game(BoardGame):
    def __init__(self,
                 columns: int = 5,
                 rows: int = 5,
                 *,
                 trees: Collection[tuple[int, int]] | None = None,
                 tents: Collection[tuple] | None = None,
                 rows_targets: list[int] | None = None,
                 columns_targets: list[int] | None = None) -> None:
        """
            Crea una nuova partita/board di TentsAndTrees.

            Puoi usarlo in due modi:
            - passando un livello già pronto (trees, tents=soluzione, e i target di righe/colonne);
            - lasciando tutto a None: in quel caso genera una board casuale valida.

            Nota: se passi alberi/tende ma la configurazione non rispetta i vincoli del gioco,
            qui viene rigenerata automaticamente una board valida.
            """

        self.columns = columns
        self.lines = rows

        self.trees = trees
        self.correct_tents = tents
        self.grass = set()
        self.tents = set()

        self.columns_targets = columns_targets
        self.rows_targets = rows_targets

        if self.trees is None:
            self.generate_board()
        elif not self.is_valid_board(self.trees, self.correct_tents):
            self.generate_board()

    # ======== INTERFACE IMPLEMENTATION ========
    def cols(self) -> int:
        return self.columns

    def rows(self) -> int:
        return self.lines

    def read(self, x: int, y: int) -> str:
        """
            Restituisce cosa c'è nella cella (x, y) come stringa di CellState.

            È il metodo che la GUI usa per sapere cosa disegnare: albero, tenda, prato o vuoto.
            Non cambia lo stato del gioco.
        """
        pos = (x, y)
        if pos in self.trees:
            return str(CellState.TREE)
        if pos in self.tents:
            return str(CellState.TENT)
        if pos in self.grass:
            return str(CellState.GRASS)
        return str(CellState.EMPTY)

    def play(self, x: int, y: int, action: Action | None) -> None:
        """
            Applica un'azione di gioco su una cella (x, y).

            - action None / Action.NONE: comportamento "click":
              * sugli alberi non fa nulla
              * vuoto -> tenda
              * tenda -> prato
              * prato -> vuoto

            - Action.PLACE_GRASS: esegue le regole automatiche che marcano prato certo.
            - Action.PLACE_TENT: esegue le regole automatiche che piazzano tende certe.
            - Action.PLACE_SOLUTION: piazza tutta la soluzione (se disponibile) e riempie il resto di prato.
            - Action.SKIP: non fa niente.
        """

        if action is Action.SKIP:
            return

        if action is None or action == Action.NONE:
            pos = (x, y)
            if pos in self.trees:
                return

            if pos in self.tents:
                self.tents.remove(pos)
                self.grass.add(pos)
            elif pos in self.grass:
                self.grass.remove(pos)
            else:
                self.tents.add(pos)


        elif action is Action.PLACE_GRASS:
            self._auto_grass()
        elif action is Action.PLACE_TENT:
            self._auto_tents()
        elif action is Action.PLACE_SOLUTION:
            if not self.correct_tents: return

            self.tents = self.correct_tents

            for i in range(self.lines):
                for j in range(self.columns):
                    self.grass.add((j, i)) if (j, i) not in self.trees and (j, i) not in self.tents else None

    def finished(self) -> bool:
        """
            Ritorna True quando il livello è risolto.

            Per essere "finito" devono valere insieme:
            - la disposizione corrente delle tende è valida (vincoli base: dentro board, no tende adiacenti, ecc.)
            - il conteggio tende per ogni riga/colonna combacia esattamente coi target.

            In pratica: qui si decide la vittoria.
        """
        cols, rows = self.columns, self.lines
        tents = self.tents

        candidate_columns_targets = [
            sum((x, y) in tents for y in range(rows))
            for x in range(cols)
        ]
        candiate_rows_targets = [
            sum((x, y) in tents for x in range(cols))
            for y in range(rows)
        ]

        return self.is_valid_board(self.trees, self.tents) and candidate_columns_targets == self.columns_targets and candiate_rows_targets == self.rows_targets

    def progress(self) -> float | None:
        """
            Stima una percentuale di quanto sei vicino alla soluzione, se la soluzione esiste.

            L'idea è semplice:
            - ogni tenda piazzata corretta aumenta lo score
            - ogni tenda piazzata sbagliata lo diminuisce
            - il valore viene normalizzato sul numero totale di tende corrette

            Torna None se non c'è una soluzione nota.
        """
        if self.correct_tents:
            solution = 0
            for tent in self.tents:
                if tent in self.correct_tents:
                    solution += 1
                else:
                    solution -= 0.5

            return round(max(0, (solution/len(self.correct_tents))), 5)
        return None

    def status(self) -> str:
        """
            Genera una stringa breve da mostrare nella barra in basso.

            Include:
            - percentuale di soluzione (se calcolabile)
            - numero di tende piazzate rispetto al numero di alberi

            È pensata per essere leggibile durante il gioco.
        """
        strings = []

        if self.progress() is not None:
            strings.append(f"Solution: {self.progress()*100:.2f}%")

        strings.append(f"Tents placed: {len(self.tents)}/{len(self.trees)}")

        return " - ".join(strings)




    # ======== HELPERS ========
    def get_cell_state(self, x: int, y: int) -> CellState | None:
        """
            Versione “comoda” di read(): restituisce direttamente un CellState.

            Se la cella è fuori dalla board restituisce CellState.OUT, così la GUI può colorarla
            diversamente senza fare controlli extra.
        """

        if not self.inside(x, y):
            return CellState.OUT

        if (x, y) in self.trees:
            return CellState.TREE
        elif (x, y) in self.tents:
            return CellState.TENT
        elif (x, y) in self.grass:
            return CellState.GRASS
        return CellState.EMPTY

    def inside(self, x: int, y: int) -> bool:
        cols, rows = self.columns, self.lines
        return 0 <= x < cols and 0 <= y < rows

    def n4(self, x: int, y: int) -> Iterable[tuple[int, int]]:
        """
            Itera sui vicini ortogonali (su/giu/sinistra/destra) restando dentro al board.

            Utile per il legame albero-tenda.
        """
        cols, rows = self.columns, self.lines
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self.inside(nx, ny):
                yield nx, ny

    def n8(self, x: int, y: int) -> Iterable[tuple[int, int]]:
        """
            Itera sui vicini in 8 direzioni (incluse diagonali) restando dentro al board.

            Serve soprattutto per controllare che le tende non si tocchino in diagonale.
        """
        cols, rows = self.columns, self.lines
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.inside(nx, ny):
                    yield nx, ny

    def generate_board(self, seed: int | None = None) -> None:
        """
            Genera una board casuale valida.

            - prova a mettere un certo numero di tende in posizioni che NON si toccano (n8)
            - per ogni tenda trova un albero adiacente (n4), 1 a 1, senza sovrapposizioni
            - salva la soluzione in correct_tents e gli alberi in trees
            - resetta i target così vengono ricalcolati dalla soluzione

            Se non riesce a generare con la densità desiderata, abbassa gradualmente il numero
            di coppie tenda-albero finché non trova qualcosa.
        """
        cols, rows = self.columns, self.lines
        rng = random.Random() if seed is None else random.Random(seed)

        # -> coppie tenda-albero da generare
        desired_pairs = max(1, round(cols * rows * 0.25))

        cells = [(x, y) for y in range(rows) for x in range(cols)]

        def try_generate(n_pairs: int) -> tuple[set[tuple[int, int]], set[tuple[int, int]]] | None:
            # -> posiziona n_pairs tende in modo valido
            rng.shuffle(cells)
            tents: set[tuple[int, int]] = set()

            for (x, y) in cells:
                if len(tents) >= n_pairs:
                    break
                if any((nx, ny) in tents for nx, ny in self.n8(x, y)):
                    continue
                tents.add((x, y))

            if len(tents) != n_pairs:
                return None

            # -> per ogni tenda 1 albero adiacente
            trees: set[tuple[int, int]] = set()

            tents_list = list(tents)
            rng.shuffle(tents_list)
            n4_dirs = [(-1,0), (1,0), (0,-1), (0,1)]

            for tent in tents_list:
                rng.shuffle(n4_dirs)
                chosen = False
                for dir_ in n4_dirs:
                    candidate_tree = tent[0]+dir_[0], tent[1]+dir_[1]
                    if self.inside(candidate_tree[0], candidate_tree[1]) and candidate_tree not in trees and candidate_tree not in tents:
                        trees.add(candidate_tree)
                        chosen = True
                        break

                if not chosen:
                    return None

            return tents, trees

        # -> prova a generare -> se fallisce riduce il numero di coppie
        tents = trees = None
        for pair_number in range(desired_pairs, 0, -1):
            for _ in range(400):  # tentativi per quel pair_number
                out = try_generate(pair_number)
                if out is not None:
                    tents, trees = out
                    break
            if tents is not None: break

        if tents is None or trees is None:
            raise RuntimeError("< Impossible to generate a board with input data >")


        self.correct_tents = sorted(tents)
        self.trees = sorted(trees)

        # -> obbliga il ricalcolo di __columns_targets e di __rows_targets
        self.reset_targets()

    def is_valid_board(self, trees: Collection[tuple[int, int]] | None = None,
                       tents: Collection[tuple[int, int]] | None = None) -> bool:
        """
            Controlla se una configurazione (alberi + tende) rispetta i vincoli base del gioco.

            Qui NON controlla i target di righe/colonne (quello lo fa finished()).
            Qui controlla:
            - tutto dentro la board
            - tende non adiacenti in n8
            - ogni tenda ha almeno un albero vicino in n4
        """
        tents = set(self.correct_tents) if tents is None else set(tents)
        trees = set(self.trees) if trees is None else set(trees)

        # -> alberi dentro
        for tx, ty in trees:
            if not self.inside(tx, ty):
                return False

        for x, y in tents:
            # -> tende dentro
            if not self.inside(x, y):
                return False

            # -> tende non adiacenti (n8)
            for nx, ny in self.n8(x, y):
                if (nx, ny) != (x, y) and (nx, ny) in tents:
                    return False

            # -> ogni tenda deve poter prendere 1 albero
            tree_found = False
            for nx, ny in self.n4(x, y):
                if (nx, ny) in trees:
                    tree_found = True
                    break
            if not tree_found:
                return False

        if len(self.trees) != len(trees):
            return False

        return True

    @staticmethod
    def _is_lateral_adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
        """True se a e b sono adiacenti in modo ortogonale (distanza == 1)."""
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by) == 1

    def _is_free(self, x: int, y: int) -> bool:
        """True se la cella è EMPTY, cioè non contiene ne albero, ne tenda, ne prato."""
        pos = (x, y)
        return pos not in self.trees and pos not in self.tents and pos not in self.grass

    def _free_cells(self):
        """Ritorna la lista di tutte le celle attualmente libere"""
        result = []
        for y in range(self.lines):
            for x in range(self.columns):
                if self._is_free(x, y):
                    result.append((x, y))
        return result

    def _mark_grass(self, x: int, y: int) -> bool:
        if self._is_free(x, y):
            self.grass.add((x, y))
            return True
        return False

    def _mark_tent(self, x: int, y: int) -> bool:
        if self._can_place_tent(x, y):
            self.tents.add((x, y))
            return True
        return False

    def reset_targets(self):
        """
            Forza il ricalcolo dei target di righe/colonne.

            Serve quando cambia la soluzione (per esempio dopo generate_board): i target sono calcolati
            "lazy" e memorizzati come attributi privati, si evita di ricalcolarli se esiste già l'attributo.
            Per questo va eliminato l'attributo per ricalcolarli.
        """
        if hasattr(self, f'_{self.__class__.__name__}__columns_targets'):
            delattr(self, f'_{self.__class__.__name__}__columns_targets')
        if hasattr(self, f'_{self.__class__.__name__}__rows_targets'):
            delattr(self, f'_{self.__class__.__name__}__rows_targets')


    # ======== AUTOMATISMI ========
    def _forced_assignments(self) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        """
        Cerca abbinamenti obbligati albero-tenda basandosi su quello che è già piazzato.

        Alcune tende/alberi diventano "forzati" quando non ci sono alternative:
        - se una tenda ha un solo albero adiacente, quell’albero deve essere suo
        - se un albero ha una sola tenda adiacente e nessuna cella libera attorno, quell’abbinamento è bloccato

        Ritorna:
          - forced_trees: alberi che risultano assegnati in modo forzato
          - forced_tents: tende che risultano assegnate in modo forzato
        """
        remaining_trees = set(self.trees or ())
        remaining_tents = set(self.tents or ())
        forced_pairs: set[tuple[tuple[int, int], tuple[int, int]]] = set()

        changed = True
        while changed:
            changed = False

            # -> regola A: tenda con un solo albero adiacente
            tents_to_remove: set[tuple[int, int]] = set()
            trees_to_remove: set[tuple[int, int]] = set()

            for tent in remaining_tents:
                adjacent_trees = {tree for tree in remaining_trees if self._is_lateral_adjacent(tent, tree)}
                if len(adjacent_trees) == 1:
                    (tree,) = tuple(adjacent_trees)
                    forced_pairs.add((tree, tent))
                    tents_to_remove.add(tent)
                    trees_to_remove.add(tree)
                    changed = True

            remaining_tents -= tents_to_remove
            remaining_trees -= trees_to_remove

            # -> regola B: albero con una sola tenda adiacente e nessuna cella libera attorno
            tents_to_remove = set()
            trees_to_remove = set()

            for tree in remaining_trees:
                adjacent_tents = {tent for tent in remaining_tents if self._is_lateral_adjacent(tree, tent)}
                adjacent_free_cells = {cell for cell in self.n4(*tree) if self._is_free(*cell)}

                if len(adjacent_tents) == 1 and len(adjacent_free_cells) == 0:
                    (tent,) = tuple(adjacent_tents)
                    forced_pairs.add((tree, tent))
                    trees_to_remove.add(tree)
                    tents_to_remove.add(tent)
                    changed = True

            remaining_trees -= trees_to_remove
            remaining_tents -= tents_to_remove

        forced_trees = {tree for (tree, _tent) in forced_pairs}
        forced_tents = {_tent for (_tree, _tent) in forced_pairs}
        return forced_trees, forced_tents

    def _tents_in_row(self, y: int) -> int:
        return sum((x, y) in self.tents for x in range(self.columns))

    def _tents_in_col(self, x: int) -> int:
        return sum((x, y) in self.tents for y in range(self.lines))

    def _can_place_tent(self, x: int, y: int) -> bool:
        if not self._is_free(x, y):
            return False
        # -> niente tende adiacenti (n8)
        if any((nx, ny) in self.tents for (nx, ny) in self.n8(x, y)):
            return False
        # -> deve essere adiacente a un albero
        if not any((nx, ny) in self.trees for (nx, ny) in self.n4(x, y)):
            return False
        # -> non superare i target
        if self._tents_in_row(y) >= self.rows_targets[y]:
            return False
        if self._tents_in_col(x) >= self.columns_targets[x]:
            return False
        return True

    def _auto_grass(self) -> None:
        """
            Applica regole per piazzare prato dove è d'obbligo che non possa esserci una tenda.

            Regole:
            - riga/colonna: se target di tende raggiunto, tutto il resto libero è prato
            - tutte le celle in n8 attorno a una tenda devono essere prato
            - se una cella non è adiacente (n4) ad alcun albero non assegnato, allora non potrà mai essere tenda -> prato
        """
        changed = True
        while changed:
            changed = False

            # -> righe: se target raggiunto, il resto libero è prato
            for y in range(self.lines):
                if self._tents_in_row(y) == self.rows_targets[y]:
                    for x in range(self.columns):
                        if self._mark_grass(x, y):
                            changed = True

            # -> colonne: se target raggiunto, il resto libero è prato
            for x in range(self.columns):
                if self._tents_in_col(x) == self.columns_targets[x]:
                    for y in range(self.lines):
                        if self._mark_grass(x, y):
                            changed = True

            # -> celle libere adiacenti (n8) a una tenda -> prato
            for x, y in list(self._free_cells()):
                if any((nx, ny) in self.tents for (nx, ny) in self.n8(x, y)):
                    if self._mark_grass(x, y):
                        changed = True

            # -> celle libere NON adiacenti (n4) a un albero non ancora assegnato -> prato
            forced_trees, _ = self._forced_assignments()
            unassigned_trees = set(self.trees) - forced_trees

            for x, y in list(self._free_cells()):
                if not any(nei in unassigned_trees for nei in self.n4(x, y)):
                    if self._mark_grass(x, y):
                        changed = True

    def _auto_tents(self) -> None:
        """
            Applica regole per piazzare tende obbligate.

            Regole:
            - riga/colonna: se (tende già messe + celle libere) == target, allora tutte le libere devono diventare tende
            - per ogni albero: se non ha ancora una tenda e ha una sola cella libera adiacente (n4), quella cella deve essere tenda
        """
        changed = True
        while changed:
            changed = False

            # -> righe: se tutte le celle vuote rimanenti raggiungono il target DEVONO essere tende
            for y in range(self.lines):
                placed = [(x, y) for x in range(self.columns) if (x, y) in self.tents]
                free = [(x, y) for x in range(self.columns) if self._is_free(x, y)]

                if len(placed) + len(free) == self.rows_targets[y]:
                    for x, y_ in free:
                        if self._mark_tent(x, y_):
                            changed = True

            # -> colonne: se tutte le celle vuote rimanenti raggiungono il target DEVONO essere tende
            for x in range(self.columns):
                placed = [(x, y) for y in range(self.lines) if (x, y) in self.tents]
                free = [(x, y) for y in range(self.lines) if self._is_free(x, y)]

                if len(placed) + len(free) == self.columns_targets[x]:
                    for xx, y in free:
                        if self._mark_tent(xx, y):
                            changed = True

            # -> per ogni albero: se non ha tende attorno e ha UNA sola cella libera adiacente -> tenda
            for ax, ay in self.trees:
                if any(self._is_lateral_adjacent((ax, ay), tent) for tent in self.tents):
                    continue

                adjacent_free = [cell for cell in self.n4(ax, ay) if self._is_free(*cell)]
                if len(adjacent_free) == 1:
                    tx, ty = adjacent_free[0]
                    if self._mark_tent(tx, ty):
                        changed = True

    # ======== PROPERTIES ========
    @property
    def board(self) -> list[list[CellState]]:
        cols, rows = self.columns, self.lines
        board: list[list[CellState]] = [[CellState.EMPTY for _ in range(cols)] for _ in range(rows)]
        for x, y in self.trees:
            board[y][x] = CellState.TREE
        for x, y in self.tents:
            board[y][x] = CellState.TENT
        for x, y in self.grass:
            board[y][x] = CellState.GRASS
        return board

    @property
    def columns_targets(self) -> list[int]:
        if not hasattr(self, f'_{self.__class__.__name__}__columns_targets'):
            cols, rows = self.columns, self.lines
            tents = self.correct_tents
            self.__columns_targets = [
                sum((x, y) in tents for y in range(rows))
                for x in range(cols)
            ]
        return self.__columns_targets
    @columns_targets.setter
    def columns_targets(self, new: list[int]) -> None:
        if new is None:
            return
        if not isinstance(new, list):
            raise TypeError("< columns_targets must be list >")
        if not all(isinstance(_, int) for _ in new):
            raise TypeError("< columns_targets must be list of ints >")
        if len(new) != self.columns:
            raise ValueError("< columns_targets must have the same length as columns >")
        self.__columns_targets: list[int] = new

    @property
    def rows_targets(self) -> list[int]:
        if not hasattr(self, f'_{self.__class__.__name__}__rows_targets'):
            cols, rows = self.columns, self.lines
            tents = self.correct_tents
            self.__rows_targets = [
                sum((x, y) in tents for x in range(cols))
                for y in range(rows)
            ]
        return self.__rows_targets
    @rows_targets.setter
    def rows_targets(self, new: list[int]) -> None:
        if new is None:
            return
        if not isinstance(new, list):
            raise TypeError("< rows_targets must be list >")
        if not all(isinstance(_, int) for _ in new):
            raise TypeError("< rows_targets must be list of ints >")
        if len(new) != self.lines:
            raise ValueError("< rows_targets must have the same length as lines >")
        self.__rows_targets: list[int] = new

    @property
    def solution_board(self) -> list[list[CellState]]:
        cols, rows = self.columns, self.lines
        board: list[list[CellState]] = [[CellState.GRASS for _ in range(cols)] for _ in range(rows)]
        for x, y in self.trees:
            board[y][x] = CellState.TREE
        for x, y in self.correct_tents:
            board[y][x] = CellState.TENT
        return board

    @property
    def columns(self) -> int:
        return self.__columns
    @columns.setter
    def columns(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError("< columns must be int >")
        self.__columns = new

    @property
    def lines(self) -> int:
        return self.__lines
    @lines.setter
    def lines(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError("< rows must be int >")
        self.__lines = new

    @property
    def trees(self) -> set[tuple[int, int]] | None:
        return self.__trees
    @trees.setter
    def trees(self, new: Collection[tuple[int, int]] | None) -> None:
        if new is not None:
            for t in new:
                if len(t) != 2:
                    raise ValueError("< trees must be tuples of length 2 >")
                x, y = t
                if x not in range(self.columns) or y not in range(self.lines):
                    raise ValueError(f"< trees contains coordinates outside the board: ({x}, {y}) >")
        self.__trees = None if new is None else set(new)

    @property
    def correct_tents(self) -> set[tuple[int, int]] | None:
        return self.__correct_tents
    @correct_tents.setter
    def correct_tents(self, new: Collection[tuple[int, int]] | None) -> None:
        if new is not None:
            for t in new:
                if not isinstance(t, tuple):
                    raise TypeError("< correct_tents must be tuples >")
                if len(t) != 2:
                    raise ValueError("< correct_tents must be tuples of length 2 >")
                x, y = t
                if x not in range(self.columns) or y not in range(self.lines):
                    raise ValueError(f"< correct_tents contains coordinates outside the board: ({x}, {y}) >")
        self.__correct_tents = None if new is None else set(new)

    @property
    def tents(self) -> set[tuple[int, int]] | None:
        return self.__tents
    @tents.setter
    def tents(self, new: Collection[tuple[int, int]] | None) -> None:
        if new is not None:
            for t in new:
                if not isinstance(t, tuple):
                    raise TypeError("< tents must be tuples >")
                if len(t) != 2:
                    raise ValueError("< tents must be tuples of length 2 >")
                x, y = t
                if x not in range(self.columns) or y not in range(self.lines):
                    raise ValueError(f"< tents contains coordinates outside the board: ({x}, {y}) >")
        self.__tents = None if new is None else set(new)

    @property
    def grass(self) -> set[tuple[int, int]] | None:
        return self.__grass
    @grass.setter
    def grass(self, new: Collection[tuple[int, int]] | None) -> None:
        if new is not None:
            for t in new:
                if not isinstance(t, tuple):
                    raise TypeError("< grass must be tuples >")
                if len(t) != 2:
                    raise ValueError("< grass must be tuples of length 2 >")
                x, y = t
                if x not in range(self.columns) or y not in range(self.lines):
                    raise ValueError(f"< grass contains coordinates outside the board: ({x}, {y}) >")
        self.__grass = None if new is None else set(new)

    # ======== CLASSMETHODS ========
    @classmethod
    def init_from_level(cls, level) -> "Game":
        """
            Crea un Game partendo da un Level già parsato.

            Copia dimensioni, alberi, soluzione e target dal livello.
            È il modo "standard" per caricare un livello da file e giocarlo.
        """
        game = cls(
            columns=level.columns,
            rows=level.lines,
            trees=set(level.trees),
            tents=set(level.correct_tents),
            columns_targets=level.columns_targets,
            rows_targets=level.rows_targets
        )
        return game
