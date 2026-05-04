# Local Demo Frontend

This folder contains a simple browser-based chat demo that runs locally against a backend API.

The frontend is made up of:
- `index.html` for the page structure
- `chat.js` for chat behavior and streaming responses
- `style.css` for layout and styling

## How to run locally

1. Start the backend API.
   - By default, the example page expects the API at `http://127.0.0.1:8000/ask` and `http://127.0.0.1:8000/ask_stream`.
2. Serve this `examples/` folder with a static file server.
   - For example:
     ```bash
     cd examples
     python -m http.server 5500
     ```
3. Open the demo in your browser.
   - Visit `http://localhost:5500/index.html`

## Customizing the demo

- Update the `data-api`, `data-client`, and `data-greeting` attributes in `index.html` to point at your own backend or change the opening message.
- Edit the starter prompt buttons in `index.html` to match your use case.
- Modify `chat.js` if you want to change the streaming behavior, formatting, or typing indicator.
- Adjust `style.css` to change colors, spacing, and layout.

## Notes

- The frontend expects the API to support both a standard chat endpoint and a streaming endpoint.
- If you change the backend route names or host, update `data-api` and the fetch logic in `chat.js` accordingly.
