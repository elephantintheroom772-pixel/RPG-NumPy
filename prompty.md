# System porównywania postaci RPG z NumPy

## Cel projektu

Celem zadania było przekształcenie początkowego programu Python, wykorzystującego listy i pętle, w analizator postaci RPG oparty na bibliotece NumPy.

Pracę wykonano etapami, korzystając z kolejnych promptów do ChatGPT. Każdy etap wprowadzał nowe funkcje i testy.

## Prompty wykorzystane podczas pracy

### Prompt 1 — Plan przebudowy programu

Przeanalizuj kod początkowy programu porównującego postacie RPG. Zaproponuj plan przebudowy z wykorzystaniem biblioteki NumPy.

Zachowaj wszystkich 8 bohaterów i ich statystyki. Przygotuj strukturę danych `NAZWY`, `STATYSTYKI`, `WAGI` i `KOLUMNY`. Na tym etapie nie twórz jeszcze kompletnego programu.

**Cel:** Zaplanowanie przejścia z list i pętli na tablice NumPy.

### Prompt 2 — Walidacja i normalizacja

Dodaj funkcję `waliduj`, która sprawdza liczbę postaci, unikatowość nazw, cztery kolumny statystyk oraz poprawność wartości liczbowych.

Dodaj funkcję `normalizuj`, wykorzystującą normalizację min-max. Jeżeli wszystkie wartości w kolumnie są jednakowe, wynik dla tej kolumny powinien wynosić zero.

Przygotuj testy poprawnych i niepoprawnych danych oraz stałej kolumny.

**Cel:** Zapewnienie poprawności danych i bezpiecznej normalizacji.

### Prompt 3 — Obliczanie siły

Dodaj funkcję `oblicz_sile`, która oblicza siłę każdej postaci za pomocą NumPy, normalizacji oraz wag.

Wykorzystaj działanie `normalizuj(dane) @ WAGI`.

Przygotuj test sprawdzający wyniki dla prostych, znanych danych.

**Cel:** Zastąpienie obliczeń wykonywanych w pętlach operacjami wektorowymi.

### Prompt 4 — Role i ranking

Dodaj funkcję `okresl_role`, która przypisuje postaciom role:

- `Szturmowiec`: atak co najmniej 35 i szybkość co najmniej 12.
- `Obrońca`: HP co najmniej 120 i obrona co najmniej 18.
- `Wszechstronny`: pozostałe postacie.

Dodaj ranking malejąco według siły z zachowaniem kolejności postaci przy remisie. Przygotuj testy.

**Cel:** Automatyczne przypisywanie ról i tworzenie stabilnego rankingu.

### Prompt 5 — Macierz pojedynków

Dodaj funkcję `macierz_pojedynkow`, która wyznacza prawdopodobieństwo zwycięstwa każdej postaci nad pozostałymi.

Zastosuj wzór logistyczny `1 / (1 + exp(-8 * różnica_siły))`.

Na przekątnej macierzy powinno znajdować się `0.5`. Sprawdź testami, czy `P(i,j) + P(j,i) = 1`.

**Cel:** Obliczanie szans zwycięstwa w pojedynkach.

### Prompt 6 — Średnie szanse i eksport CSV

Dodaj funkcję `oblicz_srednie_szanse`, obliczającą średnie prawdopodobieństwo zwycięstwa nad pozostałymi postaciami, bez uwzględniania pojedynku z samym sobą.

Dodaj funkcję `zapisz_csv`, która zapisuje ranking do pliku CSV z kodowaniem `utf-8-sig` i separatorem `;`.

Uwzględnij kolumny: miejsce, postać, rola, siła i średnia szansa wygranej. Dodaj testy.

**Cel:** Podsumowanie wyników pojedynków i eksport raportu.

### Prompt 7 — Połączenie programu

Połącz wszystkie dotychczasowe elementy w jeden kompletny, działający program Python.

Zachowaj wszystkich 8 bohaterów, ich statystyki oraz wcześniej utworzone funkcje i testy.

W funkcji `main()`:

1. Uruchom walidację i testy.
2. Oblicz siłę, role, ranking, macierz pojedynków i średnie szanse.
3. Wyświetl ranking z siłą do 3 miejsc po przecinku i szansą do 1 miejsca procentowego.
4. Wyświetl postacie spełniające warunki: HP >= 100, szybkość >= 10, siła >= 0.45. Jeśli żadna nie spełnia warunków, wyświetl `Brak`.
5. Wyświetl minimum, średnią i maksimum każdej statystyki.
6. Zapisz raport do `raport_postaci.csv`.

Dodaj `if __name__ == "__main__": main()`.

**Cel:** Integracja funkcji w kompletną aplikację.

## Wyniki przeprowadzonych testów

| Wymaganie | Wynik | Dowód |
|---|---|---|
| Uruchomienie programu | Działa | Program uruchomiony w Python 3.13.16 |
| Walidacja i testy | Działa | `Wszystkie testy: OK` |
| Ranking 8 postaci | Działa | Pierwsze miejsce: Berserker, siła 0.535 |
| Przypisywanie ról | Działa | Wyświetlono role wszystkich 8 postaci |
| Średnie szanse wygranej | Działa | Berserker: 64.0% |
| Filtrowanie postaci | Działa | Wynik: Berserker |
| Statystyki grupy | Działa | Wyświetlono min, średnią i max |
| Eksport CSV | Działa | Utworzono `raport_postaci.csv` |
| Kodowanie i separator CSV | Działa | Sprawdzono nagłówek z separatorem `;` |
| Walidacja unikatowości nazw | Działa | Powtórzenie nazwy `Mag` powoduje `ValueError` |
| Obsługa pustej tablicy | Działa po korekcie | `ValueError` z czytelnym komunikatem |

## Korekty promptów

### Korekta 1 — Obsługa pustych danych

**Wykryty problem:** Funkcja `normalizuj()` przy pustej tablicy `np.empty((0, 4))` zgłaszała techniczny błąd NumPy: `zero-size array to reduction operation minimum which has no identity`.

**Prompt korygujący:**

Popraw funkcję `normalizuj`, aby przed normalizacją sprawdzała, czy tablica jest dwuwymiarowa, zawiera co najmniej jeden wiersz i dokładnie cztery kolumny. W przypadku niepoprawnych danych zgłoś czytelny wyjątek `ValueError`. Zachowaj dotychczasowe działanie normalizacji min-max.

**Wprowadzona poprawka:** Dodano sprawdzenie kształtu tablicy przed obliczeniem minimum.

**Wynik testu:** Po przekazaniu `np.empty((0, 4))` program zgłasza `ValueError: Dane muszą zawierać co najmniej jedną postać i 4 statystyki.` — test zaliczony.

### Korekta 2 — Walidacja macierzy prawdopodobieństw

**Wykryty problem:** Funkcja `oblicz_srednie_szanse()` przyjmowała niepoprawną macierz `np.ones((2, 2))` i zwracała wynik `[1.5, 1.5]`, czyli niemożliwe prawdopodobieństwo 150%.

**Prompt korygujący:**

Popraw funkcję `oblicz_srednie_szanse`, aby sprawdzała poprawność macierzy pojedynków przed obliczeniem średnich szans. Macierz musi być kwadratowa, zawierać co najmniej dwie postacie, mieć wartości od 0 do 1, przekątną równą 0.5 oraz spełniać warunek `P(i,j) + P(j,i) = 1`. Dla niepoprawnych danych zgłaszaj `ValueError`.

**Wprowadzona poprawka:** Dodano walidację macierzy prawdopodobieństw.

**Wynik testu:** Dla `np.ones((2, 2))` program zgłasza `ValueError: Na przekątnej macierzy musi być 0.5.` — test zaliczony.

**Test końcowy:** Po obu poprawkach uruchomiono `analizator_rpg.py`. Wynik: `Wszystkie testy: OK`, ranking 8 postaci oraz poprawnie wygenerowany plik `raport_postaci.csv`.

## Pliki projektu

- `analizator_rpg.py` — kompletny program Python.
- `raport_postaci.csv` — wygenerowany raport.
- `prompty.md` — dokumentacja promptów i testów.
