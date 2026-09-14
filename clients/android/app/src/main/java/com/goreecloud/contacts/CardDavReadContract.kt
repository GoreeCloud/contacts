package com.goreecloud.contacts

import java.net.URLEncoder
import java.nio.charset.StandardCharsets

/** Source-level readiness for the native read path. This does not mean transport is active. */
enum class CardDavReadContractState {
    SOURCE_READY,
    IDENTITY_BLOCKED,
    TRANSPORT_BLOCKED,
}

data class CardDavReadContractSnapshot(
    val addressBookDiscovery: CardDavReadContractState,
    val contactListing: CardDavReadContractState,
    val contactDetail: CardDavReadContractState,
    val responseAcceptance: CardDavReadContractState,
    val nativeIdentityBindingContract: CardDavReadContractState,
    val nativeIdentitySession: CardDavReadContractState,
    val networkTransport: CardDavReadContractState,
)

/**
 * Pure Android-side model of the existing GoreeCloud Contacts read-only API surface.
 *
 * Radicale/CardDAV remains authoritative. These helpers only construct same-application relative
 * paths; they never accept or derive another host, credential, user identity, or CardDAV origin.
 */
object CardDavReadContract {
    const val ADDRESS_BOOKS_PATH = "/api/carddav/address-books"
    const val CONTACTS_PATH = "/api/carddav/contacts"
    const val CONTACT_PATH = "/api/carddav/contact"

    private const val MAX_HREF_LENGTH = 4096

    fun contactsPath(addressBookHref: String): String =
        "$CONTACTS_PATH?address_book_href=${encodeHref(requireCardDavHref(addressBookHref))}"

    fun contactDetailPath(contactHref: String): String =
        "$CONTACT_PATH?href=${encodeHref(requireCardDavHref(contactHref))}"

    fun readiness(): CardDavReadContractSnapshot = CardDavReadContractSnapshot(
        addressBookDiscovery = CardDavReadContractState.SOURCE_READY,
        contactListing = CardDavReadContractState.SOURCE_READY,
        contactDetail = CardDavReadContractState.SOURCE_READY,
        responseAcceptance = CardDavReadContractState.SOURCE_READY,
        nativeIdentityBindingContract = CardDavReadContractState.SOURCE_READY,
        nativeIdentitySession = CardDavReadContractState.IDENTITY_BLOCKED,
        networkTransport = CardDavReadContractState.TRANSPORT_BLOCKED,
    )

    private fun requireCardDavHref(value: String): String {
        require(value.isNotBlank()) { "CardDAV href must be non-blank" }
        require(value.length <= MAX_HREF_LENGTH) { "CardDAV href exceeds $MAX_HREF_LENGTH characters" }
        require(value.none(Char::isISOControl)) { "CardDAV href must not contain control characters" }
        require(value == value.trim()) { "CardDAV href must already be canonical; trimming is not allowed" }
        require(value.startsWith('/')) { "CardDAV href must be a server-relative path" }
        require(!value.startsWith("//")) { "CardDAV href must not be a scheme-relative authority" }
        return value
    }

    private fun encodeHref(value: String): String =
        URLEncoder.encode(value, StandardCharsets.UTF_8).replace("+", "%20")
}
