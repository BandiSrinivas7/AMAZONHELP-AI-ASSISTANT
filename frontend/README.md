# AmazonHelp AI Frontend

A standalone, responsive Amazon-inspired customer-support UI based on the supplied screenshot.

## Run

Open `index.html` directly, or serve this folder with any static server:

```bash
python -m http.server 5500
```

Then open `http://localhost:5500`.

The frontend calls the backend at `http://localhost:8000`. To change it without editing code:

```js
localStorage.setItem("amazonhelp_api", "http://YOUR_HOST:8000")
```

## Included UI

- Amazon-style dark header, search, navigation and footer
- Deal/category cards inspired by the supplied screenshot
- AmazonHelp AI support panel
- Suggested support prompts
- Live intent/confidence/decision display
- Grounded draft reply and retrieved evidence display
- Responsive mobile layout
