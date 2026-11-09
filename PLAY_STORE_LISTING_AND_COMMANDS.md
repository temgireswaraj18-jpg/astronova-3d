# GOOGLE PLAY STORE COPY-PASTE KIT (ASTRONOVA 3D)

## 1. App Title (Max 30 Characters)
Astronova 3D: Solar System Lab

## 2. Short Description (Max 80 Characters — Exact Length: 78 chars)
Interactive 2D/3D Solar System, Kepler's 3 Laws & Vis-Viva Physics Observatory

## 3. Full Description (Copy-paste directly into Play Console)
Explore the real-time mechanics of our Solar System and master Kepler's Laws of Planetary Motion in interactive 2D and 3D!

ASTRONOVA 3D is a hands-on astrophysics observatory and orbital mechanics sandbox built for students, teachers, space enthusiasts, and curious minds. Powered by an exact Newton-Raphson Keplerian solver and the Vis-Viva orbital energy equation, every planet and comet moves according to true celestial physics.

KEY FEATURES:
• Smart Presence 2D & 3D Viewport: Hold your phone to explore tilted 3D orbital planes (including Halley's Comet at 18° inclination), or lay your device flat on your desk to automatically switch to a clean 2D Top-Down Blueprint Map!
• Kepler's First Law (Law of Ellipses): Visualize the Sun at primary focus F1, the Empty Focus F2, and watch live telemetry prove that r1 + r2 = 2a stays constant at every point on the orbit.
• Kepler's Second Law (Law of Equal Areas): Compare live equal-time swept area wedges at Perihelion and Aphelion to see why planets accelerate close to the Sun and coast slowly when far away.
• Kepler's Third Law (Harmonic Law): Verify T² / a³ across Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Halley's Comet, and custom Exoplanets.
• Live Vis-Viva Telemetry: Track instantaneous orbital speed (km/s), heliocentric distance (AU), areal velocity (AU²/yr), and orbital period in real time.
• Exoplanet Sandbox: Customize orbital eccentricity (e) and semi-major axis (a) with live sliders to design your own extreme planetary systems.
• Built-In User Guide & Mastery Quiz: Test your astrophysics intuition with interactive review questions and clear formula breakdowns.
• 100% Privacy-Friendly (No Login Required): Start exploring immediately with zero account sign-ups.

---

## 4. Keystore Generation & AAB Signing Commands (Checklist #2 & #3)
Run these two commands in your terminal once you download `astronova-release-aab` from GitHub Actions:

```bash
# 1. Generate your Upload Keystore (Back this file up safely in Google Drive + USB!)
keytool -genkey -v -keystore astronova-upload.keystore -alias astronova -keyalg RSA -keysize 2048 -validity 10000

# 2. Sign the Release AAB for Google Play Console upload
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore astronova-upload.keystore astronova-1.0.0-arm64-v8a_armeabi-v7a-release.aab astronova
```

---

## 5. Google Play Console "Data Safety" Form Answers
- **Does your app collect or share any of the required user data types?** -> YES (Because of Google AdMob SDK).
- **Is all of the user data collected by your app encrypted in transit?** -> YES (AdMob uses HTTPS/TLS).
- **Do you provide a way for users to request that their data is deleted?** -> Select "No, my app does not allow users to create an account" (No login!).
- **Data Types to Check:**
  - `Device or other IDs` -> Collected & Shared (by Google AdMob for Analytics & Advertising/Marketing).
  - `Approximate Location` (IP-based via AdMob) -> Collected & Shared (for Advertising/Marketing).
