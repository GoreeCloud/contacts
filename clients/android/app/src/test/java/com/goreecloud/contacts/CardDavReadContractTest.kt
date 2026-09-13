package com.goreecloud.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class CardDavReadContractTest {
    @Test
    fun addressBookDiscoveryUsesExistingRelativeEndpoint() {
        assertEquals("/api/carddav/address-books", CardDavReadContract.ADDRESS_BOOKS_PATH)
    }

    @Test
    fun contactListingEncodesOnlyTheServerRelativeHref() {
        assertEquals(
            "/api/carddav/contacts?address_book_href=%2Fusers%2Falice%2Fcontacts%2F",
            CardDavReadContract.contactsPath("/users/alice/contacts/"),
        )
    }

    @Test
    fun contactDetailEncodesOpaqueHrefWithoutChangingItsIdentity() {
        assertEquals(
            "/api/carddav/contact?href=%2Fusers%2Falice%2Fcontacts%2Fcontact%201.vcf",
            CardDavReadContract.contactDetailPath("/users/alice/contacts/contact 1.vcf"),
        )
    }

    @Test
    fun absoluteAndSchemeRelativeAuthoritiesAreRejected() {
        listOf(
            "https://dav.example.test/users/alice/contacts/",
            "//dav.example.test/users/alice/contacts/",
        ).forEach { value ->
            assertThrows(IllegalArgumentException::class.java) {
                CardDavReadContract.contactsPath(value)
            }
        }
    }

    @Test
    fun blankTrimDependentControlAndOversizedHrefsAreRejected() {
        listOf(
            "",
            "   ",
            " /users/alice/contacts/",
            "/users/alice/contacts/\n",
            "/" + "a".repeat(4096),
        ).forEach { value ->
            assertThrows(IllegalArgumentException::class.java) {
                CardDavReadContract.contactDetailPath(value)
            }
        }
    }

    @Test
    fun readContractDoesNotClaimNativeIdentityOrTransportAcceptance() {
        val readiness = CardDavReadContract.readiness()
        assertEquals(CardDavReadContractState.SOURCE_READY, readiness.addressBookDiscovery)
        assertEquals(CardDavReadContractState.SOURCE_READY, readiness.contactListing)
        assertEquals(CardDavReadContractState.SOURCE_READY, readiness.contactDetail)
        assertEquals(CardDavReadContractState.IDENTITY_BLOCKED, readiness.nativeIdentitySession)
        assertEquals(CardDavReadContractState.TRANSPORT_BLOCKED, readiness.networkTransport)
    }
}
