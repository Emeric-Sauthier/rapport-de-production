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

---

**Résultat** : génération de rapport opérationnelle (`gemini-2.5-flash`).
