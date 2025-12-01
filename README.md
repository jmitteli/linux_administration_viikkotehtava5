# linux_administration_viikkotehtava5
# Viikkotehtävä: MQTT Chat + Docker + MySQL + Nginx reverse proxy

## Tehtävänanto (lyhyesti)
Tässä tehtävässä hyödynnetään aiemmin rakennettua LEMP-stack -arkkitehtuuria (Nginx portissa 80) ja varmistetaan, että Docker-kontissa pyörivä MQTT Chat -sovellus on nähtävissä polussa:

- `http://<VPS-IP>/chat`

Tehtävässä harjoitellaan:
- Docker-konttien käyttöä (Docker Compose)
- MQTT-brokerin (Mosquitto) käyttöä WebSocket-tuen kanssa
- MQTT-viestien tallentamista MySQL-tietokantaan
- Viestihistorian hakemista tietokannasta ja näyttämistä chat-sivulla sivun uudelleenlatauksen jälkeen
- Nginx reverse proxy -asetuksia (HTTP + WebSocket)

Pisteytys:
- Kontti-sovellus toimii ohjeistuksen mukaan ja viestejä voidaan lähettää sovelluksessa (+5p)
- Viestit tallentuvat tietokantaan ja vähintään 10 viimeisintä viestiä näkyy sovelluksessa uudelleenlatauksen jälkeen (+3p)

---

## Mitä tein (yhteenveto)

### 1) Docker ja Docker Compose -ympäristö
- Varmistin että Docker on asennettuna ja toimii (`docker --version`).
- Käynnistin MQTT Chat -kokonaisuuden Docker Composella.
- Ratkaisin virheet compose-tiedostosta:
  - `services.image must be a mapping` / `services.restart must be a mapping` → YAML-sisennysten ja muotoilun korjaus.
- Ratkaisin oikeusongelman:
  - `permission denied while trying to connect to the Docker API`
  - käytin `sudo docker compose up -d` (vaihtoehtoisesti olisi voinut lisätä käyttäjän docker-ryhmään).

### 2) MQTT-brokeri (Mosquitto) ja WebSocket-yhteys
- MQTT toimii portissa 1883 (sisäinen broker-yhteys)
- WebSocket-liittymä toimii portissa 9001 (MQTT over WebSockets)
- Chat-sivu yhdistää MQTT:hen selaimesta.

### 3) Chat-käyttöliittymä (HTML/JS)
- Chat UI toteutettu staattisena `index.html`-sivuna.
- Sivu:
  - muodostaa MQTT-yhteyden
  - tilaa aiheen `chat/messages`
  - lähettää viestit JSON-muodossa (nickname, text, clientId, timestamp)
  - näyttää reaaliaikaiset viestit chat-ikkunassa

### 4) MySQL-tietokanta viestien tallennukselle
- Käytin MySQL:ää viestien tallentamiseen.
- Tein taulun `messages` (id, nickname, message, client_id, created_at tms.).
- Varmistin SQL:llä että viestejä tallentuu.

