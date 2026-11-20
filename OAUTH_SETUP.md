# Social sign-in setup

The app supports Google, X, and Apple OAuth sign-in. Password-based sign-in remains available. Provider buttons appear only after the matching credentials are configured.

Configure these environment variables locally in a `.env` file (which is ignored by Git) or in the Render service's Environment settings:

- Google: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- X: `X_CLIENT_ID`, `X_CLIENT_SECRET`
- Apple: `APPLE_CLIENT_ID`, `APPLE_CLIENT_SECRET`

For the deployed Google and X buttons, create OAuth clients with Google Cloud and X Developer Console, then add the corresponding client ID and secret in the Render service's **Environment** settings. The Render Blueprint declares these four values as unsynced secrets so they are not stored in this repository. Save the values and redeploy the service; the buttons become active when both values for a provider are present.

Register the matching callback URL with each provider. Replace `<your-render-host>` with the service hostname Render assigns:

- `https://<your-render-host>/auth/google/callback`
- `https://<your-render-host>/auth/x/callback`
- `https://<your-render-host>/auth/apple/callback`

For local Google/X development, use `http://127.0.0.1:5000/auth/<provider>/callback` if the provider permits localhost callbacks. Apple web sign-in requires a verified HTTPS domain and an Apple Services ID; its client secret is a signed JWT generated from an Apple private key.

The X integration uses OAuth 2.0 Authorization Code with PKCE and requests only `users.read` to identify the account. X currently documents pay-per-use pricing for user reads, so check the Developer Console's current pricing before enabling it. The app does not store provider access tokens.

Google sign-in covers Google accounts (including Gmail). There is no separate Google Play sign-in provider.
