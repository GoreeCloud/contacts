package com.goreecloud.contacts

sealed interface CardDavDecodeResult<out T> {
    data class Decoded<T>(val value: T) : CardDavDecodeResult<T>
    data class Rejected(val path: String, val reason: String) : CardDavDecodeResult<Nothing>
}

/**
 * Converts already-parsed generic maps/lists/primitives into the exact Contacts wire models.
 *
 * This stage performs no JSON parsing, HTTP, authentication, persistence, provider access, or
 * synchronization. Structural success must still be followed by [CardDavResponseContract].
 */
object CardDavStructuralDecoder {
    fun decodeAddressBooks(value: Any?): CardDavDecodeResult<List<AddressBookWire>> = decodeResult {
        array(value, "$").mapIndexed { index, item -> decodeAddressBook(item, "$[$index]") }
    }

    fun decodeContactList(value: Any?): CardDavDecodeResult<List<ContactSummaryWire>> = decodeResult {
        array(value, "$").mapIndexed { index, item -> decodeSummary(item, "$[$index]") }
    }

    fun decodeContactDetail(value: Any?): CardDavDecodeResult<ContactDetailWire> = decodeResult {
        val obj = objectExact(value, "$", CardDavResponseContract.CONTACT_DETAIL_FIELDS)
        ContactDetailWire(
            summary = decodeSummaryObject(obj, "$"),
            structuredName = decodeStructuredName(required(obj, "structured_name", "$.structured_name"), "$.structured_name"),
            addresses = array(required(obj, "addresses", "$.addresses"), "$.addresses").mapIndexed { index, item ->
                decodeAddress(item, "$.addresses[$index]")
            },
            birthday = nullableString(obj, "birthday", "$.birthday"),
            websites = stringList(required(obj, "websites", "$.websites"), "$.websites"),
            note = nullableString(obj, "note", "$.note"),
            photo = nullableString(obj, "photo", "$.photo"),
        )
    }

    private fun decodeAddressBook(value: Any?, path: String): AddressBookWire {
        val obj = objectExact(value, path, CardDavResponseContract.ADDRESS_BOOK_FIELDS)
        return AddressBookWire(
            href = string(obj, "href", "$path.href"),
            displayName = string(obj, "display_name", "$path.display_name"),
        )
    }

    private fun decodeSummary(value: Any?, path: String): ContactSummaryWire =
        decodeSummaryObject(objectExact(value, path, CardDavResponseContract.CONTACT_SUMMARY_FIELDS), path)

    private fun decodeSummaryObject(obj: Map<String, Any?>, path: String): ContactSummaryWire =
        ContactSummaryWire(
            href = string(obj, "href", "$path.href"),
            etag = nullableString(obj, "etag", "$path.etag"),
            uid = nullableString(obj, "uid", "$path.uid"),
            formattedName = string(obj, "formatted_name", "$path.formatted_name"),
            emails = stringList(required(obj, "emails", "$path.emails"), "$path.emails"),
            phones = stringList(required(obj, "phones", "$path.phones"), "$path.phones"),
            organization = nullableString(obj, "organization", "$path.organization"),
            title = nullableString(obj, "title", "$path.title"),
            categories = stringList(required(obj, "categories", "$path.categories"), "$path.categories"),
            favorite = boolean(obj, "favorite", "$path.favorite"),
            hasPhoto = boolean(obj, "has_photo", "$path.has_photo"),
        )

    private fun decodeStructuredName(value: Any?, path: String): StructuredNameWire {
        val obj = objectExact(value, path, CardDavResponseContract.STRUCTURED_NAME_FIELDS)
        return StructuredNameWire(
            familyName = string(obj, "family_name", "$path.family_name"),
            givenName = string(obj, "given_name", "$path.given_name"),
            additionalNames = string(obj, "additional_names", "$path.additional_names"),
            honorificPrefixes = string(obj, "honorific_prefixes", "$path.honorific_prefixes"),
            honorificSuffixes = string(obj, "honorific_suffixes", "$path.honorific_suffixes"),
        )
    }

    private fun decodeAddress(value: Any?, path: String): PostalAddressWire {
        val obj = objectExact(value, path, CardDavResponseContract.POSTAL_ADDRESS_FIELDS)
        return PostalAddressWire(
            types = stringList(required(obj, "types", "$path.types"), "$path.types"),
            poBox = string(obj, "po_box", "$path.po_box"),
            extendedAddress = string(obj, "extended_address", "$path.extended_address"),
            streetAddress = string(obj, "street_address", "$path.street_address"),
            locality = string(obj, "locality", "$path.locality"),
            region = string(obj, "region", "$path.region"),
            postalCode = string(obj, "postal_code", "$path.postal_code"),
            country = string(obj, "country", "$path.country"),
        )
    }

    private inline fun <T> decodeResult(block: () -> T): CardDavDecodeResult<T> = try {
        CardDavDecodeResult.Decoded(block())
    } catch (failure: DecodeFailure) {
        CardDavDecodeResult.Rejected(failure.path, failure.message ?: "invalid value")
    }

    private fun objectExact(value: Any?, path: String, expectedFields: Set<String>): Map<String, Any?> {
        val raw = value as? Map<*, *> ?: fail(path, "expected object")
        val result = LinkedHashMap<String, Any?>(raw.size)
        for ((key, fieldValue) in raw) {
            val name = key as? String ?: fail(path, "object field names must be strings")
            result[name] = fieldValue
        }
        val unknown = result.keys - expectedFields
        if (unknown.isNotEmpty()) fail(path, "unknown fields: ${unknown.sorted().joinToString(",")}")
        val missing = expectedFields - result.keys
        if (missing.isNotEmpty()) fail(path, "missing fields: ${missing.sorted().joinToString(",")}")
        return result
    }

    private fun required(obj: Map<String, Any?>, field: String, path: String): Any? {
        if (!obj.containsKey(field)) fail(path, "field is missing")
        return obj[field]
    }

    private fun string(obj: Map<String, Any?>, field: String, path: String): String =
        required(obj, field, path) as? String ?: fail(path, "expected string")

    private fun nullableString(obj: Map<String, Any?>, field: String, path: String): String? {
        val value = required(obj, field, path)
        if (value == null) return null
        return value as? String ?: fail(path, "expected string or null")
    }

    private fun boolean(obj: Map<String, Any?>, field: String, path: String): Boolean =
        required(obj, field, path) as? Boolean ?: fail(path, "expected boolean")

    private fun array(value: Any?, path: String): List<Any?> =
        (value as? List<*>)?.toList() ?: fail(path, "expected array")

    private fun stringList(value: Any?, path: String): List<String> =
        array(value, path).mapIndexed { index, item ->
            item as? String ?: fail("$path[$index]", "expected string")
        }

    private fun fail(path: String, reason: String): Nothing = throw DecodeFailure(path, reason)

    private class DecodeFailure(val path: String, reason: String) : IllegalArgumentException(reason)
}
