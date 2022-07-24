# fifa-wc2022-tickets-checker

Yandex.Cloud function implementation for checking FIFA World Cup tickets availability.

- Gets available tickets' categories from the official FIFA site.
- Compares actual data with the latest state.
- Uses YDB in order to store the state.
- Notifies about changes via Telegram API
