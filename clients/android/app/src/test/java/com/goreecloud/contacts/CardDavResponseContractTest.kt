package com.goreecloud.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CardDavResponseContractTest {
    @Test
    fun acceptsBoundedAddressBooksAndContactList() {
        assertEquals(
            CardDavResponseDecision.Accepted(1),
            CardDavResponseContract.acceptAddressBooks(
                listOf(AddressBookWire("/alice/contacts/", "Contacts")),
            ),
        )
        assertEquals(
            CardDavResponseDecision.Accepted(1),
            CardDavResponseContract.acceptContactList(
                "/alice/contacts/",
                listOf(summary()),
            ),
        )
    }

    @Test
    fun acceptsDetailThatMatchesRequestedOpaqueHref() {
        val detail = ContactDetailWire(
            summary = summary(),
            structuredName = StructuredNameWire(givenName = "Alice", familyName = "Example"),
            addresses = listOf(
                PostalAddressWire(
                    types = listOf("HOME"),
                    streetAddress = "1 Example Street",
                    locality = "Birmingham",
                    region = "AL",
                    postalCode = "35203",
                    country = "US",
                ),
            ),
            birthday = "2000-01-02",
            websites = listOf("https://example.test/alice"),
            note = "Development fixture\nLine two",
            photo = "https://example.test/alice.jpg",
        )

        assertEquals(
            CardDavResponseDecision.Accepted(1),
            CardDavResponseContract.acceptContactDetail("/alice/contacts/alice.vcf", detail),
        )
    }

    @Test
    fun rejectsOriginChangingOrNonCanonicalHrefs() {
        val invalid = listOf(
            "https://example.test/alice.vcf",
            "//example.test/alice.vcf",
            " /alice/contacts/alice.vcf",
            "/alice/contacts/alice.vcf\u0000",
        )
        invalid.forEach { href ->
            assertRejected(CardDavResponseContract.acceptAddressBooks(listOf(AddressBookWire(href, "Contacts"))))
            assertRejected(CardDavResponseContract.acceptContactList("/alice/contacts/", listOf(summary(href = href))))
        }
    }

    @Test
    fun rejectsDuplicateOpaqueResourceIdentities() {
        assertRejected(
            CardDavResponseContract.acceptAddressBooks(
                listOf(
                    AddressBookWire("/alice/a/", "A"),
                    AddressBookWire("/alice/a/", "Duplicate"),
                ),
            ),
        )
        assertRejected(
            CardDavResponseContract.acceptContactList(
                "/alice/contacts/",
                listOf(summary(), summary()),
            ),
        )
    }

    @Test
    fun rejectsDetailHrefMismatchAndOversizedCollections() {
        val detail = ContactDetailWire(
            summary = summary(),
            structuredName = StructuredNameWire(),
            addresses = emptyList(),
            birthday = null,
            websites = emptyList(),
            note = null,
            photo = null,
        )
        assertRejected(
            CardDavResponseContract.acceptContactDetail("/alice/contacts/other.vcf", detail),
        )
        assertRejected(
            CardDavResponseContract.acceptContactList(
                "/alice/contacts/",
                List(257) { index -> summary(href = "/alice/contacts/$index.vcf") },
            ),
        )
    }

    @Test
    fun rejectsControlBearingAndMalformedPresentationData() {
        assertRejected(
            CardDavResponseContract.acceptContactList(
                "/alice/contacts/",
                listOf(summary(formattedName = "Alice\u0000Example")),
            ),
        )
        assertRejected(
            CardDavResponseContract.acceptContactList(
                "/alice/contacts/",
                listOf(summary(emails = listOf(" alice@example.test "))),
            ),
        )
    }

    @Test
    fun exactFieldAllowlistsRejectUnknownAuthorityOrSecretFields() {
        assertTrue(
            CardDavResponseContract.unexpectedFields(
                setOf("href", "display_name", "origin"),
                CardDavResponseContract.ADDRESS_BOOK_FIELDS,
            ).contains("origin"),
        )
        assertTrue(
            CardDavResponseContract.unexpectedFields(
                setOf("href", "formatted_name", "password"),
                CardDavResponseContract.CONTACT_SUMMARY_FIELDS,
            ).contains("password"),
        )
        assertTrue(
            CardDavResponseContract.unexpectedFields(
                setOf("href", "formatted_name", "radicale_credential"),
                CardDavResponseContract.CONTACT_DETAIL_FIELDS,
            ).contains("radicale_credential"),
        )
    }

    private fun summary(
        href: String = "/alice/contacts/alice.vcf",
        formattedName: String = "Alice Example",
        emails: List<String> = listOf("alice@example.test"),
    ) = ContactSummaryWire(
        href = href,
        etag = "\"etag-1\"",
        uid = "alice-example",
        formattedName = formattedName,
        emails = emails,
        phones = listOf("+12055550100"),
        organization = "GoreeCloud",
        title = "Development Contact",
        categories = listOf("Example"),
        favorite = false,
        hasPhoto = true,
    )

    private fun assertRejected(decision: CardDavResponseDecision) {
        assertTrue(decision is CardDavResponseDecision.Rejected)
    }
}
