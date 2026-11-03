# Décisions d'architecture

Chaque décision garde le raisonnement : le contexte, le choix, pourquoi, ce qui a été écarté et ce que ça implique.

## 2026-10-28 : convention de topics MQTT

**Contexte** : ceux qui publient (ESP32) et ceux qui écoutent (ingest, Node-RED) doivent s'accorder sur les noms. Chacun doit pouvoir deviner où se trouve le CO2 de la chambre sans lire le code.

**Décision** : `bt/<bâtiment>/<pièce>/<point>`, par exemple `bt/home/r1-chambre-03/co2`. Le dernier niveau est le point mesuré (`co2`, `temperature`), pas le nom du capteur. Le payload est la valeur brute, sans JSON. Les diagnostics matériels (`wifi_signal`, `uptime`) vont sous `bt/home/node-01/...`.

**Pourquoi** : c'est lisible et prévisible. Le topic décrit ce qu'on mesure, pas le matériel : si je change de puce, le topic ne change pas.

**Écarté** :
- Payload JSON : l'horodatage est posé par l'ingest, et l'unité est une propriété du point, pas du message. Le JSON n'apportait rien de plus et compliquait l'ESP32 et Node-RED.
- Nom de pièce `chambre-V` : la majuscule casse la règle (les topics sont sensibles à la casse), et le nom dépend de l'occupant. Si je change de chambre, il faut tout renommer.
- `wifi_signal` rangé sous la pièce où se trouve la box : c'est une mesure du matériel, pas de la pièce.

**Conséquences** :
- L'ingest lit le bâtiment, la pièce et le point directement dans le topic (`split('/')`).
- Il est abonné à `bt/home/+/+` : les diagnostics, qui ont plus de niveaux, sont filtrés par la forme du topic.
- L'unité doit être connue ailleurs (`UNITES` dans l'ingest, plus tard une table des points).
- Projet école : `+` est un joker MQTT, interdit dans un topic publié. `R+1` devient donc `r1` (minuscules, `+` supprimé), par exemple `bt/ycampus/r1-salle-101/co2`.

## 2026-10-31 : notifications avec ntfy.sh

**Contexte** : recevoir sur mon téléphone une alerte quand le CO2 dépasse 1000 ppm, et un message « ok » quand il redescend sous 900 ppm.

**Décision** : ntfy.sh public. Node-RED envoie un POST HTTP, l'application ntfy du téléphone reçoit la notification.

**Pourquoi** : très simple à mettre en place. Pas de compte, pas de token, un seul POST.

**Écarté** :
- Telegram : manipulations en plus (créer un bot, gérer un token).
- ntfy hébergé chez moi : un service de plus à faire tourner, pas utile à ce stade.

**Conséquences** :
- Toute personne qui connaît le nom du topic peut lire mes notifications. Le topic est donc une suite aléatoire, gardée dans `.env` (variable `NTFY_TOPIC`) et jamais dans le dépôt.
- Si ntfy.sh ou ma connexion internet tombe, je ne reçois plus rien. Il n'y a pas de solution de secours.
- Les messages passent par un serveur tiers.

## 2026-11-01 : utilisateur Postgres en lecture seule pour Grafana

**Contexte** : Grafana se connectait à la base avec l'utilisateur créé par `POSTGRES_USER`, qui est un superutilisateur et peut tout faire, y compris `DELETE` ou `DROP TABLE`. Grafana n'a besoin que de lire.

**Décision** : un rôle `grafana_reader` avec `CONNECT` sur la base `building_twin`, `USAGE` sur le schéma `public` et `SELECT` sur la table `measurements`. Son mot de passe est dans `.env` (variable `POSTGRES_PASSWORD_GRAFANA`). Le mot de passe du superutilisateur n'est plus transmis au conteneur Grafana.

**Pourquoi** : principe du moindre privilège. Si Grafana est compromis, ou si une mauvaise requête est tapée dans un panneau, il ne doit pas devenir une porte d'entrée (backdoor) avec tous les droits sur TimescaleDB.

**Écarté** : garder le superutilisateur pour Grafana. C'est plus simple, mais tous les droits restent exposés.

**Conséquences** :
- `grafana_reader` dans le le depôt du projet. Après un clone ou un `down -v`, il se rajoute à nouveau au docker compose up grâce au script d'init dans `sql/`.
- Le `SELECT` ne porte que sur `measurements`. Si je crée une 2e table, Grafana ne pourra pas la lire tant que je ne lui aurai pas donné un nouveau `GRANT`.
