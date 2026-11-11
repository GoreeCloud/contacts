# GoreeCloud Contacts — Android client

The **native Android Kotlin app** remains in this repository's existing root Gradle project, under [app/](../app/), with [build.gradle.kts](../build.gradle.kts), [settings.gradle.kts](../settings.gradle.kts), the existing Android CI and its original Git history. This layout is retained to avoid disruptive package, signing or build-path changes while adding web and Linux.

Package ID: com.goreecloud.contacts. Minimum API 26, target SDK 35. The Android client reads the device Contacts Provider only after explicit READ_CONTACTS permission; it does not use browser IndexedDB or Linux SQLite. No INTERNET, WRITE_CONTACTS, CardDAV or background sync permissions have been introduced.

Build from the repository root: `gradle :app:testDebugUnitTest :app:assembleDebug :app:lintDebug`.

See the [Android feature register](../docs/FEATURES.md), [platform matrix](../docs/PLATFORMS.md) and [license](../LICENSE). Any Android APK offered for installation or testing must be delivered as a verified standalone APK in the authorized GoreeCloud Google Drive Artifacts folder. Real-device, accessibility, signing and Stable release gates remain open.
