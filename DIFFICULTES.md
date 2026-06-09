# Difficultés rencontrées

Mise en service de la génération de rapport par le LLM Gemini.

## 1. Les erreurs Gemini étaient avalées silencieusement

Le `except Exception` de `generate_report_content` attrapait toute erreur et
renvoyait un faux succès (HTTP 200 + texte générique). Clé invalide, panne
réseau, quota dépassé, JSON malformé produisaient tous le **même** message —
diagnostic impossible.

**Résolu** : log du vrai stacktrace (`logger.exception`). C'est cette correction
qui a rendu visible la cause réelle du blocage ci-dessous.

## 2. `gemini-2.0-flash` n'a plus de quota gratuit (HTTP 429, `limit: 0`)

Une fois la clé en place, l'appel échouait en `429 RESOURCE_EXHAUSTED`,
`limit: 0` sur `gemini-2.0-flash`. Le piège : la clé était **valide**, le réseau
OK, le code correct — rien ne pointait vers le modèle. `limit: 0` signifie
*aucun quota alloué*, pas « épuisé pour aujourd'hui ».

**Diagnostic** : la clé donne accès à 54 modèles ; un test sur `gemini-2.5-flash`
répond immédiatement. Le verrou était spécifique à `2.0-flash`.

**Résolu** : bascule sur `gemini-2.5-flash`, rendu configurable via `GEMINI_MODEL`
(le quota dépend du modèle ; coder un modèle en dur est fragile).

## 3. Rate limit / quota du free tier (HTTP 429, ~1 génération sur 2 en échec)

En usage réel, la génération échouait par intermittence (~1 sur 2). Cause : le
free tier impose un rate limit par minute **et** un quota de **20 requêtes par
jour** par modèle. Au-delà, Gemini renvoie `429 RESOURCE_EXHAUSTED` ; le backend
l'avalait et affichait « Erreur ». Reproduit : 8 requêtes simultanées → 5 échecs.

**Résolu (pics par minute)** : retry automatique avec backoff sur les 429
(3 tentatives), et `thinking` désactivé (`thinking_budget=0`) pour accélérer et
consommer moins de tokens.

**Limite restante** : le quota *journalier* ne se contourne pas par du code —
soit basculer `GEMINI_MODEL` sur un modèle au quota séparé (ex.
`gemini-2.5-flash-lite`), soit passer au tier payant.

---

**Résultat** : génération opérationnelle et robuste aux pics de rate limit
(`gemini-2.5-flash`, ou `gemini-2.5-flash-lite` selon le quota).
