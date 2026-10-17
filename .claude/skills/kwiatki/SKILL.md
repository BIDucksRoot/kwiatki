---
name: kwiatki
description: Comiesięczny przegląd roślin doniczkowych w repo kwiatki. Przypisuje nowe zdjęcia z folderu nowe/ do folderów roślin (rosliny/nazwa-rosliny/), porównuje każdą roślinę z poprzednim miesiącem, ocenia, czy jest lepiej czy gorzej, i rozpisuje na najbliższy miesiąc podlewanie, nawóz, miejsce i zabiegi, z dziennikiem każdej rośliny i raportem w raporty/RRRR-MM.md. Używaj zawsze, gdy użytkownik wrzuca albo wspomina zdjęcia kwiatków lub roślin, pisze „przegląd kwiatków”, „nowe zdjęcia roślin”, „zrobiłem zdjęcia kwiatków”, pyta, co podlać, czym i kiedy nawozić, co dolega konkretnej roślinie, co ma zrobić z roślinami w tym miesiącu, chce dodać nową roślinę albo zobaczyć, jak roślina zmieniała się w czasie, nawet jeśli nie nazywa skilla. Monthly houseplant photo check-in, matching photos to plant folders, assessing change and planning watering and fertilizing.
---

# Kwiatki: comiesięczny przegląd roślin

Użytkownik raz w miesiącu fotografuje wszystkie rośliny. Twoja praca: rozpoznać, która roślina jest na którym zdjęciu, odłożyć zdjęcia do jej folderu, porównać z poprzednim miesiącem i powiedzieć konkretnie, co robić przez najbliższy miesiąc. Z czasem w repo powstaje historia każdej rośliny, więc dokładność dopasowania jest ważniejsza niż szybkość: zdjęcie w złym folderze psuje historię dwóch roślin naraz.

Pisz po polsku, prosto i krótko. Nazwy folderów i plików bez polskich znaków.

## Układ repo

```
nowe/                         zdjęcia do przejrzenia (użytkownik wrzuca tu cały miesiąc)
rosliny/<slug>/karta.md       kim jest roślina: gatunek, gdzie stoi, doniczka, znaki rozpoznawcze, potrzeby, historia
rosliny/<slug>/dziennik.md    wpis z każdego przeglądu, najnowszy na górze
rosliny/<slug>/zdjecia/       RRRR-MM-DD_GGMMSS.jpg (pomniejszone do 2048 px, bez EXIF i GPS)
rosliny/_archiwum/<slug>/     rośliny, których już nie ma (skrypt je pomija)
rosliny/README.md             spis wszystkich roślin (generowany)
raporty/RRRR-MM.md            raport z przeglądu: tabela, plan na miesiąc, zakupy, pytania
.podglad/                     podglądy i arkusze do oglądania (poza gitem)
```

Skrypt (uruchamiaj z katalogu repo): `python3 .claude/skills/kwiatki/scripts/kwiatki.py <komenda>`, dalej w skrócie `kwiatki.py`. Potrzebuje Pillow; dla zdjęć HEIC z iPhone'a `pillow-heif` albo ImageMagick. Gdy czegoś brakuje: `pip install pillow pillow-heif`.

Materiały pomocnicze, czytaj, gdy są potrzebne:
- `references/kalendarz.md`: co robić w danym miesiącu, zasady podlewania, nawożenia, przesadzania, światła, wilgotności i bezpieczeństwa. Przeczytaj na początku każdego przeglądu (przynajmniej wiersz bieżącego miesiąca i zasady).
- `references/objawy.md`: objaw, przyczyny, co zrobić. Gdy coś roślinie dolega.
- `references/gatunki.md`: potrzeby popularnych gatunków. Gdy zakładasz kartę albo nie znasz gatunku dobrze.
- `szablony/`: karta, dziennik, wpis do dziennika, raport.

## Przegląd miesięczny

### 1. Zdjęcia na miejscu

Użytkownik wrzuca zdjęcia do `nowe/` przez GitHub (Add file → Upload files) albo załącza je w czacie. Najpierw pobierz najnowszy stan gałęzi domyślnej repo (jej nazwę pokazuje `git remote show origin`, linia „HEAD branch”) i wciągnij ją do swojej gałęzi (`git fetch origin <gałąź>` i merge), bo zdjęcia wrzucone przez GitHub są tam, a nie na gałęzi sesji.

Jeśli zdjęć nie ma w `nowe/`, a użytkownik je załączył, poszukaj ich na dysku (np. `find / -xdev -newermt "-1 day" \( -iname '*.jp*g' -o -iname '*.heic' -o -iname '*.png' \) -not -path '*/proc/*' 2>/dev/null | head`) i skopiuj do `nowe/`. Gdy są tylko w rozmowie, bez pliku: możesz je dopasować i ocenić, ale nie zapiszesz ich w repo. Powiedz to i poproś o wrzucenie ich do `nowe/`, żeby historia była kompletna.

### 2. Lista nowych zdjęć

`kwiatki.py nowe` robi podglądy `.podglad/nowe/NN.jpg` (1024 px), arkusze `.podglad/nowe_arkusz_N.jpg` (po 12 miniatur z numerem i godziną) i wypisuje tabelę: numer, czas zrobienia, przerwę od poprzedniego zdjęcia i źródło czasu (EXIF, nazwa pliku albo „plik”, czyli niepewny). Numery zostają ważne do końca sesji (zapisane w `.podglad/nowe.json`), aż znowu uruchomisz `nowe`. Gdy skrypt pisze „HEIC nie do odczytania”, zrób `pip install pillow-heif` i uruchom `nowe` jeszcze raz.

### 3. Wzorce

`kwiatki.py wzorce` wypisuje dla każdej rośliny nazwę, gatunek, miejsce, doniczkę i znaki rozpoznawcze z karty, ścieżkę ostatniego zdjęcia, robi arkusze `.podglad/wzorce_arkusz_N.jpg` (ostatnie zdjęcie każdej rośliny podpisane nazwą folderu) i podaje kolejność zdjęć z poprzedniej sesji. Przy pierwszym przeglądzie roślin jeszcze nie ma: przejdź od razu do „Nowa roślina” niżej.

### 4. Dopasowanie

Obejrzyj arkusze nowych zdjęć i arkusze wzorców, a pojedyncze podglądy wtedy, gdy arkusz nie wystarcza. Wskazówki, mniej więcej od najmocniejszej:

1. **Gatunek i kształt liści** odsiewają większość kandydatów od razu.
2. **Doniczka i osłonka**: kolor, materiał, wzór, kształt. Zmienia się tylko przy przesadzeniu (sprawdź „Historię” w karcie i to, co pisze użytkownik).
3. **Miejsce i tło**: okno, parapet, mebel, ściana, podłoga. Rośliny zwykle stoją tam, gdzie miesiąc temu.
4. **Szczegóły tej konkretnej rośliny**: liczba pędów, podpora, złamany albo przycięty liść, wzór przebarwień na pstrych liściach (niepowtarzalny jak odcisk palca), kwiaty.
5. **Wielkość** względem doniczki i otoczenia (pamiętaj, że roślina przez miesiąc rośnie).
6. **Czas i kolejność**: użytkownik zwykle chodzi tą samą trasą co miesiąc temu. Zdjęcie zrobione mniej niż ok. minutę po zdjęciu całej rośliny to najczęściej zbliżenie tej samej rośliny (liść, plama, podłoże).

Każdemu zdjęciu daj pewność:
- **pewne**: co najmniej dwie niezależne wskazówki się zgadzają i nie ma drugiego kandydata,
- **prawdopodobne**: jedna mocna wskazówka albo rywale prawie wykluczeni (np. zbliżenie przypisane tylko po czasie),
- **niepewne**: pasuje do dwóch lub więcej roślin albo nie wiadomo, czy to roślina z repo, czy nowa.

Zdjęcie, które nie pasuje do żadnej rośliny z repo (inny gatunek i inna doniczka niż wszystkie), to nowa roślina: załóż ją od razu (sekcja „Nowa roślina”) i poproś w raporcie o potwierdzenie nazwy i miejsca.

Pewne i prawdopodobne przypisz od razu. O niepewne zapytaj użytkownika jedną turą (AskUserQuestion, do 4 pytań naraz; resztę wypisz w czacie): opisz zdjęcie słowami („zdjęcie 7, 14:32: mała sansewieria w białej doniczce na parapecie”), bo użytkownik nie widzi twoich podglądów, i daj kandydatów do wyboru plus „nowa roślina”. Jeśli nie da się zapytać albo użytkownik nie odpowiada, zostaw te zdjęcia w `nowe/` (przejrzysz je przy następnej sesji), zrób resztę i wpisz je w raporcie w „Pytaniach”.

Dwie rośliny tego samego gatunku: rozróżniaj po doniczce, miejscu i szczegółach, a po przeglądzie dopisz do „Znaków rozpoznawczych” w obu kartach to, po czym je w końcu rozróżniłeś. Karty mają ułatwiać kolejne dopasowanie, więc uzupełniaj je zawsze, gdy było trudno.

Seria prawie identycznych ujęć tej samej rośliny: przypisz najlepsze (ostre, cała roślina), resztę usuń z `nowe/` i wspomnij o tym w raporcie. Zdjęcia, które nie są roślinami albo są nieostre, zostaw w `nowe/` i powiedz o nich użytkownikowi.

### 5. Przeniesienie

`kwiatki.py przypisz 1=monstera 2=monstera 3=fikus-lirolistny` (albo `IMG_1234.HEIC=monstera`). Skrypt zapisuje zdjęcie jako `rosliny/<slug>/zdjecia/RRRR-MM-DD_GGMMSS.jpg`, pomniejszone, z poprawnym obrotem i bez EXIF, usuwa oryginał z `nowe/` i dopisuje parę do `.podglad/przypisane.json` (z tego zrobisz tabelę „Dopasowanie zdjęć” w raporcie). Gdy zdjęcie nie ma daty (źródło „plik”), dodaj `--data RRRR-MM-DD` z daty sesji.

Potem `kwiatki.py brak` pokazuje rośliny bez zdjęcia z tego miesiąca. Zapytaj o nie w raporcie: zapomniane, czy już ich nie ma (wtedy po potwierdzeniu `git mv rosliny/<slug> rosliny/_archiwum/<slug>` i wpis w historii karty, dlaczego).

### 6. Ocena każdej rośliny

Dla każdej sfotografowanej rośliny przeczytaj kartę i 2–3 ostatnie wpisy dziennika (żeby wiedzieć, co zalecałeś i co miało się poprawić), a potem obejrzyj obok siebie nowe zdjęcie i zdjęcie z poprzedniego przeglądu. Co kilka miesięcy porównaj też z pierwszym zdjęciem: powolne zmiany łatwo przegapić z miesiąca na miesiąc.

Na co patrzeć: nowe liście i pędy (policz, to najlepszy dowód, że roślina rośnie), kolor starych i młodych liści, końcówki i brzegi, plamy, liście opadłe i zwisające, pokrój (wyciąganie się, pochylanie do okna), podłoże (nalot, pleśń, odstawanie od ścianek), korzenie przy dnie i na wierzchu, proporcja rośliny do doniczki, ślady szkodników, kwiaty i pąki.

Zdjęcia z dwóch miesięcy rzadko są zrobione tak samo. Inne światło, balans bieli i odległość potrafią zmienić kolor i wielkość, więc porównuj konkretne rzeczy (ten sam liść, liczba liści, wysokość względem okna), a nie ogólne wrażenie. Jeśli nie da się rzetelnie porównać, napisz „nie da się ocenić” i dlaczego, zamiast zgadywać. Czego nie widać na zdjęciu (wilgotność podłoża, korzenie, spód liści, drobne szkodniki), o to zapytaj albo poproś o konkretne zdjęcie następnym razem.

**Stan** w skali 1–5:
- 5: zdrowa, rośnie, nic do poprawy
- 4: dobrze, drobiazgi (pojedynczy żółty liść, suche końcówki)
- 3: coś jej dolega, ale nie pilne (wyciąga się, kilka liści z plamami)
- 2: wyraźny problem, działać w tym miesiącu (szkodniki, gnicie, duża utrata liści)
- 1: ratunek, zostało niewiele zdrowej rośliny

**Trend** względem poprzedniego przeglądu: lepiej, bez zmian, gorzej albo nie da się ocenić. W tabelach ↑ → ↓ ?.

### 7. Zalecenia na najbliższy miesiąc

Dla każdej rośliny osobno, dopasowane do jej karty, stanu i bieżącego miesiąca z `references/kalendarz.md`:

- **Podlewanie**: sygnał (np. „gdy wierzchnie 3 cm są suche”), orientacyjnie co ile dni w tym miesiącu w tej doniczce, ile i jak (od góry do wycieknięcia, do podstawki, moczenie), jaka woda. Jeśli karta mówi, jak użytkownik podlewa teraz, odnieś się do tego („zamiast co tydzień, co 10–14 dni”).
- **Nawóz**: rodzaj, dawka, co ile i do kiedy, albo „nie” z krótkim powodem (spoczynek, świeżo przesadzona, chora). Lepiej pół dawki niż za dużo.
- **Miejsce i światło**, **wilgotność**: tylko gdy coś zmienić albo pilnować.
- **Zabiegi**: przesadzanie (z terminem, zwykle III–IV), cięcie, mycie liści, obracanie, walka ze szkodnikami. Gdy nic nie trzeba, napisz „nic poza podlewaniem”: zdrowej roślinie nie dokładaj pracy.
- **Sprawdzić następnym razem**: np. „zbliżenie spodu liści”, „czy nowy liść się rozwinął”.

Bądź konkretny (liczby, nazwy, terminy), ale nie udawaj precyzji, której nie masz: interwał podlewania to orientacja, decyduje podłoże. W domu jest małe dziecko: przy roślinach trujących przypominaj o miejscu poza zasięgiem, a na szkodniki proponuj najpierw sposoby łagodne (szczegóły w `kalendarz.md`, „Bezpieczeństwo”).

### 8. Zapis

1. **Dziennik** każdej rośliny: nowy wpis według `szablony/wpis.md`, zaraz pod nagłówkiem pliku (najnowszy na górze), z miniaturami zdjęcia teraz i z poprzedniego przeglądu. „Co zrobiono od ostatniego przeglądu” wypełnij tym, co powiedział użytkownik, inaczej „brak informacji”.
2. **Karta**: popraw to, co się zmieniło (miejsce, doniczka, podlewanie, znaki rozpoznawcze) i dopisz do „Historii” zdarzenia (przesadzenie, cięcie, szkodniki, przestawienie).
3. **Raport** `raporty/RRRR-MM.md` według `szablony/raport.md`. Najważniejsze są „W skrócie” i „Plan na miesiąc”: rośliny pogrupowane według rytmu podlewania, lista nawożenia i zabiegów do odhaczenia, zakupy zebrane ze wszystkich roślin. Jeśli raport z tego miesiąca już jest (druga tura zdjęć), dopisz do niego sekcję „Uzupełnienie RRRR-MM-DD”.
4. **Spis**: `kwiatki.py spis` odświeża `rosliny/README.md` (miniatura, stan i trend z ostatniego wpisu).

### 9. Commit i odpowiedź

Sprawdź, że w `nowe/` zostały tylko zdjęcia celowo odłożone, potem commit (np. „Przegląd roślin 2026-10: 18 zdjęć, 12 roślin”) i push według zasad sesji (w sesji w chmurze: gałąź sesji i PR).

W czacie krótko: ile zdjęć i roślin, co jest lepiej i co gorzej, 1–3 najpilniejsze rzeczy, zakupy, pytania (w tym zdjęcia niepewne i rośliny bez zdjęcia) i link do raportu. Resztę użytkownik przeczyta w raporcie.

## Nowa roślina

Gdy zdjęcie nie pasuje do żadnej rośliny (albo to pierwszy przegląd i roślin jeszcze nie ma):

1. Pogrupuj zdjęcia nowej rośliny (cała roślina i zbliżenia).
2. Rozpoznaj gatunek i napisz, jak bardzo jesteś pewny („prawdopodobnie *Epipremnum aureum*”). Zaproponuj slug: polska nazwa zwyczajowa małymi literami, z miejscem albo cechą, gdy roślin tego gatunku jest więcej (`sansewieria-kuchnia`, `monstera-duza`). Slugów później nie zmieniaj, bo psują się linki w raportach.
3. `kwiatki.py nowa <slug> --nazwa "Sansewieria w kuchni" --gatunek "Dracaena trifasciata"` zakłada folder z kartą i dziennikiem.
4. Wypełnij kartę tym, co widać (doniczka, tło, prawdopodobne okno, znaki rozpoznawcze) i potrzebami gatunku (`references/gatunki.md`). Czego nie widać, zostaw jako „do uzupełnienia” i zbierz w pytaniach: gdzie stoi i na którą stronę świata jest okno, jak i czym jest teraz podlewana, od kiedy jest i kiedy była przesadzana.
5. Pierwszy wpis w dzienniku ma trend „pierwszy przegląd”.

Przy pierwszym przeglądzie wszystkich roślin nie blokuj pracy na pytaniach: załóż karty z najlepszymi propozycjami nazw, zrób raport, a na końcu poproś o jedną listę poprawek (nazwy, miejsca, podlewanie).

## Pytania między przeglądami

- „Co z monsterą?”, „Czemu fikus zrzuca liście?”: przeczytaj kartę i ostatnie wpisy dziennika tej rośliny, w razie potrzeby `references/objawy.md`, i odpowiedz. Jeśli użytkownik podaje nowe fakty (przesadził, przestawił, pojawiły się szkodniki), dopisz je do historii w karcie i krótką notatkę do dziennika (`## RRRR-MM-DD – notatka`).
- Pojedyncze zdjęcie z problemem: dopasuj, oceń jak wyżej, zapisz zdjęcie przez `nowe/` i `przypisz` i dodaj do dziennika wpis `## RRRR-MM-DD – dodatkowe zdjęcie` (bez pełnego planu, chyba że coś się zmienia).
- „Co mam zrobić w tym tygodniu?”: plan z najnowszego raportu w `raporty/`.
