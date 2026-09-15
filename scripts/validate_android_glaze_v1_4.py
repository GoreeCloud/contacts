#!/usr/bin/env python3
"""Fail-closed validation for GoreeCloud Contacts Android GLAZE UI V1.4.x adoption."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "clients/android/app/src/main/java/com/goreecloud/contacts/GlazeContactsTheme.kt"
MAIN = ROOT / "clients/android/app/src/main/java/com/goreecloud/contacts/MainActivity.kt"
READ_CONTRACT = ROOT / "clients/android/app/src/main/java/com/goreecloud/contacts/CardDavReadContract.kt"
RESPONSE_CONTRACT = ROOT / "clients/android/app/src/main/java/com/goreecloud/contacts/CardDavResponseContract.kt"
MANIFEST = ROOT / "clients/android/app/src/main/AndroidManifest.xml"
DOC = ROOT / "docs/glaze-ui-v1.4-android-adoption.md"
ANDROID_README = ROOT / "clients/android/README.md"
VERSION = "1.4.1"
REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"
ROLLBACK_VERSION = "1.4.0"


def require(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        raise SystemExit(f"{label}: required fragment missing: {fragment!r}")


def forbid(text: str, fragment: str, label: str) -> None:
    if fragment in text:
        raise SystemExit(f"{label}: forbidden fragment present: {fragment!r}")


def main() -> None:
    theme = THEME.read_text(encoding="utf-8")
    main_source = MAIN.read_text(encoding="utf-8")
    read_contract = READ_CONTRACT.read_text(encoding="utf-8")
    response_contract = RESPONSE_CONTRACT.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    android_readme = ANDROID_README.read_text(encoding="utf-8")

    require(theme, f'VERSION = "{VERSION}"', "theme")
    require(theme, f'REFERENCE_REVISION = "{REVISION}"', "theme")
    require(theme, f'ROLLBACK_VERSION = "{ROLLBACK_VERSION}"', "theme")
    require(theme, 'ADOPTION_STATE = "ADOPTION_IN_PROGRESS"', "theme")
    for flag in (
        "OPTICAL_ENGINE_ACCEPTED",
        "REDUCED_TRANSPARENCY_ACCEPTED",
        "INCREASED_CONTRAST_ACCEPTED",
        "PHYSICAL_DEVICE_ACCEPTED",
        "HUMAN_VISUAL_ACCEPTED",
    ):
        require(theme, f"{flag} = false", "theme")
    require(main_source, "GlazeContactsTheme", "MainActivity")
    require(doc, "Radicale/CardDAV remains the sole authoritative contact store", "documentation")
    require(doc, REVISION, "documentation")
    require(doc, "Shared V1.4.1 qualification does not establish Contacts-local acceptance", "documentation")

    require(read_contract, 'responseAcceptance = CardDavReadContractState.SOURCE_READY', "read contract")
    require(read_contract, 'nativeIdentitySession = CardDavReadContractState.IDENTITY_BLOCKED', "read contract")
    require(read_contract, 'networkTransport = CardDavReadContractState.TRANSPORT_BLOCKED', "read contract")

    for fragment in (
        'ADDRESS_BOOK_FIELDS = setOf("href", "display_name")',
        "CONTACT_SUMMARY_FIELDS",
        "CONTACT_DETAIL_FIELDS",
        "contact href does not match request",
        "duplicate address-book href",
        "duplicate contact href",
        "href is a scheme-relative authority",
        "unexpectedFields",
    ):
        require(response_contract, fragment, "response contract")
    for forbidden in (
        "HttpURLConnection",
        "OkHttp",
        "android.net.",
        "java.net.http",
    ):
        forbid(response_contract, forbidden, "response contract")

    forbid(manifest, "android.permission.INTERNET", "manifest")
    forbid(manifest, "android.permission.READ_CONTACTS", "manifest")
    forbid(manifest, "android.permission.WRITE_CONTACTS", "manifest")
    require(manifest, 'android:allowBackup="false"', "manifest")

    require(android_readme, "CardDAV response acceptance", "Android README")
    require(android_readme, "no network authority", "Android README")
    require(android_readme, "GLAZE UI V1.4.1", "Android README")

    print(
        "Contacts Android GLAZE UI V1.4.1 adoption validated: "
        f"version={VERSION} revision={REVISION} rollback={ROLLBACK_VERSION} "
        "responseAcceptance=source-ready network=false providerAuthority=false "
        "consumerAcceptance=false production=false"
    )


if __name__ == "__main__":
    main()
