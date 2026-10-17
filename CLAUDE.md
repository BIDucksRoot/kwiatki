# Kwiatki – kontekst projektu

Repo do comiesięcznego monitorowania roślin doniczkowych i balkonowych. Raz w miesiącu użytkownik fotografuje wszystkie rośliny i wrzuca zdjęcia do `nowe/`. Claude przypisuje zdjęcia do folderów roślin, porównuje z poprzednim miesiącem i pisze, co robić przez najbliższy miesiąc (podlewanie, nawóz, miejsce, zabiegi). Język: polski, prosty.

Każdy przegląd, każde zdjęcie roślin i każde pytanie o konkretną roślinę obsługuje skill `kwiatki` (`.claude/skills/kwiatki/SKILL.md`, wywołanie `/kwiatki`). Tam jest przebieg przeglądu, skrypt do zdjęć (`.claude/skills/kwiatki/scripts/kwiatki.py`), szablony i materiały (kalendarz pielęgnacji, objawy, gatunki).

## Układ repo

- `nowe/` – zdjęcia do przejrzenia. Po przeglądzie zostają tu tylko zdjęcia, których nie udało się przypisać.
- `rosliny/<slug>/` – jedna roślina: `karta.md` (gatunek, gdzie stoi, doniczka, znaki rozpoznawcze, potrzeby, historia), `dziennik.md` (wpis z każdego przeglądu, najnowszy na górze), `zdjecia/RRRR-MM-DD_GGMMSS.jpg`.
- `rosliny/_archiwum/` – rośliny, których już nie ma.
- `rosliny/README.md` – spis roślin, generowany przez `kwiatki.py spis`, nie edytuj ręcznie.
- `raporty/RRRR-MM.md` – raport z przeglądu: stan i trend każdej rośliny, plan na miesiąc, zakupy, pytania.
- `.podglad/` – podglądy i arkusze robione przez skrypt, poza gitem.

## Ustalenia

- Zdjęcia w repo są pomniejszone do 2048 px i bez EXIF (bez lokalizacji z telefonu). Oryginały zostają w telefonie.
- Slugi folderów: małe litery bez polskich znaków, z myślnikami, nie zmieniają się (linki w raportach).
- W domu jest małe dziecko: rośliny trujące mają to w karcie, a na szkodniki najpierw sposoby łagodne.
- Mieszkanie po przeprowadzce: Akwarelowa w Szczecinie (repo `akwarelowa`, strony świata okien i plany pokoi w jego `CLAUDE.md`). Po przestawieniu roślin popraw „Gdzie stoi” w kartach.
