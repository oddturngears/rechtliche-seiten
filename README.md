# Rechtliche Seiten für Answerobics, Daily Logic, DicePad, Wortweber und Harbor Flow (A0.2, A5.5)

Datenschutzerklärung und Support-Seite je App sowie ein gemeinsames Impressum, jeweils auf Deutsch und Englisch auf derselben Seite. Der Browser zeigt seine Sprache, oben rechts lässt sich umschalten. Die Seiten passen auf Handy und Desktop und folgen dem hellen bzw. dunklen Modus.

**Entwurf, keine Rechtsberatung.** Die Texte beschreiben, was die Apps laut Code am 13.11.2026 tun (Wortweber und Harbor Flow: am 22.11.2026). Vor der Veröffentlichung sollte sie jemand mit Rechtskenntnis prüfen, zum Beispiel ein Anwalt oder der Datenschutz-Check der Wirtschaftskammer.

## Aufbau

| Datei | Zweck |
|---|---|
| `config.json` | Deine Angaben, App-Namen, Menüpfade in den Apps, Fristen. Platzhalter stehen in `[eckigen Klammern]`. Was eine App tut, steht in `features` (Liste oben in `build.py`), z. B. `mediation` für weitere Werbenetzwerke, `subscriptions` für Abos und `revenuecat` für Käufe über RevenueCat |
| `build.py` | Erzeugt aus `config.json` die Seiten in `docs/` |
| `docs/` | Die fertige Website, so wie sie online geht |

Nach jeder Änderung an `config.json`:

```powershell
python build.py
```

Am Ende meldet das Skript, wie viele Platzhalter noch offen sind. Auf den Seiten sind sie gelb markiert.

Benennst du eine App um (Phase B, Namens-Schalter), änderst du `name` in `config.json` und baust neu. Die Adressen der Seiten bleiben gleich, weil sie am Kürzel (`slug`) hängen.

## Vor der Veröffentlichung

1. In `config.json` ausfüllen: Name, Anschrift, E-Mail-Adresse und Unternehmensgegenstand. Nach der Gewerbeanmeldung (Phase C) kommen `vat_id` (UID-Nummer, falls vorhanden) und die Gewerbebehörde dazu.
2. **Altersgrenze** im Abschnitt „Kinder“ bestätigen. Grundlage ist die Store-Zielgruppe ab 13 Jahren aus den Datenschutzangaben von Daily Logic. Danach die Markierung `[Altersgrenze prüfen]` in `build.py` entfernen.
3. **Answerobics-Server:** den Supabase-Standort eintragen. Empfohlen ist eine EU-Region, zum Beispiel Frankfurt. Zwei Fristen in der Erklärung muss der Server auch wirklich einhalten:
   - anonyme Konten nach `[30]` Tagen ohne Nutzung löschen und
   - Einladungsdaten nach höchstens `[24]` Monaten löschen.

   Beides erledigt seit 26.11.2026 der tägliche Job `quinovo-account-maintenance` (Migration `20261126090000_account_retention.sql` in quiz_app). Nach dem Einspielen in Supabase prüfen, dass pg_cron den Job angelegt hat. Danach die eckigen Klammern um die beiden Zahlen in `config.json` entfernen.
4. Mit Supabase und RevenueCat jeweils den Auftragsverarbeitungsvertrag (DPA) abschließen. Beide bieten ihn im Konto an.

## Online stellen (GitHub Pages, kostenlos)

1. In der GitHub-Organisation `oddturngears` das **öffentliche** Repository `rechtliche-seiten` anlegen (ohne README, .gitignore und Lizenz).
2. Diesen Ordner hochladen (alle Dateien inklusive `docs/`).
3. Im Repository unter **Settings → Pages**: „Deploy from a branch“, Branch `main`, Ordner `/docs`.
4. Nach ein bis zwei Minuten sind die Seiten erreichbar:

| Seite | Adresse |
|---|---|
| Übersicht | `https://oddturngears.github.io/rechtliche-seiten/` |
| Impressum | `https://oddturngears.github.io/rechtliche-seiten/imprint.html` |
| Answerobics | `…/answerobics/privacy.html` und `…/answerobics/support.html` |
| Daily Logic | `…/dailylogic/privacy.html` und `…/dailylogic/support.html` |
| DicePad | `…/dicepad/privacy.html` und `…/dicepad/support.html` |
| Wortweber | `…/wortweber/privacy.html` und `…/wortweber/support.html` |
| Harbor Flow | `…/harborflow/privacy.html` und `…/harborflow/support.html` |

5. Die Datenschutz-Adresse jeder App in deren `brand.json` unter `privacyUrl` eintragen und `dart run tools/apply_brand.dart` ausführen. Die Support-Adresse kommt in die Store-Einträge. Die eigene Domain folgt in Phase C. Dann ändern sich nur die Adressen, die Seiten bleiben.

## Harbor Flow (seit 22.11.2026)

Harbor Flow ist ein Godot-Spiel und unterscheidet sich von den Flutter-Apps:

- Werbung nur über Google AdMob (eigenes Plugin), Einwilligung über Googles UMP, keine weiteren Werbenetzwerke. Kommt später Mediation dazu, `mediation` ergänzen.
- Käufe direkt über Google Play Billing, später auch den App Store. Kein Abo und kein RevenueCat.
- Spielstand nur auf dem Gerät, kein Konto, keine Analyse, kein eigener Server.
- Die Menüpfade (`Einstellungen → „Datenschutz & Werbung“`, `„Käufe wiederherstellen“`) passen zur geplanten Einstellungsseite (A6.6). Heißen die Einträge dort anders, in `config.json` angleichen und neu bauen.
