"""Wektorowy analizator balansu postaci RPG z NumPy."""
import csv
import numpy as np

NAZWY = np.array(["Wojownik", "Mag", "Łucznik", "Paladyn", "Łotrzyk",
                  "Berserker", "Druid", "Strażnik"])
STATYSTYKI = np.array([
    [120, 28, 18, 9], [75, 44, 6, 13], [95, 34, 10, 17],
    [140, 25, 22, 7], [80, 39, 8, 21], [110, 42, 7, 12],
    [105, 26, 15, 14], [155, 18, 26, 5]
], dtype=float)
WAGI = np.array([0.20, 0.40, 0.25, 0.15])
KOLUMNY = ("HP", "Atak", "Obrona", "Szybkość")


def waliduj(nazwy, dane):
    nazwy, dane = np.asarray(nazwy), np.asarray(dane)
    if nazwy.ndim != 1 or len(nazwy) < 2:
        raise ValueError("Potrzeba co najmniej dwóch nazw postaci.")
    if dane.ndim != 2 or dane.shape != (len(nazwy), 4):
        raise ValueError("Każda postać musi mieć dokładnie 4 statystyki.")
    if len(np.unique(nazwy)) != len(nazwy):
        raise ValueError("Nazwy postaci muszą być unikatowe.")
    try:
        liczby = dane.astype(float)
    except (ValueError, TypeError, OverflowError) as blad:
        raise ValueError("Statystyki muszą być liczbami.") from blad
    if not np.all(np.isfinite(liczby)) or np.any(liczby < 0):
        raise ValueError("Statystyki muszą być nieujemnymi, skończonymi liczbami.")
    return True


def normalizuj(dane):
    dane = np.asarray(dane, dtype=float)

    if dane.ndim != 2 or dane.shape[0] == 0 or dane.shape[1] != 4:
        raise ValueError("Dane muszą zawierać co najmniej jedną postać i 4 statystyki.")

    minimum = np.min(dane, axis=0)
    rozpietosc = np.ptp(dane, axis=0)

    return np.divide(dane - minimum, rozpietosc,
                     out=np.zeros_like(dane, dtype=float),
                     where=rozpietosc != 0)


def oblicz_sile(dane):
    return normalizuj(dane) @ WAGI


def okresl_role(dane):
    ofensywa = (dane[:, 1] >= 35) & (dane[:, 3] >= 12)
    obrona = (dane[:, 0] >= 120) & (dane[:, 2] >= 18)
    return np.select([ofensywa, obrona], ["Szturmowiec", "Obrońca"],
                     default="Wszechstronny")


def sortuj_ranking(sila):
    return np.argsort(-sila, kind="stable")


def macierz_pojedynkow(sila):
    roznice = sila[:, None] - sila[None, :]
    wynik = 1 / (1 + np.exp(-8 * roznice))
    np.fill_diagonal(wynik, 0.5)
    return wynik


def oblicz_srednie_szanse(pojedynki):
    pojedynki = np.asarray(pojedynki, dtype=float)

    if (pojedynki.ndim != 2
            or pojedynki.shape[0] != pojedynki.shape[1]
            or len(pojedynki) < 2):
        raise ValueError("Macierz musi być kwadratowa i zawierać co najmniej 2 postacie.")

    if not np.all(np.isfinite(pojedynki)):
        raise ValueError("Macierz zawiera niepoprawne wartości.")

    if np.any((pojedynki < 0) | (pojedynki > 1)):
        raise ValueError("Prawdopodobieństwa muszą być w zakresie od 0 do 1.")

    if not np.allclose(np.diag(pojedynki), 0.5):
        raise ValueError("Na przekątnej macierzy musi być 0.5.")

    if not np.allclose(pojedynki + pojedynki.T, 1.0):
        raise ValueError("Macierz musi spełniać warunek P(i,j) + P(j,i) = 1.")

    return (pojedynki.sum(axis=1) - 0.5) / (len(pojedynki) - 1)


def zapisz_csv(sciezka, nazwy, role, sila, srednie_szanse, ranking):
    with open(sciezka, "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.writer(plik, delimiter=";")
        pisarz.writerow(["Miejsce", "Postać", "Rola", "Siła", "Średnia szansa wygranej"])
        for miejsce, i in enumerate(ranking, start=1):
            pisarz.writerow([miejsce, nazwy[i], role[i],
                             f"{sila[i]:.4f}", f"{srednie_szanse[i]:.2%}"])


def testy():
    assert waliduj(NAZWY, STATYSTYKI)
    for dane in [np.array([[1, 2, 3, 4]]),
                 np.array([[1, 2, 3, 4], [-1, 2, 3, 4]]),
                 np.array([[1, 2, 3, 4], [np.nan, 2, 3, 4]])]:
        try:
            waliduj(np.array(["A", "B"]), dane)
        except ValueError:
            pass
        else:
            raise AssertionError("Brak oczekiwanego błędu walidacji")
    przyklad = np.array([[10, 20, 30, 40], [10, 50, 60, 40]], dtype=float)
    wynik = normalizuj(przyklad)
    np.testing.assert_allclose(wynik[:, 0], [0, 0])
    np.testing.assert_allclose(wynik[:, 1], [0, 1])
    np.testing.assert_allclose(wynik[:, 3], [0, 0])
    dane_sily = np.array([[0, 0, 0, 0], [10, 20, 30, 40], [20, 40, 60, 80]], dtype=float)
    np.testing.assert_allclose(oblicz_sile(dane_sily), [0, 0.5, 1])
    role_test = np.array([[100, 40, 10, 15], [130, 20, 20, 8], [100, 20, 10, 10]])
    np.testing.assert_array_equal(okresl_role(role_test),
                                  ["Szturmowiec", "Obrońca", "Wszechstronny"])
    np.testing.assert_array_equal(sortuj_ranking(np.array([0.4, 0.9, 0.9])),
                                  [1, 2, 0])
    proby = macierz_pojedynkow(np.array([0.1, 0.6, 0.9]))
    assert np.allclose(np.diag(proby), 0.5)
    assert np.allclose(proby + proby.T, 1.0)
    np.testing.assert_allclose(oblicz_srednie_szanse(
        np.array([[0.5, 0.8, 0.6], [0.2, 0.5, 0.4], [0.4, 0.6, 0.5]])),
        [0.7, 0.3, 0.5])
    print("Wszystkie testy: OK")


def main():
    waliduj(NAZWY, STATYSTYKI)
    testy()
    sila = oblicz_sile(STATYSTYKI)
    role = okresl_role(STATYSTYKI)
    ranking = sortuj_ranking(sila)
    pojedynki = macierz_pojedynkow(sila)
    srednie_szanse = oblicz_srednie_szanse(pojedynki)

    print("\n=== RANKING POSTACI RPG ===")
    for miejsce, i in enumerate(ranking, start=1):
        print(f"{miejsce}. {NAZWY[i]:12} | {role[i]:13} "
              f"| siła: {sila[i]:.3f} | średnia szansa: {srednie_szanse[i]:.1%}")

    print("\n=== POSTACIE SPEŁNIAJĄCE WYMAGANIA ===")
    maska = ((STATYSTYKI[:, 0] >= 100)
             & (STATYSTYKI[:, 3] >= 10) & (sila >= 0.45))
    wybrane = NAZWY[maska]
    print(", ".join(wybrane.tolist()) if len(wybrane) else "Brak")

    print("\n=== STATYSTYKI GRUPY ===")
    for i, etykieta in enumerate(KOLUMNY):
        print(f"{etykieta:10}: min={np.min(STATYSTYKI[:, i]):.1f}, "
              f"średnia={np.mean(STATYSTYKI[:, i]):.1f}, "
              f"max={np.max(STATYSTYKI[:, i]):.1f}")

    zapisz_csv("raport_postaci.csv", NAZWY, role, sila, srednie_szanse, ranking)
    print("\nZapisano: raport_postaci.csv")


if __name__ == "__main__":
    main()
