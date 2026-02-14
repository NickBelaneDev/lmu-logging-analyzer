import re
from collections import Counter





def analyze_lmu_trace(file_path):
    # Definition der kritischen Suchmuster
    patterns = {
        "Physik-Warnungen (Ruckler)": r"slow physics ticks",
        "Dateifehler (MAS/WAV)": r"Error opening|not found|Failed to find",
        "Hardware/FFB Probleme": r"hwinput|Force feedback|Controller",
        "Kritische Fehler": r"Error:",
        "Lade-Warnungen": r"Warning"
    }

    findings = {key: [] for key in patterns}
    all_errors = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                current_line = line.strip()
                # Suche nach den definierten Mustern
                for category, pattern in patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):

                        if current_line not in findings[category]:
                            findings[category].append(current_line)

                # Sammle alle Zeilen mit "Error" für eine Top-Liste
                if "Error" in line:
                    all_errors.append(current_line)

        # Ausgabe der Analyse
        print("=== LMU TRACE ANALYSE REPORT ===\n")

        for category, matches in findings.items():
            count = len(matches)
            print(f"[{category}]: {count} Vorkommnisse")
            # Zeige die ersten 3 Beispiele jeder Kategorie
            for m in matches[:3]:
                print(f"  -> {m[:120]}...")
            print("-" * 30)

        # Top 5 häufigste Fehlermeldungen (hilft bei fehlenden Dateien)
        print("\n=== TOP 5 SPEZIFISCHE FEHLER ===")
        common_errors = Counter(all_errors).most_common(5)
        for err, count in common_errors:
            print(f"{count}x: {err[:100]}")

    except FileNotFoundError:
        print(f"Fehler: Die Datei '{file_path}' wurde nicht gefunden.")


if __name__ == "__main__":
    # Pfad zur trace.txt anpassen
    analyze_lmu_trace(r"C:\Program Files (x86)\Steam\steamapps\common\Le Mans Ultimate\UserData\Log\trace.txt")