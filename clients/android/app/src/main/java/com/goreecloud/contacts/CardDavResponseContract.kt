package com.goreecloud.contacts

/** Transport-neutral models for the existing read-only Contacts API. */
data class AddressBookWire(val href: String, val displayName: String)

data class ContactSummaryWire(
    val href: String,
    val etag: String?,
    val uid: String?,
    val formattedName: String,
    val emails: List<String>,
    val phones: List<String>,
    val organization: String?,
    val title: String?,
    val categories: List<String>,
    val favorite: Boolean,
    val hasPhoto: Boolean,
)

data class StructuredNameWire(
    val familyName: String = "",
    val givenName: String = "",
    val additionalNames: String = "",
    val honorificPrefixes: String = "",
    val honorificSuffixes: String = "",
)

data class PostalAddressWire(
    val types: List<String> = emptyList(),
    val poBox: String = "",
    val extendedAddress: String = "",
    val streetAddress: String = "",
    val locality: String = "",
    val region: String = "",
    val postalCode: String = "",
    val country: String = "",
)

data class ContactDetailWire(
    val summary: ContactSummaryWire,
    val structuredName: StructuredNameWire,
    val addresses: List<PostalAddressWire>,
    val birthday: String?,
    val websites: List<String>,
    val note: String?,
    val photo: String?,
)

sealed interface CardDavResponseDecision {
    data class Accepted(val itemCount: Int) : CardDavResponseDecision
    data class Rejected(val reason: String) : CardDavResponseDecision
}

/**
 * Fail-closed consumer policy for the existing session-bound Contacts API.
 *
 * This contract performs no HTTP, authentication, credential handling, JSON parsing, storage,
 * provider writes, or synchronization. A future exact-field decoder must reject unknown fields
 * with these allowlists before supplying typed values here. Radicale/CardDAV remains authoritative.
 */
object CardDavResponseContract {
    val ADDRESS_BOOK_FIELDS = setOf("href", "display_name")
    val CONTACT_SUMMARY_FIELDS = setOf(
        "href", "etag", "uid", "formatted_name", "emails", "phones", "organization", "title",
        "categories", "favorite", "has_photo",
    )
    val STRUCTURED_NAME_FIELDS = setOf(
        "family_name", "given_name", "additional_names", "honorific_prefixes", "honorific_suffixes",
    )
    val POSTAL_ADDRESS_FIELDS = setOf(
        "types", "po_box", "extended_address", "street_address", "locality", "region",
        "postal_code", "country",
    )
    val CONTACT_DETAIL_FIELDS = CONTACT_SUMMARY_FIELDS + setOf(
        "structured_name", "addresses", "birthday", "websites", "note", "photo",
    )

    private const val MAX_HREF_LENGTH = 4096
    private const val MAX_DISPLAY_NAME = 1024
    private const val MAX_FORMATTED_NAME = 512
    private const val MAX_TEXT = 10_000
    private const val MAX_PHOTO_REFERENCE = 2_000_000
    private const val MAX_LIST_ITEMS = 256
    private const val MAX_ADDRESSES = 64

    fun unexpectedFields(actual: Set<String>, allowed: Set<String>): Set<String> = actual - allowed

    fun acceptAddressBooks(items: List<AddressBookWire>): CardDavResponseDecision {
        if (items.size > MAX_LIST_ITEMS) return reject("too many address books")
        if (items.map { it.href }.toSet().size != items.size) return reject("duplicate address-book href")
        items.forEachIndexed { index, item ->
            validateHref(item.href)?.let { return reject("addressBook[$index]: $it") }
            if (!validText(item.displayName, MAX_DISPLAY_NAME, allowEmpty = false)) {
                return reject("addressBook[$index]: display_name is invalid")
            }
        }
        return CardDavResponseDecision.Accepted(items.size)
    }

    fun acceptContactList(
        expectedAddressBookHref: String,
        items: List<ContactSummaryWire>,
    ): CardDavResponseDecision {
        validateHref(expectedAddressBookHref)?.let { return reject("expected address book href: $it") }
        if (items.size > MAX_LIST_ITEMS) return reject("too many contacts")
        if (items.map { it.href }.toSet().size != items.size) return reject("duplicate contact href")
        items.forEachIndexed { index, item ->
            validateSummary(item)?.let { return reject("contact[$index]: $it") }
        }
        return CardDavResponseDecision.Accepted(items.size)
    }

    fun acceptContactDetail(
        expectedContactHref: String,
        item: ContactDetailWire,
    ): CardDavResponseDecision {
        validateHref(expectedContactHref)?.let { return reject("expected contact href: $it") }
        validateSummary(item.summary)?.let { return reject("contact: $it") }
        if (item.summary.href != expectedContactHref) return reject("contact href does not match request")
        validateStructuredName(item.structuredName)?.let { return reject("structured_name: $it") }
        if (item.addresses.size > MAX_ADDRESSES) return reject("too many postal addresses")
        item.addresses.forEachIndexed { index, address ->
            validateAddress(address)?.let { return reject("address[$index]: $it") }
        }
        if (item.birthday != null && !validOptionalText(item.birthday, 64)) return reject("birthday is invalid")
        if (!validStringList(item.websites, MAX_LIST_ITEMS, 4096)) return reject("websites are invalid")
        if (item.note != null && !validOptionalText(item.note, MAX_TEXT, preserveOuterWhitespace = true)) {
            return reject("note is invalid")
        }
        if (item.photo != null && !validOptionalText(item.photo, MAX_PHOTO_REFERENCE, preserveOuterWhitespace = true)) {
            return reject("photo is invalid")
        }
        return CardDavResponseDecision.Accepted(1)
    }

    private fun validateSummary(item: ContactSummaryWire): String? {
        validateHref(item.href)?.let { return it }
        if (item.etag != null && !validOptionalText(item.etag, 2048)) return "etag is invalid"
        if (item.uid != null && !validOptionalText(item.uid, 2048)) return "uid is invalid"
        if (!validText(item.formattedName, MAX_FORMATTED_NAME, allowEmpty = false)) return "formatted_name is invalid"
        if (!validStringList(item.emails, MAX_LIST_ITEMS, 4096)) return "emails are invalid"
        if (!validStringList(item.phones, MAX_LIST_ITEMS, 4096)) return "phones are invalid"
        if (item.organization != null && !validOptionalText(item.organization, 1024, preserveOuterWhitespace = true)) return "organization is invalid"
        if (item.title != null && !validOptionalText(item.title, 1024, preserveOuterWhitespace = true)) return "title is invalid"
        if (!validStringList(item.categories, MAX_LIST_ITEMS, 1024)) return "categories are invalid"
        return null
    }

    private fun validateStructuredName(value: StructuredNameWire): String? {
        val fields = listOf(
            value.familyName,
            value.givenName,
            value.additionalNames,
            value.honorificPrefixes,
            value.honorificSuffixes,
        )
        return if (fields.all { validText(it, 512, allowEmpty = true, preserveOuterWhitespace = true) }) null
        else "contains invalid text"
    }

    private fun validateAddress(value: PostalAddressWire): String? {
        if (!validStringList(value.types, 20, 128)) return "types are invalid"
        val bounded = listOf(
            value.poBox to 512,
            value.extendedAddress to 1024,
            value.streetAddress to 2048,
            value.locality to 512,
            value.region to 512,
            value.postalCode to 128,
            value.country to 512,
        )
        return if (bounded.all { (text, max) -> validText(text, max, allowEmpty = true, preserveOuterWhitespace = true) }) null
        else "contains invalid text"
    }

    private fun validateHref(value: String): String? {
        if (value.isBlank()) return "href is blank"
        if (value.length > MAX_HREF_LENGTH) return "href is too long"
        if (value != value.trim()) return "href is not canonical"
        if (value.any(Char::isISOControl)) return "href contains control characters"
        if (!value.startsWith('/')) return "href is not server-relative"
        if (value.startsWith("//")) return "href is a scheme-relative authority"
        return null
    }

    private fun validStringList(values: List<String>, maxItems: Int, maxLength: Int): Boolean =
        values.size <= maxItems && values.all {
            validText(it, maxLength, allowEmpty = false, preserveOuterWhitespace = true)
        }

    private fun validOptionalText(
        value: String,
        maxLength: Int,
        preserveOuterWhitespace: Boolean = false,
    ): Boolean = validText(value, maxLength, allowEmpty = false, preserveOuterWhitespace = preserveOuterWhitespace)

    private fun validText(
        value: String,
        maxLength: Int,
        allowEmpty: Boolean,
        preserveOuterWhitespace: Boolean = false,
    ): Boolean {
        if (value.length > maxLength) return false
        if (!allowEmpty && value.isEmpty()) return false
        if (!preserveOuterWhitespace && value != value.trim()) return false
        if (value.any { it.isISOControl() && it != '\n' && it != '\r' && it != '\t' }) return false
        return true
    }

    private fun reject(reason: String): CardDavResponseDecision.Rejected =
        CardDavResponseDecision.Rejected(reason)
}
