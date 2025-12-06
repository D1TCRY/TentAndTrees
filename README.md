# TentsAndTrees

Progetto universitario (1° anno) — Ingegneria delle Tecnologie Informatiche, Università di Parma.

**Autore:** Diego Cecchelani  
**Matricola:** 386276

---

## Indice

- [Descrizione](#descrizione)
- [Features](#features-principali)
- [Struttura](#struttura-del-progetto)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Avvio](#avvio)
- [Eseguire i test](#eseguire-i-test)
- [Come si gioca](#come-si-gioca-controlli)
- [Formato dei livelli](#formato-dei-livelli-datalevelstxt)
- [Configurazione](#configurazione-datasettingsjson)
- [Architettura](#architettura-overview-rapida)
- [Troubleshooting](#troubleshooting)
- [Licenza e note](#licenza-e-note)
- [Autore](#autore)

---

## Descrizione

**TentsAndTrees** è un videogioco/puzzle ispirato al classico *Tents and Trees*.

Obiettivo: posizionare tutte le **tende (⛺)** sulla griglia rispettando i vincoli:
- ogni tenda deve essere **adiacente ortogonalmente (N4)** a **un albero (🌳)**;
- ogni albero deve avere **esattamente una** tenda associata;
- **nessuna tenda può toccare un’altra tenda**, nemmeno in diagonale (N8);
- i numeri su **righe** e **colonne** indicano quante tende devono comparire in quella riga/colonna.

Il progetto supporta:
- livelli predefiniti caricati da file;
- generazione casuale di una board valida;
- una GUI con griglia, indicatori di riga/colonna e barra di stato.

---

## Features principali

- **Menu livelli (Tkinter)**:
  - selezione livello da file
  - modalità **Random** (generazione)
  - uscita dal programma
- **Gioco con GUI (g2d)**:
  - click sinistro per interagire con la cella (toggle tenda → prato → vuoto, con vincoli sugli alberi)
  - automazioni per piazzamenti “forzati”
  - visualizzazione soluzione (se disponibile nel livello)
- **Board generator**:
  - genera una configurazione valida di tende (non adiacenti in N8)
  - assegna 1 albero per ogni tenda (adiacenza N4)
  - calcola automaticamente i target di righe/colonne

---

## Struttura del progetto

```
└── TentsAndTrees/
    ├── req.txt
    ├── run.bat
    ├── run.vbs
    ├── test.bat
    ├── src/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── data/
    │   │   ├── settings.json
    │   │   └── levels/
    │   │       ├── tents-2025-11-27-8x8-easy.txt
    │   │       ├── tents-2025-11-27-8x8-medium.txt
    │   │       ├── tents-2025-11-27-12x12-easy.txt
    │   │       ├── tents-2025-11-27-12x12-medium.txt
    │   │       ├── tents-2025-11-27-16x16-easy.txt
    │   │       ├── tents-2025-11-27-16x16-medium.txt
    │   │       └── tents-2025-11-27-20x20-special.txt
    │   ├── g2d_lib/
    │   │   ├── __init__.py
    │   │   ├── g2d.py
    │   │   └── oog2d.py
    │   └── game/
    │       ├── __init__.py
    │       ├── board_game.py
    │       ├── board_game_gui.py
    │       ├── core/
    │       │   ├── __init__.py
    │       │   ├── app.py
    │       │   ├── file_management.py
    │       │   ├── game.py
    │       │   ├── level.py
    │       │   ├── menu_manager.py
    │       │   └── menu_window.py
    │       ├── gui/
    │       │   ├── __init__.py
    │       │   ├── bar.py
    │       │   ├── board.py
    │       │   ├── button.py
    │       │   ├── cell.py
    │       │   ├── color.py
    │       │   ├── gui_component.py
    │       │   └── text.py
    │       └── state/
    │           ├── __init__.py
    │           ├── action.py
    │           ├── app_phase.py
    │           ├── cell_state.py
    │           └── menu_phase.py
    └── tests/
        └── game/
            ├── __init__.py
            ├── test_board_game_gui.py
            ├── core/
            │   ├── __init__.py
            │   ├── test_app.py
            │   ├── test_game.py
            │   ├── test_level.py
            │   ├── test_menu_manager.py
            │   └── test_menu_window.py
            └── gui/
                ├── __init__.py
                ├── test_board.py
                └── test_cell.py
```

---

## Requisiti

- Python 3.10+ (consigliato 3.11)
- Dipendenze:
  - **Tkinter** (di solito incluso con Python nelle installazioni standard)
  - Libreria **g2d** (inclusa nel progetto in `src/g2d_lib/`)

> Nota: se su Linux manca Tkinter, potrebbe essere necessario installare il pacchetto di sistema (es. `python3-tk`).

---

## Installazione

1. Clona o scarica il progetto.
2. Posizionati nella root del repository.
3. (Opzionale ma consigliato) Crea un virtual environment:

```bash
python -m venv env
```

4. Avvia il gioco (vedi sezione successiva).

---

## Avvio
Se hai l'ambiente virtuale `env` puoi semplicemente eseguire il file `run.bat` o `run.vbs` per eseguire il programma.

In alternativa, puoi eseguire questo comando:
```bash
python -m src.main
```

dopo aver impostato come working-directory la cartella root del progetto:
```bash
cd path/to/TentsAndTrees/
```

> Se ricevi errori di import, assicurati di eseguire il comando dalla **root** del progetto e di star eseguendo il modulo **src.main**.

---

## Come si gioca (controlli)

Nel menu (finestra Tkinter):
- clicca un livello per iniziare
- **Random**: genera un livello casuale
- **Quit**: chiude il programma

In gioco (canvas g2d):
- **Click sinistro** su una cella:
  - se la cella è vuota: piazza una tenda (se consentito)
  - se c’è una tenda: diventa prato
  - se c’è prato: torna vuota
  - sugli alberi non si piazza nulla
- **t**: piazza automaticamente tende “forzate”
- **g**: piazza automaticamente prato “forzato”
- **s**: mostra la soluzione (solo per livelli che la includono)
- **Esc**: torna al menu

---

## Formato dei livelli (`data/levels/*.txt`)

I livelli sono file di testo strutturati così:

- **prima riga (header)**: un carattere qualsiasi + una sequenza di target colonna  
  - `.` significa 0
  - cifre (`0-9`) → valore numerico
- **righe successive**: ogni riga inizia col target di riga, poi la griglia
  - `.` = cella vuota
  - `T` = albero
  - `^` = tenda (soluzione)

Esempio (illustrativo):

```text
.2001
1T..^
1^..T
0....
1^T..
```

---

## Configurazione (`data/settings.json`)

Nel file `settings.json` puoi personalizzare:
- **fps**, **scale**, **size**
- stile per ogni `CellState` (`EMPTY`, `TREE`, `TENT`, `GRASS`, `OUT`):
  - `text` (emoji o carattere)
  - `background_color`, `hover_color`, `pressed_color`
- impostazioni GUI:
  - dimensioni `menu_window`
  - layout e colori di `board_game_gui`

---

## Architettura (overview rapida)

- `App` gestisce lo **stato dell’applicazione** (`AppPhase`) e coordina:
  - `MenuManager` (apertura menu Tkinter e scelta livello)
  - `Game` (logica puzzle)
  - `BoardGameGui` (rendering + input su canvas g2d)
- `Game` implementa l’interfaccia `BoardGame`:
  - reading delle celle (`read`)
  - gioco/azioni (`play`)
  - condizione di vittoria (`finished`)
  - stato testuale (`status`)
  - generazione e validazione board (`generate_board`, `is_valid_board`)

---

## Eseguire i test

I test sono eseguibili dalla **root** del progetto (come per l’avvio del programma).

### Windows

Se sei su Windows puoi eseguire direttamente il file `test.bat` usare direttamente:

```bat
test.bat
```

### Comando manuale

In alternativa, dalla root del repository esegui:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

> Nota: assicurati di lanciare il comando dalla cartella **TentsAndTrees/**, altrimenti `unittest` potrebbe non trovare correttamente i moduli e i test.


---

## Troubleshooting

### Emoji non visibili / quadratini
Dipende dal font/sistema. Puoi sostituire le emoji in `settings.json` con caratteri ASCII (es. `T`, `^`, `g`).

### Problemi di import
Esegui i comandi dalla root (TentsAndTrees\) e preferisci:

```bash
python -m src.main
```

### Tkinter non trovato (Linux)
```bash
sudo apt-get install python3-tk
```

---

## Licenza e note

Questo progetto è stato realizzato a scopo didattico.  

---

## Autore

Diego Cecchelani — Matricola 386276  
Ingegneria delle Tecnologie Informatiche, Università di Parma


Aggiungi questa sezione al README (va bene metterla dopo **Avvio** o prima di **Troubleshooting**):

---

