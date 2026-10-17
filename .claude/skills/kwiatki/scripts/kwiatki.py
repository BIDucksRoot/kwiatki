#!/usr/bin/env python3
"""Zdjęcia roślin: lista nowych, wzorce do porównania, przypisanie do folderów, spis.

Uruchamiaj z katalogu repo kwiatki:
  python3 .claude/skills/kwiatki/scripts/kwiatki.py nowe
  python3 .claude/skills/kwiatki/scripts/kwiatki.py wzorce
  python3 .claude/skills/kwiatki/scripts/kwiatki.py przypisz 1=monstera 2=monstera IMG_1240.HEIC=fikus
  python3 .claude/skills/kwiatki/scripts/kwiatki.py nowa monstera --nazwa "Monstera" --gatunek "Monstera deliciosa"
  python3 .claude/skills/kwiatki/scripts/kwiatki.py brak [RRRR-MM]
  python3 .claude/skills/kwiatki/scripts/kwiatki.py spis

Potrzebny Pillow (pip install pillow). HEIC z iPhone'a: pip install pillow-heif
albo ImageMagick (convert). Podglądy i arkusze trafiają do .podglad/ (poza gitem).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, time
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    sys.exit("Brak Pillow: pip install pillow pillow-heif")
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

SKILL = Path(__file__).resolve().parents[1]
ZDJECIA = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}
ARCHIWUM_MAX = 2048   # dłuższy bok zdjęcia zapisanego w repo
PODGLAD_MAX = 1024    # dłuższy bok podglądu do oglądania
KAFEL = 380           # kafel na arkuszu
NA_ARKUSZ = 12        # 4 × 3 kafle, arkusz ok. 1520 × 1250 px


def repo_root():
    if os.environ.get("KWIATKI_REPO"):
        return Path(os.environ["KWIATKI_REPO"]).resolve()
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "rosliny").is_dir() and (d / "nowe").is_dir():
            return d
    return Path(__file__).resolve().parents[4]


ROOT = repo_root()
NOWE = ROOT / "nowe"
ROSLINY = ROOT / "rosliny"
PODGLAD = ROOT / ".podglad"


def rel(p):
    try:
        return str(Path(p).relative_to(ROOT))
    except ValueError:
        return str(p)


# ---------- obrazy ----------

def otworz(path):
    """Otwiera zdjęcie (też HEIC) z obrotem według EXIF. Zwraca (obraz, exif)."""
    try:
        im = Image.open(path)
        im.load()
    except Exception:
        if path.suffix.lower() not in {".heic", ".heif"}:
            raise
        tmp = PODGLAD / "tmp" / (path.stem + ".jpg")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        if not shutil.which("convert") or subprocess.run(
                ["convert", str(path), "-auto-orient", str(tmp)], capture_output=True).returncode:
            raise RuntimeError("HEIC nie do odczytania: pip install pillow-heif i uruchom jeszcze raz")
        im = Image.open(tmp)
        im.load()
    exif = im.getexif()
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im, exif


def zmniejsz(im, bok):
    im = im.copy()
    im.thumbnail((bok, bok), Image.LANCZOS)
    return im


WZORY_NAZW = [
    # IMG_20261017_143205.jpg, PXL_20261017_143205123.jpg, 20261017_143205.jpg
    re.compile(r"(20\d\d)(\d\d)(\d\d)[_-](\d\d)(\d\d)(\d\d)"),
    # WhatsApp Image 2026-10-03 at 09.12.27.jpeg
    re.compile(r"(20\d\d)-(\d\d)-(\d\d) at (\d\d)\.(\d\d)\.(\d\d)"),
    # 2026-10-17_143205.jpg (zdjęcia już w repo)
    re.compile(r"(20\d\d)-(\d\d)-(\d\d)_(\d\d)(\d\d)(\d\d)"),
]


def czas_zdjecia(path, exif):
    """Zwraca (datetime, źródło): exif, nazwa albo plik (niepewne)."""
    if exif:
        txt = exif.get_ifd(0x8769).get(36867) or exif.get(306)
        if txt:
            try:
                return datetime.strptime(str(txt).strip()[:19], "%Y:%m:%d %H:%M:%S"), "exif"
            except ValueError:
                pass
    for w in WZORY_NAZW:
        m = w.search(path.name)
        if m:
            try:
                return datetime(*map(int, m.groups())), "nazwa"
            except ValueError:
                pass
    return datetime.fromtimestamp(path.stat().st_mtime).replace(microsecond=0), "plik"


def arkusz(pozycje, cel_prefix):
    """pozycje: [(ścieżka podglądu, podpis)]. Zapisuje arkusze po 12 kafli."""
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        try:
            font = ImageFont.load_default(size=22)
        except TypeError:
            font = ImageFont.load_default()
    pisz = 30
    kol = 4
    pliki = []
    for start in range(0, len(pozycje), NA_ARKUSZ):
        partia = pozycje[start:start + NA_ARKUSZ]
        wiersze = (len(partia) + kol - 1) // kol
        k = min(kol, len(partia))
        ark = Image.new("RGB", (k * KAFEL, wiersze * (KAFEL + pisz)), "white")
        d = ImageDraw.Draw(ark)
        for i, (sciezka, podpis) in enumerate(partia):
            x, y = (i % kol) * KAFEL, (i // kol) * (KAFEL + pisz)
            im = Image.open(sciezka)
            im.thumbnail((KAFEL - 8, KAFEL - 8))
            ark.paste(im, (x + (KAFEL - im.width) // 2, y + (KAFEL - im.height) // 2))
            d.text((x + 6, y + KAFEL + 2), podpis[:30], fill="black", font=font)
            d.rectangle([x, y, x + KAFEL - 1, y + KAFEL + pisz - 1], outline="#bbb")
        cel = PODGLAD / f"{cel_prefix}_{len(pliki) + 1}.jpg"
        ark.save(cel, quality=85)
        pliki.append(cel)
    return pliki


# ---------- rośliny ----------

POLE = re.compile(r"^- \*\*(.+?):\*\*[ \t]*(.*)$", re.M)


def pola(md_path):
    if not md_path.exists():
        return {}
    # „do uzupełnienia (podpowiedź z szablonu)” → „do uzupełnienia”
    return {k.strip(): re.sub(r"^(do uzupełnienia) \(.*\)$", r"\1", v.strip())
            for k, v in POLE.findall(md_path.read_text(encoding="utf-8"))}


def rosliny():
    if not ROSLINY.is_dir():
        return []
    return sorted(d for d in ROSLINY.iterdir()
                  if d.is_dir() and not d.name.startswith(("_", ".")))


def zdjecia_rosliny(d):
    z = d / "zdjecia"
    return sorted(p for p in z.iterdir() if p.suffix.lower() in ZDJECIA) if z.is_dir() else []


def czas_z_nazwy(p):
    m = WZORY_NAZW[2].search(p.name)
    return datetime(*map(int, m.groups())) if m else None


def pierwszy_wpis(d):
    """Pola z najnowszego wpisu dziennika (pierwsza sekcja ## …)."""
    dz = d / "dziennik.md"
    if not dz.exists():
        return None, {}
    txt = dz.read_text(encoding="utf-8")
    m = re.search(r"^## (.+)$", txt, re.M)
    if not m:
        return None, {}
    reszta = txt[m.end():]
    n = re.search(r"^## ", reszta, re.M)
    sekcja = reszta[:n.start()] if n else reszta
    return m.group(1).strip(), {k.strip(): v.strip() for k, v in POLE.findall(sekcja)}


# ---------- komendy ----------

def cmd_nowe(a):
    if not NOWE.is_dir():
        sys.exit(f"Brak folderu {rel(NOWE)}")
    pliki = sorted(p for p in NOWE.rglob("*") if p.is_file() and p.suffix.lower() in ZDJECIA)
    if not pliki:
        print("Brak nowych zdjęć w nowe/.")
        return
    (PODGLAD / "nowe").mkdir(parents=True, exist_ok=True)
    for stary in (PODGLAD / "nowe").glob("*.jpg"):
        stary.unlink()
    for stary in PODGLAD.glob("nowe_arkusz_*.jpg"):
        stary.unlink()
    lista, bledy = [], []
    for p in pliki:
        try:
            im, exif = otworz(p)
        except Exception as e:
            bledy.append(f"{rel(p)}: {e}")
            continue
        t, zrodlo = czas_zdjecia(p, exif)
        lista.append({"plik": rel(p), "czas": t.isoformat(), "zrodlo": zrodlo,
                      "wymiary": f"{im.width}x{im.height}", "_im": im})
    # zdjęcia bez daty na końcu: ich czas z pliku nic nie mówi o kolejności
    for b in bledy:
        print("Nie da się otworzyć:", b)
    if not lista:
        return
    lista.sort(key=lambda x: (x["zrodlo"] == "plik", x["czas"], x["plik"]))
    for nr, z in enumerate(lista, 1):
        z["nr"] = nr
        pod = PODGLAD / "nowe" / f"{nr:02d}.jpg"
        zmniejsz(z.pop("_im"), PODGLAD_MAX).save(pod, quality=85)
        z["podglad"] = rel(pod)
    (PODGLAD / "nowe.json").write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")

    miesiace = [z["czas"][:7] for z in lista if z["zrodlo"] != "plik"]
    miesiac = max(set(miesiace), key=miesiace.count) if miesiace else date.today().isoformat()[:7]
    print(f"Nowe zdjęcia: {len(lista)}, miesiąc sesji: {miesiac}")
    print("nr  czas              przerwa  źródło  plik")
    poprz = None
    for z in lista:
        t = datetime.fromisoformat(z["czas"])
        przerwa = "–" if z["zrodlo"] != "plik" else "?"
        if poprz and z["zrodlo"] != "plik":
            s = int((t - poprz).total_seconds())
            przerwa = f"{s // 60}:{s % 60:02d}" if 0 <= s < 3600 else ">1 h"
        poprz = t
        print(f"{z['nr']:>2}  {t:%Y-%m-%d %H:%M}  {przerwa:>7}  {z['zrodlo']:<6}  {z['plik']}")
    if any(z["zrodlo"] == "plik" for z in lista):
        print("Uwaga: źródło „plik” = brak daty w EXIF i w nazwie, czas niepewny (kolejność też).")
    ark = arkusz([(ROOT / z["podglad"], f"{z['nr']}  {z['czas'][11:16] if z['zrodlo'] != 'plik' else '?'}")
                  for z in lista], "nowe_arkusz")
    print("Podglądy: .podglad/nowe/NN.jpg")
    print("Arkusze:", ", ".join(rel(p) for p in ark))


def cmd_wzorce(a):
    rs = rosliny()
    if not rs:
        print("Brak roślin w rosliny/ (pierwszy przegląd: wszystkie zdjęcia to nowe rośliny).")
        return
    (PODGLAD / "wzorce").mkdir(parents=True, exist_ok=True)
    for stary in PODGLAD.glob("wzorce_arkusz_*.jpg"):
        stary.unlink()
    pozycje, sesje = [], {}
    for d in rs:
        k = pola(d / "karta.md")
        zd = zdjecia_rosliny(d)
        print(f"\n{d.name}: {k.get('Nazwa', '?')} ({k.get('Gatunek', '?')})")
        print(f"  gdzie: {k.get('Gdzie stoi', '?')}")
        print(f"  doniczka: {k.get('Doniczka', '?')}")
        print(f"  znaki: {k.get('Znaki rozpoznawcze', '?')}")
        if not zd:
            print("  brak zdjęć")
            continue
        ost = zd[-1]
        pod = PODGLAD / "wzorce" / f"{d.name}.jpg"
        if not pod.exists() or pod.stat().st_mtime < ost.stat().st_mtime:
            zmniejsz(otworz(ost)[0], PODGLAD_MAX).save(pod, quality=85)
        print(f"  ostatnie zdjęcie: {rel(ost)} (podgląd {rel(pod)})")
        pozycje.append((pod, d.name))
        for p in zd:
            t = czas_z_nazwy(p)
            if t:
                sesje.setdefault(t.strftime("%Y-%m"), []).append((t, d.name))
    if sesje:
        m = max(sesje)
        kol, bylo = [], set()
        for t, s in sorted(sesje[m]):
            if s not in bylo:
                bylo.add(s)
                kol.append(s)
        print(f"\nKolejność zdjęć w ostatniej sesji ({m}): " + " → ".join(kol))
    if pozycje:
        print("Arkusze wzorców:", ", ".join(rel(p) for p in arkusz(pozycje, "wzorce_arkusz")))


def cmd_przypisz(a):
    meta = PODGLAD / "nowe.json"
    lista = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else []
    po_nr = {str(z["nr"]): z for z in lista}
    log_path = PODGLAD / "przypisane.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    for para in a.pary:
        if "=" not in para:
            sys.exit(f"Zły zapis „{para}” – ma być nr=roślina albo plik=roślina")
        klucz, slug = para.rsplit("=", 1)
        d = ROSLINY / slug
        if not d.is_dir():
            sys.exit(f"Nie ma rośliny „{slug}”. Najpierw: kwiatki.py nowa {slug} --nazwa …")
        if klucz in po_nr:
            src = ROOT / po_nr[klucz]["plik"]
        else:
            src = next((p for p in [ROOT / klucz, NOWE / klucz] if p.is_file()), None)
            if src is None:
                hit = [p for p in NOWE.rglob("*") if p.name == klucz]
                src = hit[0] if hit else None
        if src is None or not src.is_file():
            print(f"Pominięte: nie ma pliku dla „{klucz}” (już przeniesiony?)")
            continue
        im, exif = otworz(src)
        t, zrodlo = czas_zdjecia(src, exif)
        if a.data:
            # bez daty: koniec dnia, żeby nie mieszało kolejności zdjęć z sesji
            t = datetime.combine(date.fromisoformat(a.data), t.time() if zrodlo != "plik" else time(23, 59))
        (d / "zdjecia").mkdir(exist_ok=True)
        cel = d / "zdjecia" / f"{t:%Y-%m-%d_%H%M%S}.jpg"
        n = 2
        while cel.exists():
            cel = d / "zdjecia" / f"{t:%Y-%m-%d_%H%M%S}-{n}.jpg"
            n += 1
        # bez EXIF: w repo nie ma lokalizacji GPS z telefonu
        zmniejsz(im, ARCHIWUM_MAX).save(cel, "JPEG", quality=85, optimize=True)
        src.unlink()
        log.append({"oryginal": rel(src), "roslina": slug, "zdjecie": rel(cel),
                    "czas": t.isoformat(), "zrodlo_czasu": zrodlo})
        uwaga = "  (czas niepewny)" if zrodlo == "plik" and not a.data else ""
        print(f"{rel(src)} → {rel(cel)}{uwaga}")
    PODGLAD.mkdir(exist_ok=True)
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")


def cmd_nowa(a):
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        sys.exit("Nazwa folderu: małe litery bez polskich znaków, cyfry i myślniki, np. sansewieria-kuchnia")
    d = ROSLINY / a.slug
    if d.exists():
        sys.exit(f"{rel(d)} już jest")
    (d / "zdjecia").mkdir(parents=True)
    zamiany = {"{{nazwa}}": a.nazwa, "{{gatunek}}": a.gatunek or "do ustalenia",
               "{{data}}": date.today().isoformat(), "{{slug}}": a.slug}
    for szablon, cel in [("karta.md", "karta.md"), ("dziennik.md", "dziennik.md")]:
        txt = (SKILL / "szablony" / szablon).read_text(encoding="utf-8")
        for k, v in zamiany.items():
            txt = txt.replace(k, v)
        (d / cel).write_text(txt, encoding="utf-8")
    print(f"Nowa roślina: {rel(d)}/ (karta.md, dziennik.md, zdjecia/)")


def cmd_brak(a):
    miesiac = a.miesiac
    if not miesiac:
        wszystkie = [czas_z_nazwy(p) for d in rosliny() for p in zdjecia_rosliny(d)]
        wszystkie = [t for t in wszystkie if t]
        miesiac = max(wszystkie).strftime("%Y-%m") if wszystkie else date.today().isoformat()[:7]
    braki = [d.name for d in rosliny()
             if not any(p.name.startswith(miesiac) for p in zdjecia_rosliny(d))]
    print(f"Bez zdjęcia z {miesiac}: " + (", ".join(braki) if braki else "brak, są wszystkie"))


def cmd_spis(a):
    w = ["# Rośliny", "",
         "Plik generowany: `python3 .claude/skills/kwiatki/scripts/kwiatki.py spis`. "
         "Szczegóły w karcie i dzienniku każdej rośliny.", "",
         "| | Roślina | Gatunek | Gdzie stoi | Ostatni przegląd | Stan | Trend |",
         "|---|---|---|---|---|---|---|"]
    for d in rosliny():
        k = pola(d / "karta.md")
        zd = zdjecia_rosliny(d)
        mini = f'<img src="{d.name}/zdjecia/{zd[-1].name}" width="100">' if zd else ""
        tytul, wpis = pierwszy_wpis(d)
        kiedy = tytul.split(" ")[0] if tytul else "–"
        nazwa = k.get("Nazwa", d.name)
        w.append(f"| {mini} | [{nazwa}]({d.name}/dziennik.md) · [karta]({d.name}/karta.md) "
                 f"| {k.get('Gatunek', '')} | {k.get('Gdzie stoi', '')} | {kiedy} "
                 f"| {wpis.get('Stan', '–')} | {wpis.get('Trend', '–')} |")
    arch = sorted(d.name for d in ROSLINY.glob("_archiwum/*") if d.is_dir())
    if arch:
        w += ["", "Archiwum (rośliny, których już nie ma): " + ", ".join(
            f"[{s}](_archiwum/{s}/dziennik.md)" for s in arch)]
    (ROSLINY / "README.md").write_text("\n".join(w) + "\n", encoding="utf-8")
    print(f"Zapisano {rel(ROSLINY / 'README.md')} ({len(rosliny())} roślin)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("nowe", help="lista zdjęć w nowe/, podglądy i arkusze")
    sub.add_parser("wzorce", help="ostatnie zdjęcie i znaki rozpoznawcze każdej rośliny")
    p = sub.add_parser("przypisz", help="przenieś zdjęcia z nowe/ do roślin")
    p.add_argument("pary", nargs="+", help="nr=roślina albo plik=roślina")
    p.add_argument("--data", help="RRRR-MM-DD, gdy zdjęcie nie ma daty")
    p = sub.add_parser("nowa", help="nowy folder rośliny z szablonów")
    p.add_argument("slug")
    p.add_argument("--nazwa", required=True)
    p.add_argument("--gatunek")
    p = sub.add_parser("brak", help="rośliny bez zdjęcia z danego miesiąca")
    p.add_argument("miesiac", nargs="?")
    sub.add_parser("spis", help="odśwież rosliny/README.md")
    a = ap.parse_args()
    {"nowe": cmd_nowe, "wzorce": cmd_wzorce, "przypisz": cmd_przypisz, "nowa": cmd_nowa,
     "brak": cmd_brak, "spis": cmd_spis}[a.cmd](a)


if __name__ == "__main__":
    main()
