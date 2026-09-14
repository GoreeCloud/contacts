package com.goreecloud.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CardDavStructuralDecoderTest {
    @Test
    fun exactAddressBookAndContactShapesDecodeAndAccept() {
        val books = CardDavStructuralDecoder.decodeAddressBooks(
            listOf(linkedMapOf("href" to "/users/alice/contacts/", "display_name" to "Contacts")),
        )
        assertTrue(books is CardDavDecodeResult.Decoded)
        assertEquals(
            CardDavResponseDecision.Accepted(1),
            CardDavResponseContract.acceptAddressBooks((books as CardDavDecodeResult.Decoded).value),
        )

        val contacts = CardDavStructuralDecoder.decodeContactList(listOf(summary()))
        assertTrue(contacts is CardDavDecodeResult.Decoded)
        assertEquals(
            CardDavResponseDecision.Accepted(1),
            CardDavResponseContract.acceptContactList(
                "/users/alice/contacts/",
                (contacts as CardDavDecodeResult.Decoded).value,
            ),
        )
    }

    @Test
    fun exactDetailShapeDecodesAndAccepts() {
        val decoded = CardDavStructuralDecoder.decodeContactDetail(detail())
        assertTrue(decoded is CardDavDecodeResult.Decoded)
        assertEquals(
            CardDavResponseDecision.Accepted(1),
            CardDavResponseContract.acceptContactDetail(
                "/users/alice/contacts/1.vcf",
                (decoded as CardDavDecodeResult.Decoded).value,
            ),
        )
    }

    @Test
    fun unknownAndMissingFieldsFailClosed() {
        val unknown = summary().toMutableMap().apply { put("password", "secret") }
        assertRejectedAt(CardDavStructuralDecoder.decodeContactList(listOf(unknown)), "$[0]")

        val missing = summary().toMutableMap().apply { remove("favorite") }
        assertRejectedAt(CardDavStructuralDecoder.decodeContactList(listOf(missing)), "$[0]")
    }

    @Test
    fun truthyStringsAndWrongNullabilityAreNotCoerced() {
        val truthy = summary().toMutableMap().apply { put("favorite", "true") }
        assertRejectedAt(CardDavStructuralDecoder.decodeContactList(listOf(truthy)), "$[0].favorite")

        val nullList = summary().toMutableMap().apply { put("emails", null) }
        assertRejectedAt(CardDavStructuralDecoder.decodeContactList(listOf(nullList)), "$[0].emails")

        val stringNull = summary().toMutableMap().apply { put("etag", 7) }
        assertRejectedAt(CardDavStructuralDecoder.decodeContactList(listOf(stringNull)), "$[0].etag")
    }

    @Test
    fun nestedDetailObjectsUseExactFieldSets() {
        val payload = detail().toMutableMap()
        val structured = map(payload.getValue("structured_name")).toMutableMap()
        structured["nickname"] = "hidden"
        payload["structured_name"] = structured
        assertRejectedAt(CardDavStructuralDecoder.decodeContactDetail(payload), "$.structured_name")

        val badAddress = detail().toMutableMap()
        val addresses = (badAddress.getValue("addresses") as List<*>).toMutableList()
        val address = map(addresses.single()).toMutableMap()
        address.remove("country")
        addresses[0] = address
        badAddress["addresses"] = addresses
        assertRejectedAt(CardDavStructuralDecoder.decodeContactDetail(badAddress), "$.addresses[0]")
    }

    private fun assertRejectedAt(result: CardDavDecodeResult<*>, path: String) {
        assertTrue(result is CardDavDecodeResult.Rejected)
        assertEquals(path, (result as CardDavDecodeResult.Rejected).path)
    }

    private fun summary(): Map<String, Any?> = linkedMapOf(
        "href" to "/users/alice/contacts/1.vcf",
        "etag" to "etag-1",
        "uid" to "uid-1",
        "formatted_name" to "Alice Example",
        "emails" to listOf("alice@example.test"),
        "phones" to listOf("+15555550100"),
        "organization" to "GoreeCloud",
        "title" to "Engineer",
        "categories" to listOf("work"),
        "favorite" to true,
        "has_photo" to false,
    )

    private fun detail(): Map<String, Any?> = LinkedHashMap(summary()).apply {
        put(
            "structured_name",
            linkedMapOf(
                "family_name" to "Example",
                "given_name" to "Alice",
                "additional_names" to "",
                "honorific_prefixes" to "",
                "honorific_suffixes" to "",
            ),
        )
        put(
            "addresses",
            listOf(
                linkedMapOf(
                    "types" to listOf("work"),
                    "po_box" to "",
                    "extended_address" to "",
                    "street_address" to "1 Main St",
                    "locality" to "Birmingham",
                    "region" to "AL",
                    "postal_code" to "35203",
                    "country" to "US",
                ),
            ),
        )
        put("birthday", "1990-01-01")
        put("websites", listOf("https://example.test"))
        put("note", "Notes")
        put("photo", null)
    }

    private fun map(value: Any?): Map<String, Any?> =
        (value as Map<*, *>).entries.associate { it.key as String to it.value }
}
