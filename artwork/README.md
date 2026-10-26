# Launcher artwork

Ryan can commit his own artwork here. The shared-library updater copies these assets from upstream main, and applies changed images to the local Steam shortcut on launch when the local CEF endpoint is available. Existing per-title Steam artwork sync carries artwork through the configured rom-artwork share; Steam shortcut IDs stay local to each machine.

| File | Purpose | Suggested canvas |
| --- | --- | --- |
| `portrait.png` | Library cover | 600 × 900 |
| `landscape.png` | Library horizontal capsule | 920 × 430 |
| `hero.png` | Library background | 3840 × 1240 |
| `logo.png` | Transparent game logo | 1280 × 720 |
| `icon.png` | Shortcut icon | 256 × 256 |

PNG and JPG are supported by the installer; use PNG for transparency. These are launcher deliverables, not a complete Steam store submission checklist. Check the current [Steam graphical asset specifications](https://partner.steamgames.com/doc/store/assets) when preparing a store release. The desktop's initial artwork is an unedited game screenshot in its shared library, explicitly temporary; no generated branding is presented as Ryan's art.

A practical publication sequence is a GitHub draft release for review, an itch.io project with versioned builds (optionally uploaded using butler), then a Steamworks release if Ryan wants the full store/onboarding route. Heroic is primarily a launcher for Epic/GOG/Amazon libraries and can launch custom local games; it is not itself a new-game publishing storefront. No store accounts, purchases or public release are created by this PR.
