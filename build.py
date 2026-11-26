"""Erzeugt die rechtlichen Seiten (Datenschutz, Support, Impressum) fuer alle
Apps aus config.json nach docs/ (GitHub Pages). Jede Seite enthaelt Deutsch und Englisch;
angezeigt wird die Sprache des Browsers, umschaltbar oben rechts.

Aufruf:  python build.py

Merkmale einer App ("features" in config.json): ads, banner, mediation (weitere
Werbenetzwerke über AdMob), purchases, subscriptions (Abos), revenuecat (Käufe
über RevenueCat statt direkt beim Store), online, local_network, share,
question_updates, rankings (Ranglisten, Liga, Aufzeichnungen, Herausforderungen),
cloud_save (Sicherung des Spielstands auf dem Server).
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
OP = CFG["operator"]
ON = CFG["online"]


def v(value: str) -> str:
    """Wert aus der Konfiguration; Platzhalter in [eckigen Klammern] markiert."""
    escaped = html.escape(value)
    return re.sub(r"\[([^\]]+)\]", r'<mark class="todo">[\1]</mark>', escaped)


def mail(lang: str) -> str:
    address = OP["email"]
    if address.startswith("["):
        return v(address)
    return f'<a href="mailto:{html.escape(address)}">{html.escape(address)}</a>'


def operator_block(lang: str) -> str:
    country = OP["country_de"] if lang == "de" else OP["country_en"]
    label = "E-Mail" if lang == "de" else "Email"
    return (
        f"<p>{v(OP['name'])}<br>{v(OP['street'])}<br>{v(OP['city'])}<br>"
        f"{html.escape(country)}<br>{label}: {mail(lang)}</p>"
    )


# --------------------------------------------------------------------------
# Datenschutzerklaerung
# --------------------------------------------------------------------------

AD_PARTNERS = [
    ("Google AdMob", "Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland",
     "Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Ireland",
     "https://policies.google.com/privacy"),
    ("AppLovin", "AppLovin Corporation, USA", "AppLovin Corporation, USA",
     "https://www.applovin.com/privacy/"),
    ("Unity Ads", "Unity Technologies, USA", "Unity Technologies, USA",
     "https://unity.com/legal/privacy-policy"),
    ("Liftoff Monetize (Vungle)", "Liftoff Mobile, Inc., USA", "Liftoff Mobile, Inc., USA",
     "https://liftoff.io/privacy-policy/"),
]


def partner_list(lang: str, mediation: bool = True) -> str:
    items = []
    for name, de, en, url in AD_PARTNERS if mediation else AD_PARTNERS[:1]:
        who = de if lang == "de" else en
        label = "Datenschutzhinweise" if lang == "de" else "Privacy policy"
        items.append(f'<li><strong>{name}</strong> ({who}), <a href="{url}">{label}</a></li>')
    return "<ul>" + "".join(items) + "</ul>"


def privacy_de(app: dict) -> str:
    f = set(app["features"])
    n = html.escape(app["name"])
    s = []
    s.append(f"<h1>Datenschutzerklärung für die App „{n}“</h1>")
    s.append(f'<p class="meta">Stand: {html.escape(app.get("updated", CFG["updated"]))}</p>')
    s.append("<h2>1. Wer ist verantwortlich?</h2>")
    s.append(f"<p>Verantwortlich für die Datenverarbeitung in der App „{n}“ ist:</p>")
    s.append(operator_block("de"))
    s.append("<h2>2. Das Wichtigste in Kürze</h2><ul>")
    if "online" in f and "cloud_save" in f:
        s.append("<li>Du brauchst kein Konto mit Namen, E-Mail-Adresse oder Passwort. Für die "
                 "Online-Funktionen und die Sicherung deines Spielstands legt die App ein anonymes "
                 "Konto an (Abschnitt 6).</li>")
    elif "online" in f:
        s.append("<li>Du brauchst kein Konto mit Namen, E-Mail-Adresse oder Passwort. Nur für das "
                 "Online-Duell und Einladungen legt die App ein anonymes Konto an (Abschnitt 6).</li>")
    else:
        s.append("<li>Du brauchst kein Konto. Wir fragen weder Namen noch E-Mail-Adresse ab.</li>")
    if "cloud_save" in f:
        s.append("<li>Fortschritt, Statistiken, Münzen und Einstellungen speichert die App auf deinem "
                 "Gerät. Eine Sicherungskopie deines Spielstands liegt auf unserem Server.</li>")
    else:
        s.append("<li>Fortschritt, Statistiken, Münzen und Einstellungen speichert die App nur auf deinem Gerät.</li>")
    s.append("<li>Die App zeigt Werbung. Ob sie personalisiert wird, entscheidest du im "
             "Einwilligungsdialog und kannst es jederzeit ändern.</li>")
    s.append("<li>Käufe wickeln Google Play bzw. der App Store ab. Zahlungsdaten erhalten wir nicht.</li>")
    s.append("<li>Wir setzen keine eigenen Analyse- oder Tracking-Werkzeuge ein.</li></ul>")

    s.append("<h2>3. Daten auf deinem Gerät</h2>")
    if "cloud_save" in f:
        s.append("<p>Die App speichert deinen Fortschritt, Statistiken, Münzen, Käufe-Status und "
                 "Einstellungen lokal auf deinem Gerät. Wenn du die App löschst, werden sie dort "
                 "ebenfalls gelöscht. Was davon zusätzlich auf unserem Server gesichert wird, steht "
                 "weiter unten unter „Sicherung des Spielstands“. Rechtsgrundlage ist die "
                 "Bereitstellung der von dir genutzten App (Art. 6 Abs. 1 lit. b DSGVO, § 165 Abs. 3 TKG 2021).</p>")
    else:
        s.append("<p>Die App speichert deinen Fortschritt, Statistiken, Münzen, Käufe-Status und "
                 "Einstellungen lokal auf deinem Gerät. Diese Daten werden nicht an uns übertragen. "
                 "Wenn du die App löschst, werden sie ebenfalls gelöscht. Rechtsgrundlage ist die "
                 "Bereitstellung der von dir genutzten App (Art. 6 Abs. 1 lit. b DSGVO, § 165 Abs. 3 TKG 2021).</p>")

    s.append("<h2>4. Werbung</h2>")
    banner = " (Banner und Videos)" if "banner" in f else ""
    if "mediation" in f:
        s.append(f"<p>Die App ist kostenlos und finanziert sich über Werbung{banner}. Die Anzeigen liefert "
                 "Google AdMob, das weitere Werbenetzwerke einbindet („Vermittlung“):</p>")
    else:
        s.append(f"<p>Die App ist kostenlos und finanziert sich über Werbung{banner}. Die Anzeigen liefert "
                 "Google AdMob:</p>")
    s.append(partner_list("de", "mediation" in f))
    s.append("<p><strong>Welche Daten:</strong> Werbe-ID deines Geräts (auf dem iPhone nur mit deiner "
             "Erlaubnis in der Tracking-Abfrage), IP-Adresse und daraus der ungefähre Standort, Angaben "
             "zu Gerät, Betriebssystem und App, Interaktionen mit Anzeigen sowie technische "
             "Diagnosedaten.</p>")
    s.append("<p><strong>Wozu:</strong> Anzeigen ausspielen, ihre Häufigkeit begrenzen, Betrug "
             "verhindern, Reichweite messen und – nur mit deiner Einwilligung – Werbung auf deine "
             "Interessen zuschneiden.</p>")
    s.append("<p><strong>Deine Wahl:</strong> Beim ersten Start fragt dich ein Einwilligungsdialog "
             "(Google User Messaging Platform), auf dem iPhone zusätzlich die Tracking-Abfrage von "
             f"Apple. Du kannst deine Entscheidung jederzeit unter <em>{html.escape(app['privacy_setting_de'])}</em> "
             "ändern oder widerrufen. Ohne Einwilligung siehst du nur nicht personalisierte Werbung.</p>")
    s.append(f"<p>Videos mit Belohnung ({html.escape(app['rewarded_de'])}) siehst du nur, wenn du sie "
             "selbst startest.</p>")
    s.append("<p><strong>Rechtsgrundlage:</strong> deine Einwilligung (Art. 6 Abs. 1 lit. a DSGVO, "
             "§ 165 Abs. 3 TKG 2021) für personalisierte Werbung und den Zugriff auf Kennungen deines "
             "Geräts; für nicht personalisierte Werbung unser berechtigtes Interesse, die App kostenlos "
             "anzubieten (Art. 6 Abs. 1 lit. f DSGVO). Die Werbepartner verarbeiten die Daten teils in "
             "den USA. Grundlage ist der Angemessenheitsbeschluss zum EU-US Data Privacy Framework, "
             "soweit der Partner zertifiziert ist, sonst die Standardvertragsklauseln der "
             "EU-Kommission.</p>")

    if "subscriptions" in f:
        s.append("<h2>5. Käufe und Abos</h2>")
        s.append("<p>Käufe und Abos bezahlst du über Google Play bzw. den App Store von Apple, nach deren "
                 "Bedingungen. Deine Zahlungsdaten erhalten wir nicht.</p>")
    else:
        s.append("<h2>5. Käufe</h2>")
        s.append("<p>Käufe bezahlst du über Google Play bzw. den App Store von Apple, nach deren "
                 "Bedingungen. Deine Zahlungsdaten erhalten wir nicht.</p>")
    if "revenuecat" not in f:
        s.append("<p>Damit gekaufte Inhalte freigeschaltet werden und sich wiederherstellen lassen, fragt "
                 "die App direkt beim Store ab, welche Käufe zu deinem Store-Konto gehören. Einen "
                 "eigenen Server oder weitere Dienstleister nutzen wir dafür nicht. Google bzw. Apple "
                 "verarbeiten die Kaufdaten in eigener Verantwortung nach ihren "
                 "Datenschutzbestimmungen. Rechtsgrundlage ist die Erfüllung des Kaufvertrags "
                 "(Art. 6 Abs. 1 lit. b DSGVO).</p>")
    else:
        s.append("<p>Damit gekaufte Inhalte freigeschaltet werden und sich wiederherstellen lassen, nutzen "
                 'wir <strong>RevenueCat</strong> (RevenueCat, Inc., USA, <a href="https://www.revenuecat.com/privacy">'
                 "Datenschutzhinweise</a>) als Auftragsverarbeiter. Verarbeitet werden eine zufällige, "
                 "anonyme Kennung, die die App erzeugt, Angaben zum Kauf (Produkt, Zeitpunkt, Preis, "
                 "Transaktionsnummer des Stores, Abo-Status) sowie Angaben zu Gerät, Betriebssystem, "
                 "App-Version und die IP-Adresse. Rechtsgrundlage ist die Erfüllung des Kaufvertrags "
                 "(Art. 6 Abs. 1 lit. b DSGVO). Für die Übermittlung in die USA gilt das in Abschnitt 4 "
                 "Gesagte.</p>")

    nr = 6
    if "online" in f:
        extra = "rankings" in f or "cloud_save" in f
        s.append(f"<h2>{nr}. {'Server, Online-Duell und Einladungen' if extra else 'Online-Duell und Einladungen'}</h2>")
        s.append("<p>Für Duelle gegen andere Spielerinnen und Spieler, für Einladungscodes"
                 + (", Ranglisten" if "rankings" in f else "")
                 + (" und die Sicherung deines Spielstands" if "cloud_save" in f else "")
                 + " nutzt die App einen Server von <strong>Supabase</strong> (Supabase Inc., USA) als "
                 f"Auftragsverarbeiter. Standort der Server: {v(ON['server_region_de'])}.</p>")
        if "cloud_save" in f:
            s.append("<p>Sobald du in der App Fortschritt machst oder eine Online-Funktion nutzt, legt "
                     "die App ein <strong>anonymes Konto</strong> an: eine zufällige Kennung ohne "
                     "E-Mail-Adresse oder Telefonnummer, die an dieser Installation der App hängt.</p>")
        else:
            s.append("<p>Wenn du das Online-Duell oder Einladungen zum ersten Mal nutzt, legt die App ein "
                     "<strong>anonymes Konto</strong> an: eine zufällige Kennung ohne E-Mail-Adresse oder "
                     "Telefonnummer.</p>")
        s.append("<p><strong>Welche Daten:</strong> die anonyme Kennung, der Spielname, den du in der App "
                 "festlegst, Avatar, Rahmen und Level, die gewählte Kategorie, Fragen, deine Antworten "
                 "und Punkte je Runde, Zeitpunkte sowie Verbindungsdaten (IP-Adresse, Zeitpunkt). Dein "
                 "Gegenüber sieht deinen Spielnamen, Avatar, Rahmen, Level und deine Punkte. Bei "
                 "Einladungen speichern wir deinen Einladungscode, welcher Code bei dir eingelöst wurde "
                 "und die daraus gutgeschriebenen Belohnungen.</p>")
        s.append("<p><strong>Wie lange:</strong> Einträge der Spielersuche höchstens einen Tag, "
                 "Duell-Daten sieben Tage nach Spielende. Anonyme Konten löschen wir nach "
                 f"{v(ON['anonymous_account_days'])} Tagen ohne Nutzung, zusammen mit den Daten, die "
                 "daran hängen. Einladungsdaten speichern wir, solange sie für die Gutschrift nötig "
                 f"sind, längstens {v(ON['referral_months'])} Monate.</p>")
        s.append("<p><strong>Rechtsgrundlage:</strong> Erfüllung des Vertrags über die von dir gewählte "
                 "Funktion (Art. 6 Abs. 1 lit. b DSGVO). Für die Übermittlung in die USA gilt das in "
                 "Abschnitt 4 Gesagte.</p>")
        if "question_updates" in f:
            s.append("<p>Über denselben Server lädt die App neue Fragen. Dabei werden außer den technisch "
                     "nötigen Verbindungsdaten (IP-Adresse, Zeitpunkt) keine Daten über dich "
                     "übertragen.</p>")
        nr += 1
    if "online" in f and "rankings" in f:
        vis = html.escape(app.get("rankings_setting_de", "Einstellungen → „In Ranglisten anzeigen“"))
        s.append(f"<h2>{nr}. Ranglisten, Liga, Aufzeichnungen und Herausforderungen</h2>")
        s.append("<p><strong>Ranglisten:</strong> Für die Monatsranglisten (Daily Challenge und Survival) "
                 "gehen an den Server: Startzeit je Runde, Punkte und Antwortzeit der Daily Challenge, "
                 "die Werte eines Survival-Laufs (beantwortete und richtige Fragen, Wiederbelebungen, "
                 "Spielzeit), dein Spielname, Avatar und Rahmen sowie erhaltene Belohnungen. Andere "
                 "sehen deinen Spielnamen (oder „Spieler“ mit einer Nummer), Avatar, Rahmen, Platz "
                 "und Wert.</p>")
        s.append("<p><strong>Liga:</strong> Aus deinen Arena-Duellen berechnet der Server Punkte und "
                 "Ergebnisse je Monat.</p>")
        s.append("<p><strong>Aufzeichnungen:</strong> Findet sich in der Arena kein Live-Gegner, kann die "
                 "App ein beendetes Duell eines echten Spielers abspielen. Dein Spielname, Avatar, "
                 "Rahmen, Level sowie deine Antworten und Antwortzeiten aus einem Duell können so bis "
                 "zu sieben Tage lang anderen gezeigt werden.</p>")
        s.append("<p><strong>Herausforderungen:</strong> Forderst du einen Freund mit einem Code heraus, "
                 "sieht er deinen Spielnamen, Avatar, Rahmen, Level, deine Antworten und dein "
                 "Ergebnis.</p>")
        s.append("<p><strong>Melden:</strong> Spielnamen in Ranglisten lassen sich melden. Wir speichern, "
                 "wer welchen Eintrag gemeldet hat, und prüfen gemeldete Namen.</p>")
        s.append(f"<p><strong>Deine Wahl:</strong> Schaltest du <em>{vis}</em> aus, erscheinst du in "
                 "keiner Rangliste, wirst nicht als Aufzeichnung gezeigt und erhältst keine "
                 "Ranglisten-Belohnungen.</p>")
        s.append("<p><strong>Wie lange:</strong> Ranglisten- und Liga-Daten, Belohnungen und Meldungen "
                 "13 Monate, Aufzeichnungen und Herausforderungen 30 Tage.</p>")
        s.append("<p><strong>Rechtsgrundlage:</strong> Erfüllung des Vertrags über die von dir gewählte "
                 "Funktion (Art. 6 Abs. 1 lit. b DSGVO); für das Prüfen gemeldeter Namen unser "
                 "berechtigtes Interesse an einem fairen und respektvollen Spiel (Art. 6 Abs. 1 lit. f "
                 "DSGVO).</p>")
        nr += 1
    if "online" in f and "cloud_save" in f:
        s.append(f"<h2>{nr}. Sicherung des Spielstands</h2>")
        s.append("<p>Damit dein Fortschritt nicht verloren geht, legt die App eine Kopie deines "
                 "Spielstands auf dem Server ab und gleicht sie beim Start und beim Verlassen der App "
                 "ab: Münzen, Erfahrung und Level, Erfolge, Statistik, freigeschaltete Inhalte, "
                 "Spielname und Avatar, Serien, Tagesaufgaben, Liga-Stand und Bestwerte. Nicht "
                 "gesichert werden Abos (die stellt der Store wieder her), Energie und die "
                 "Einstellungen des Geräts.</p>")
        s.append("<p><strong>Wie lange:</strong> Eine Kopie, die sich 400 Tage nicht geändert hat, "
                 "löschen wir. Mit dem anonymen Konto verschwindet auch die Kopie.</p>")
        s.append("<p><strong>Rechtsgrundlage:</strong> Bereitstellung der App mit gesichertem "
                 "Fortschritt (Art. 6 Abs. 1 lit. b DSGVO).</p>")
        nr += 1
    if app.get("report_question"):
        s.append(f"<h2>{nr}. Fragen melden</h2>")
        s.append("<p>Meldest du eine Frage, öffnet die App dein E-Mail-Programm mit einer vorbereiteten "
                 "Nachricht (Kennung und Text der Frage, deine Anmerkung). Die E-Mail schickst du selbst "
                 "ab. Wir erhalten dann deine E-Mail-Adresse und den Inhalt, nutzen beides nur, um die "
                 "Frage zu prüfen und dir gegebenenfalls zu antworten, und löschen die E-Mail, sobald "
                 "die Meldung erledigt ist. Rechtsgrundlage ist unser berechtigtes Interesse an "
                 "richtigen Fragen (Art. 6 Abs. 1 lit. f DSGVO).</p>")
        nr += 1
    if "local_network" in f:
        s.append(f"<h2>{nr}. Lokales Match im selben WLAN</h2>")
        s.append("<p>Beim lokalen Match verbinden sich die Geräte direkt im selben WLAN. Spielname, "
                 "Avatar und Antworten gehen nur an die beteiligten Geräte, nicht über unsere Server. "
                 "Auf dem iPhone fragt das System dafür nach der Erlaubnis für das lokale Netzwerk.</p>")
        nr += 1
    if "share" in f:
        s.append(f"<h2>{nr}. Teilen</h2>")
        s.append("<p>Wenn du ein Ergebnis oder eine Einladung teilst, öffnet die App das Teilen-Menü "
                 "deines Geräts mit einem Text. Wohin du ihn schickst, entscheidest du. Die App selbst "
                 "überträgt dabei nichts; die gewählte App verarbeitet den Text nach ihren eigenen "
                 "Bedingungen.</p>")
        nr += 1
    s.append(f"<h2>{nr}. Kinder</h2>")
    s.append("<p>Die App richtet sich nicht an Kinder unter 13 Jahren. In Österreich kann man in "
             "personalisierte Werbung erst ab 14 Jahren selbst einwilligen; jüngere Personen brauchen "
             "dafür die Zustimmung der Eltern. <mark class=\"todo\">[Altersgrenze prüfen]</mark></p>")
    nr += 1
    s.append(f"<h2>{nr}. Deine Rechte</h2>")
    hint = ("dein Einladungscode oder die Bestellnummer aus der Kaufbestätigung von Google oder Apple"
            if "online" in f else
            "die Bestellnummer aus der Kaufbestätigung von Google oder Apple")
    s.append("<p>Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der "
             "Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15–21 DSGVO). Eine erteilte "
             "Einwilligung kannst du jederzeit mit Wirkung für die Zukunft widerrufen. Schreib uns "
             f"dazu an {mail('de')}. Weil die App ohne Namen auskommt, hilft uns ein Hinweis, um deine "
             f"Daten zu finden, zum Beispiel {hint}.</p>")
    s.append("<p>Du kannst dich außerdem bei der Österreichischen Datenschutzbehörde beschweren: "
             "Barichgasse 40–42, 1030 Wien, "
             '<a href="https://www.dsb.gv.at">www.dsb.gv.at</a>.</p>')
    nr += 1
    s.append(f"<h2>{nr}. Änderungen</h2>")
    s.append("<p>Wenn sich die App oder die eingesetzten Dienste ändern, passen wir diese Erklärung an. "
             "Es gilt die jeweils hier veröffentlichte Fassung.</p>")
    return "\n".join(s)


def privacy_en(app: dict) -> str:
    f = set(app["features"])
    n = html.escape(app["name"])
    s = []
    s.append(f"<h1>Privacy policy for the app “{n}”</h1>")
    s.append(f'<p class="meta">Last updated: {html.escape(app.get("updated_en", CFG["updated_en"]))}</p>')
    s.append("<h2>1. Who is responsible?</h2>")
    s.append(f"<p>The controller responsible for data processing in the app “{n}” is:</p>")
    s.append(operator_block("en"))
    s.append("<h2>2. The essentials</h2><ul>")
    if "online" in f and "cloud_save" in f:
        s.append("<li>You don’t need an account with a name, email address or password. For the "
                 "online features and the backup of your progress, the app creates an anonymous "
                 "account (section 6).</li>")
    elif "online" in f:
        s.append("<li>You don’t need an account with a name, email address or password. Only for "
                 "online duels and invitations does the app create an anonymous account (section 6).</li>")
    else:
        s.append("<li>You don’t need an account. We never ask for your name or email address.</li>")
    if "cloud_save" in f:
        s.append("<li>Your progress, statistics, coins and settings are stored on your device. A backup "
                 "copy of your progress is kept on our server.</li>")
    else:
        s.append("<li>Your progress, statistics, coins and settings are stored only on your device.</li>")
    s.append("<li>The app shows ads. You decide in the consent dialog whether they are personalized, "
             "and you can change that at any time.</li>")
    s.append("<li>Purchases are handled by Google Play or the App Store. We never receive payment data.</li>")
    s.append("<li>We don’t use any analytics or tracking tools of our own.</li></ul>")

    s.append("<h2>3. Data on your device</h2>")
    if "cloud_save" in f:
        s.append("<p>The app stores your progress, statistics, coins, purchase status and settings locally "
                 "on your device, where they are deleted when you uninstall the app. What is also backed "
                 "up on our server is described below under “Backup of your progress”. The legal basis is "
                 "providing the app you use (Art. 6(1)(b) GDPR, Section 165(3) of the Austrian "
                 "Telecommunications Act 2021).</p>")
    else:
        s.append("<p>The app stores your progress, statistics, coins, purchase status and settings locally "
                 "on your device. This data is not sent to us and is deleted when you uninstall the app. "
                 "The legal basis is providing the app you use (Art. 6(1)(b) GDPR, Section 165(3) of the "
                 "Austrian Telecommunications Act 2021).</p>")

    s.append("<h2>4. Advertising</h2>")
    banner = " (banners and videos)" if "banner" in f else ""
    if "mediation" in f:
        s.append(f"<p>The app is free and funded by advertising{banner}. Ads are delivered by Google AdMob, "
                 "which also works with other ad networks (“mediation”):</p>")
    else:
        s.append(f"<p>The app is free and funded by advertising{banner}. Ads are delivered by Google "
                 "AdMob:</p>")
    s.append(partner_list("en", "mediation" in f))
    s.append("<p><strong>What data:</strong> your device’s advertising ID (on iPhone only if you allow "
             "it in the tracking prompt), IP address and the approximate location derived from it, "
             "information about your device, operating system and app, interactions with ads, and "
             "technical diagnostic data.</p>")
    s.append("<p><strong>What for:</strong> serving ads, limiting how often you see them, preventing "
             "fraud, measuring reach and – only with your consent – tailoring ads to your interests.</p>")
    s.append("<p><strong>Your choice:</strong> On first launch a consent dialog (Google User Messaging "
             "Platform) asks for your choice; on iPhone, Apple’s tracking prompt appears as well. You can "
             f"change or withdraw your choice at any time under <em>{html.escape(app['privacy_setting_en'])}</em>. "
             "Without consent you only see non-personalized ads.</p>")
    s.append(f"<p>Rewarded videos ({html.escape(app['rewarded_en'])}) only play when you start them "
             "yourself.</p>")
    s.append("<p><strong>Legal basis:</strong> your consent (Art. 6(1)(a) GDPR, Section 165(3) of the "
             "Austrian Telecommunications Act 2021) for personalized ads and access to identifiers on "
             "your device; for non-personalized ads, our legitimate interest in offering the app for "
             "free (Art. 6(1)(f) GDPR). Some ad partners process data in the USA. This is based on the "
             "EU adequacy decision for the EU-US Data Privacy Framework where the partner is certified, "
             "otherwise on the European Commission’s standard contractual clauses.</p>")

    if "subscriptions" in f:
        s.append("<h2>5. Purchases and subscriptions</h2>")
        s.append("<p>You pay for purchases and subscriptions through Google Play or Apple’s App Store, "
                 "under their terms. We never receive your payment data.</p>")
    else:
        s.append("<h2>5. Purchases</h2>")
        s.append("<p>You pay for purchases through Google Play or Apple’s App Store, under their terms. "
                 "We never receive your payment data.</p>")
    if "revenuecat" not in f:
        s.append("<p>To unlock purchased content and let you restore it, the app asks the store directly "
                 "which purchases belong to your store account. We don’t use a server of our own or any "
                 "other service provider for this. Google or Apple process the purchase data as "
                 "independent controllers under their own privacy policies. The legal basis is "
                 "performance of the purchase contract (Art. 6(1)(b) GDPR).</p>")
    else:
        s.append("<p>To unlock purchased content and let you restore it, we use <strong>RevenueCat</strong> "
                 '(RevenueCat, Inc., USA, <a href="https://www.revenuecat.com/privacy">privacy policy</a>) as '
                 "a processor. It processes a random, anonymous identifier created by the app, purchase "
                 "details (product, time, price, store transaction ID, subscription status), information "
                 "about your device, operating system and app version, and your IP address. The legal basis "
                 "is performance of the purchase contract (Art. 6(1)(b) GDPR). Transfers to the USA are "
                 "covered as described in section 4.</p>")

    nr = 6
    if "online" in f:
        extra = "rankings" in f or "cloud_save" in f
        s.append(f"<h2>{nr}. {'Server, online duels and invitations' if extra else 'Online duels and invitations'}</h2>")
        uses = ["duels against other players", "invitation codes"]
        if "rankings" in f:
            uses.append("rankings")
        if "cloud_save" in f:
            uses.append("the backup of your progress")
        s.append("<p>For " + ", ".join(uses[:-1]) + " and " + uses[-1] + ", the app uses a server "
                 "run by <strong>Supabase</strong> (Supabase Inc., USA) as a processor. Server location: "
                 f"{v(ON['server_region_en'])}.</p>")
        if "cloud_save" in f:
            s.append("<p>As soon as you make progress in the app or use an online feature, the app "
                     "creates an <strong>anonymous account</strong>: a random identifier without an email "
                     "address or phone number, tied to this installation of the app.</p>")
        else:
            s.append("<p>The first time you use online duels or invitations, the app creates an "
                     "<strong>anonymous account</strong>: a random identifier without an email address or "
                     "phone number.</p>")
        s.append("<p><strong>What data:</strong> the anonymous identifier, the player name you set in the "
                 "app, avatar, frame and level, the chosen category, the questions, your answers and "
                 "points per round, timestamps, and connection data (IP address, time). Your opponent "
                 "sees your player name, avatar, frame, level and points. For invitations we store your "
                 "invitation code, which code was redeemed by you and the rewards credited as a "
                 "result.</p>")
        s.append("<p><strong>How long:</strong> matchmaking entries for at most one day, duel data for "
                 "seven days after the match ends. We delete anonymous accounts after "
                 f"{v(ON['anonymous_account_days'])} days without use, together with the data linked to "
                 "them. We keep invitation data as long as "
                 f"needed to credit rewards, for at most {v(ON['referral_months'])} months.</p>")
        s.append("<p><strong>Legal basis:</strong> performance of the contract for the feature you chose "
                 "(Art. 6(1)(b) GDPR). Transfers to the USA are covered as described in section 4.</p>")
        if "question_updates" in f:
            s.append("<p>The app also downloads new questions from the same server. Apart from the "
                     "technically necessary connection data (IP address, time), no data about you is "
                     "transmitted.</p>")
        nr += 1
    if "online" in f and "rankings" in f:
        vis = html.escape(app.get("rankings_setting_en", "Settings → “Show me in rankings”"))
        s.append(f"<h2>{nr}. Rankings, league, recordings and challenges</h2>")
        s.append("<p><strong>Rankings:</strong> For the monthly rankings (Daily Challenge and Survival), "
                 "the following goes to the server: start time of each round, Daily Challenge points and "
                 "answer time, the values of a Survival run (questions answered and correct, revives, "
                 "playing time), your player name, avatar and frame, and rewards received. Others see "
                 "your player name (or “Player” with a number), avatar, frame, rank and score.</p>")
        s.append("<p><strong>League:</strong> The server calculates monthly points and results from your "
                 "Arena duels.</p>")
        s.append("<p><strong>Recordings:</strong> If no live opponent is found in the Arena, the app may "
                 "replay a finished duel of a real player. Your player name, avatar, frame and level as "
                 "well as your answers and answer times from a duel may be shown to others in this way "
                 "for up to seven days.</p>")
        s.append("<p><strong>Challenges:</strong> If you challenge a friend with a code, they see your "
                 "player name, avatar, frame, level, your answers and your result.</p>")
        s.append("<p><strong>Reporting:</strong> Player names in rankings can be reported. We store who "
                 "reported which entry and review reported names.</p>")
        s.append(f"<p><strong>Your choice:</strong> If you turn off <em>{vis}</em>, you appear in no "
                 "ranking, are not shown as a recording and receive no ranking rewards.</p>")
        s.append("<p><strong>How long:</strong> ranking and league data, rewards and reports for 13 "
                 "months, recordings and challenges for 30 days.</p>")
        s.append("<p><strong>Legal basis:</strong> performance of the contract for the feature you chose "
                 "(Art. 6(1)(b) GDPR); for reviewing reported names, our legitimate interest in fair and "
                 "respectful play (Art. 6(1)(f) GDPR).</p>")
        nr += 1
    if "online" in f and "cloud_save" in f:
        s.append(f"<h2>{nr}. Backup of your progress</h2>")
        s.append("<p>So that your progress isn’t lost, the app keeps a copy of it on the server and syncs "
                 "it when you start and leave the app: coins, experience and level, achievements, "
                 "statistics, unlocked content, player name and avatar, streaks, daily tasks, league "
                 "standing and best scores. Subscriptions (restored by the store), energy and device "
                 "settings are not backed up.</p>")
        s.append("<p><strong>How long:</strong> We delete a copy that hasn’t changed for 400 days. The "
                 "copy is also deleted together with the anonymous account.</p>")
        s.append("<p><strong>Legal basis:</strong> providing the app with saved progress "
                 "(Art. 6(1)(b) GDPR).</p>")
        nr += 1
    if app.get("report_question"):
        s.append(f"<h2>{nr}. Reporting questions</h2>")
        s.append("<p>If you report a question, the app opens your email app with a prepared message "
                 "(question ID and text, your comment). You send the email yourself. We then receive "
                 "your email address and the content, use both only to check the question and reply "
                 "to you if needed, and delete the email once the report has been dealt with. The legal "
                 "basis is our legitimate interest in correct questions (Art. 6(1)(f) GDPR).</p>")
        nr += 1
    if "local_network" in f:
        s.append(f"<h2>{nr}. Local match on the same Wi-Fi</h2>")
        s.append("<p>In a local match, the devices connect directly on the same Wi-Fi network. Player "
                 "name, avatar and answers only go to the participating devices, not through our "
                 "servers. On iPhone, the system asks for permission to access the local network.</p>")
        nr += 1
    if "share" in f:
        s.append(f"<h2>{nr}. Sharing</h2>")
        s.append("<p>When you share a result or an invitation, the app opens your device’s share menu "
                 "with a text. You decide where it goes. The app itself sends nothing; the app you choose "
                 "processes the text under its own terms.</p>")
        nr += 1
    s.append(f"<h2>{nr}. Children</h2>")
    s.append("<p>The app is not directed at children under 13. In Austria, people can consent to "
             "personalized advertising themselves from the age of 14; younger people need their "
             "parents’ consent. <mark class=\"todo\">[check age limit]</mark></p>")
    nr += 1
    s.append(f"<h2>{nr}. Your rights</h2>")
    hint = ("your invitation code or the order number from Google’s or Apple’s purchase receipt"
            if "online" in f else
            "the order number from Google’s or Apple’s purchase receipt")
    s.append("<p>You have the right of access, rectification, erasure, restriction of processing, data "
             "portability and objection (Art. 15–21 GDPR). You can withdraw any consent at any time "
             f"with effect for the future. Just write to {mail('en')}. Since the app works without names, "
             f"a hint helps us find your data, for example {hint}.</p>")
    s.append("<p>You can also lodge a complaint with the Austrian Data Protection Authority: "
             "Barichgasse 40–42, 1030 Vienna, Austria, "
             '<a href="https://www.dsb.gv.at">www.dsb.gv.at</a>.</p>')
    nr += 1
    s.append(f"<h2>{nr}. Changes</h2>")
    s.append("<p>If the app or the services it uses change, we will update this policy. The version "
             "published here applies.</p>")
    return "\n".join(s)


# --------------------------------------------------------------------------
# Support
# --------------------------------------------------------------------------


def support_de(app: dict) -> str:
    f = set(app["features"])
    n = html.escape(app["name"])
    s = [f"<h1>Support für „{n}“</h1>"]
    s.append(f"<p>Du hast eine Frage, ein Problem oder eine Idee? Schreib uns an {mail('de')}. "
             "Hilfreich sind die App-Version (steht in den Einstellungen) und dein Gerätemodell.</p>")
    s.append("<h2>Häufige Fragen</h2>")
    s.append("<h3>Wie stelle ich einen Kauf wieder her?</h3>")
    s.append(f"<p>Öffne <em>{html.escape(app['restore_de'])}</em>. Das funktioniert auch auf einem neuen "
             "Gerät, solange du dasselbe Google- bzw. Apple-Konto nutzt wie beim Kauf.</p>")
    if "subscriptions" in f:
        s.append("<h3>Wie kündige ich ein Abo?</h3>")
        s.append("<p>Abos kündigst du im Store: auf Android im Play Store unter Profilbild → „Zahlungen und "
                 "Abos“ → „Abos“, auf dem iPhone unter Einstellungen → dein Name → „Abonnements“. Das "
                 "Löschen der App kündigt kein Abo.</p>")
    s.append("<h3>Wie ändere ich meine Entscheidung zur Werbung?</h3>")
    s.append(f"<p>Unter <em>{html.escape(app['privacy_setting_de'])}</em> kannst du deine Einwilligung "
             "jederzeit ändern oder widerrufen.</p>")
    s.append("<h3>Kann ich meinen Fortschritt auf ein neues Gerät mitnehmen?</h3>")
    s.append("<p>Derzeit nicht: Fortschritt und Münzen liegen nur auf dem Gerät. Gekaufte Inhalte "
             "kannst du auf dem neuen Gerät wiederherstellen.</p>")
    s.append("<h3>Wie lösche ich meine Daten?</h3>")
    delete = ("<p>Die Daten auf deinem Gerät verschwinden, wenn du die App löschst. ")
    if "online" in f:
        delete += ("Daten aus Online-Duellen löschen wir automatisch nach sieben Tagen. Für alles "
                   "Weitere, etwa Einladungen oder Käufe, schreib uns mit deinem Einladungscode bzw. der "
                   "Bestellnummer.</p>")
    elif "revenuecat" in f:
        delete += "Für Daten zu Käufen schreib uns mit der Bestellnummer aus der Kaufbestätigung.</p>"
    else:
        delete += ("Außerhalb deines Geräts speichern wir keine Daten über dich. Deine Käufe verwaltet "
                   "Google bzw. Apple in deinem Store-Konto.</p>")
    s.append(delete)
    if app.get("report_question"):
        s.append("<h3>Mir ist eine falsche Frage aufgefallen.</h3>")
        s.append("<p>Danke! Schreib uns den Fragetext, die Kategorie und was nicht stimmt. Wir prüfen "
                 "jede Meldung.</p>")
    s.append(f'<p class="links"><a href="privacy.html">Datenschutzerklärung</a> · '
             f'<a href="../imprint.html">Impressum</a></p>')
    return "\n".join(s)


def support_en(app: dict) -> str:
    f = set(app["features"])
    n = html.escape(app["name"])
    s = [f"<h1>Support for “{n}”</h1>"]
    s.append(f"<p>Have a question, a problem or an idea? Write to us at {mail('en')}. It helps if you "
             "include the app version (shown in the settings) and your device model.</p>")
    s.append("<h2>Frequently asked questions</h2>")
    s.append("<h3>How do I restore a purchase?</h3>")
    s.append(f"<p>Open <em>{html.escape(app['restore_en'])}</em>. This also works on a new device, as "
             "long as you use the same Google or Apple account you bought with.</p>")
    if "subscriptions" in f:
        s.append("<h3>How do I cancel a subscription?</h3>")
        s.append("<p>Subscriptions are managed in the store: on Android in the Play Store under your profile "
                 "picture → “Payments & subscriptions” → “Subscriptions”, on iPhone under Settings → your "
                 "name → “Subscriptions”. Deleting the app does not cancel a subscription.</p>")
    s.append("<h3>How do I change my ad choice?</h3>")
    s.append(f"<p>Under <em>{html.escape(app['privacy_setting_en'])}</em> you can change or withdraw your "
             "consent at any time.</p>")
    s.append("<h3>Can I move my progress to a new device?</h3>")
    s.append("<p>Not at the moment: progress and coins are stored only on the device. You can restore "
             "purchased content on the new device.</p>")
    s.append("<h3>How do I delete my data?</h3>")
    delete = "<p>The data on your device is removed when you delete the app. "
    if "online" in f:
        delete += ("We delete online duel data automatically after seven days. For anything else, such "
                   "as invitations or purchases, write to us with your invitation code or order "
                   "number.</p>")
    elif "revenuecat" in f:
        delete += "For purchase data, write to us with the order number from your receipt.</p>"
    else:
        delete += ("We don’t store any data about you outside your device. Your purchases are managed "
                   "by Google or Apple in your store account.</p>")
    s.append(delete)
    if app.get("report_question"):
        s.append("<h3>I found a wrong question.</h3>")
        s.append("<p>Thank you! Send us the question text, the category and what’s wrong. We check every "
                 "report.</p>")
    s.append('<p class="links"><a href="privacy.html">Privacy policy</a> · '
             '<a href="../imprint.html">Imprint</a></p>')
    return "\n".join(s)


# --------------------------------------------------------------------------
# Impressum
# --------------------------------------------------------------------------


def imprint_de() -> str:
    s = ["<h1>Impressum</h1>"]
    s.append("<p>Angaben nach § 5 E-Commerce-Gesetz und Offenlegung nach § 25 Mediengesetz</p>")
    s.append("<h2>Medieninhaber und Diensteanbieter</h2>")
    s.append(operator_block("de"))
    s.append(f"<p><strong>Unternehmensgegenstand:</strong> {v(OP['business_de'])}</p>")
    if OP.get("vat_id"):
        s.append(f"<p><strong>UID-Nummer:</strong> {v(OP['vat_id'])}</p>")
    if OP.get("trade_authority_de"):
        s.append(f"<p><strong>Gewerbebehörde / Kammer:</strong> {v(OP['trade_authority_de'])}</p>")
    names = ", ".join(f"„{html.escape(a['name'])}“" for a in CFG["apps"])
    s.append(f"<p><strong>Grundlegende Richtung:</strong> Informationen zu den Apps {names} sowie "
             "Datenschutzerklärungen und Support.</p>")
    s.append('<p class="links"><a href="index.html">Übersicht</a></p>')
    return "\n".join(s)


def imprint_en() -> str:
    s = ["<h1>Imprint</h1>"]
    s.append("<p>Information under Section 5 of the Austrian E-Commerce Act and disclosure under "
             "Section 25 of the Austrian Media Act</p>")
    s.append("<h2>Media owner and service provider</h2>")
    s.append(operator_block("en"))
    s.append(f"<p><strong>Business purpose:</strong> {v(OP['business_en'])}</p>")
    if OP.get("vat_id"):
        s.append(f"<p><strong>VAT ID:</strong> {v(OP['vat_id'])}</p>")
    if OP.get("trade_authority_en"):
        s.append(f"<p><strong>Trade authority / chamber:</strong> {v(OP['trade_authority_en'])}</p>")
    names = ", ".join(f"“{html.escape(a['name'])}”" for a in CFG["apps"])
    s.append(f"<p><strong>Editorial line:</strong> Information about the apps {names}, privacy policies "
             "and support.</p>")
    s.append('<p class="links"><a href="index.html">Overview</a></p>')
    return "\n".join(s)


def index_de() -> str:
    s = ["<h1>Unsere Apps</h1>", "<ul class=\"apps\">"]
    for a in CFG["apps"]:
        s.append(f'<li><strong>{html.escape(a["name"])}</strong>: '
                 f'<a href="{a["slug"]}/privacy.html">Datenschutzerklärung</a> · '
                 f'<a href="{a["slug"]}/support.html">Support</a></li>')
    s.append("</ul>")
    s.append('<p class="links"><a href="imprint.html">Impressum</a></p>')
    return "\n".join(s)


def index_en() -> str:
    s = ["<h1>Our apps</h1>", "<ul class=\"apps\">"]
    for a in CFG["apps"]:
        s.append(f'<li><strong>{html.escape(a["name"])}</strong>: '
                 f'<a href="{a["slug"]}/privacy.html">Privacy policy</a> · '
                 f'<a href="{a["slug"]}/support.html">Support</a></li>')
    s.append("</ul>")
    s.append('<p class="links"><a href="imprint.html">Imprint</a></p>')
    return "\n".join(s)


# --------------------------------------------------------------------------
# Seitenrahmen
# --------------------------------------------------------------------------

PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{base}style.css">
</head>
<body>
<header>
  <a class="home" href="{base}index.html">{site}</a>
  <nav class="lang" aria-label="Sprache / Language">
    <button type="button" data-lang="de">Deutsch</button>
    <button type="button" data-lang="en">English</button>
  </nav>
</header>
<main>
<section lang="de" class="de">
{de}
</section>
<section lang="en" class="en">
{en}
</section>
</main>
<script>
(function () {{
  var p = new URLSearchParams(location.search).get('lang');
  var lang = p || ((navigator.language || 'en').toLowerCase().indexOf('de') === 0 ? 'de' : 'en');
  function show(l) {{
    document.documentElement.lang = l;
    document.body.setAttribute('data-lang', l);
    document.querySelectorAll('.lang button').forEach(function (b) {{
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === l);
    }});
  }}
  document.querySelectorAll('.lang button').forEach(function (b) {{
    b.addEventListener('click', function () {{ show(b.getAttribute('data-lang')); }});
  }});
  show(lang === 'de' ? 'de' : 'en');
}})();
</script>
</body>
</html>
"""

CSS = """:root { --bg:#f6f7fb; --card:#fff; --text:#1d2433; --muted:#5b6478; --accent:#2f5bd3; --on-accent:#fff; --line:#e3e6ef; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#0e1020; --card:#171a2e; --text:#e8eaf3; --muted:#a3aac0; --accent:#8fb0ff; --on-accent:#0e1020; --line:#2a2f4a; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
header { display:flex; justify-content:space-between; align-items:center; gap:12px;
  max-width:820px; margin:0 auto; padding:16px; }
.home { color:var(--text); font-weight:700; text-decoration:none; }
.lang button { font:inherit; font-size:14px; border:1px solid var(--line); background:var(--card);
  color:var(--text); border-radius:999px; padding:4px 12px; cursor:pointer; }
.lang button[aria-pressed="true"] { background:var(--accent); border-color:var(--accent); color:var(--on-accent); font-weight:600; }
main { max-width:820px; margin:0 auto 48px; padding:8px 24px 32px; background:var(--card);
  border:1px solid var(--line); border-radius:16px; }
@media (max-width: 860px) { main { margin:0 16px 32px; padding:8px 16px 24px; } }
h1 { font-size:1.6rem; line-height:1.3; margin:24px 0 8px; }
h2 { font-size:1.15rem; margin:28px 0 6px; }
h3 { font-size:1rem; margin:20px 0 4px; }
a { color:var(--accent); }
.meta, .links { color:var(--muted); font-size:.95rem; }
mark.todo { background:#ffe08a; color:#1d2433; padding:0 3px; border-radius:3px; }
ul.apps { padding-left:20px; }
body[data-lang="de"] section.en, body[data-lang="en"] section.de { display:none; }
"""


def page(path: str, title: str, de: str, en: str) -> None:
    depth = path.count("/")
    base = "../" * depth
    site = "Apps"
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PAGE.format(title=html.escape(title), base=base, site=site, de=de, en=en),
                      encoding="utf-8", newline="\n")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "style.css").write_text(CSS, encoding="utf-8", newline="\n")
    # GitHub Pages: keine Jekyll-Verarbeitung.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    page("index.html", "Apps", index_de(), index_en())
    page("imprint.html", "Impressum / Imprint", imprint_de(), imprint_en())
    for app in CFG["apps"]:
        page(f"{app['slug']}/privacy.html", f"{app['name']} – Datenschutz / Privacy",
             privacy_de(app), privacy_en(app))
        page(f"{app['slug']}/support.html", f"{app['name']} – Support",
             support_de(app), support_en(app))
    todos = sum(p.read_text(encoding="utf-8").count('class="todo"') for p in OUT.rglob("*.html"))
    print(f"Seiten in {OUT}: {len(list(OUT.rglob('*.html')))}, offene Platzhalter: {todos}")


if __name__ == "__main__":
    main()
