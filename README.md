# TOHLCV Wiki – przewodnik redakcyjny

Repozytorium przechowuje statyczną stronę wiki o algotradingu, której zawartość w całości pochodzi z plików JSON. Po ostatniej przebudowie jedynym językiem serwisu jest polski, co ułatwia dodawanie nowych elementów.

## Kluczowe pliki

| Ścieżka | Rola |
| --- | --- |
| `site_config.json` | Konfiguracja witryny: tytuły, komunikaty, kolejność sekcji. |
| `site_objects.json` | Słownik obiektów budujących stronę (tematy, kategorie, definicje). |
| `generate.py` | Skrypt renderujący stronę `index.html` na podstawie danych z JSON. |
| `styles/main.css` | Wspólny arkusz stylów dla wygenerowanej strony. |
| `dashboard/` | Prosty panel WWW do edycji obiektów i pobierania nowej wersji `site_objects.json`. |
| `index.html` | Wygenerowany rezultat – aktualna strona wiki w języku polskim. |

## Konfiguracja strony (`site_config.json`)

Plik zawiera ustawienia globalne. Najważniejsze pola:

- `language` – kod języka renderowanej strony (`"pl"`).
- `site_title` – tytuł wyświetlany w nagłówku i tagu `<title>`.
- `site_subtitle` – opcjonalny podtytuł (można wykorzystać we własnych sekcjach HTML).
- `index_content` – blok HTML umieszczany w sekcji startowej.
- `labels` – słownik etykiet używanych w nawigacji, stopce i komentarzach generowanych w glosariuszu:
  - `code` – prefiks dla wierszy typu „Kod w systemie”.
  - `comments.section` i `comments.definition` – podpisy komentarzy otwierających/zamykających sekcje glosariusza.
  - `navigation.home` – tekst linku prowadzącego do sekcji startowej.
  - `footer` – treść stopki.
- `pages` – uporządkowana lista sekcji pojawiających się na stronie. Każdy wpis ma:
  - `slug` – identyfikator używany jako `id` sekcji.
  - `topic` – odwołanie do obiektu `topics` w `site_objects.json`. Jeśli `topic` nie zostanie podany, generator użyje wartości `slug`.

## Obiekty treści (`site_objects.json`)

Plik dzieli się na trzy tablice:

1. **`topics`** – opisują sekcje strony.
    - `id` – unikalny identyfikator.
    - `title` – tytuł sekcji.
    - `type` – `"standard"` (domyślnie) lub `"glossary"` (sekcja glosariusza).
    - `content` – fragment HTML wstawiany do sekcji.
    - `categories` – tylko dla glosariusza: lista identyfikatorów kategorii, które mają zostać wyrenderowane poniżej treści.

2. **`categories`** – grupują definicje w glosariuszu.
    - `id` – identyfikator kategorii.
    - `title` – nagłówek wyświetlany na stronie.
    - `definition_ids` – uporządkowana lista definicji przypisanych do kategorii.

3. **`definitions`** – pojedyncze hasła słownikowe.
    - `id` – identyfikator używany w odnośnikach.
    - `label` – nazwa wyświetlana w glosariuszu.
    - `description` – treść (HTML). Można używać prostych znaczników i list.
    - `code` – (opcjonalnie) dodatkowy opis kodowy, pojawia się pod treścią.
    - `tags` – tablica hashtagów bez znaku `#`. Generator tworzy z nich indeks tagów na końcu strony.

> **Powiązania:** Tematy typu glosariusz wskazują kategorie, a kategorie decydują o kolejności definicji. Każdy nowy hashtag dodany do definicji automatycznie trafia do sekcji „Tagi”.

## Dashboard do edycji (`dashboard/index.html`)

W katalogu `dashboard/` znajduje się prosty panel napisany w czystym HTML/JS:

1. Uruchom lokalny serwer, np. `python -m http.server 8000` z katalogu głównego repo.
2. Wejdź na adres `http://localhost:8000/dashboard/`.
3. Panel wczyta `site_objects.json`, policzy obiekty i pozwoli:
   - dodać nowy temat (w tym sekcję glosariusza),
   - utworzyć definicję wraz z przypisaniem jej do istniejących lub nowych kategorii,
   - dopisać hashtag do wybranej definicji,
   - pobrać zaktualizowany plik `site_objects.json` (przycisk „Pobierz”).
4. Po pobraniu nadpisz plik w repozytorium i uruchom generator HTML.

Panel nie zapisuje zmian na dysku – to narzędzie pomocnicze do przygotowania poprawnego JSON-a.

## Generowanie strony

1. Upewnij się, że `site_config.json` i `site_objects.json` zawierają pożądane dane.
2. Uruchom:

   ```bash
   python generate.py
   ```

   Skrypt nadpisze plik `index.html` najnowszą wersją strony.

3. Zatwierdź zmiany w repozytorium.

## Rekomendowany workflow

1. Edytuj treść w `dashboard/` (lub ręcznie w JSON-ach).
2. Pobierz i podmień `site_objects.json`.
3. W razie potrzeby zaktualizuj `site_config.json` (np. kolejność sekcji).
4. Wygeneruj `index.html` poleceniem `python generate.py`.
5. Sprawdź stronę lokalnie (`python -m http.server`).
6. Commit i push.

Dzięki ograniczeniu do jednego języka możesz skupić się na tworzeniu treści, a w przyszłości ponownie włączyć wielojęzyczność, przywracając pola tłumaczeń do JSON-ów oraz odpowiednie fragmenty w `generate.py`.
