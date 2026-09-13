package com.goreecloud.contacts

import java.time.Instant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactsIdentityBindingTest {
    private val now = Instant.parse("2026-09-13T18:00:00Z")
    private val expectation = ContactsIdentityExpectation(principalId = "user-42")

    private fun proof(
        principalId: String = expectation.principalId,
        audience: String = ContactsIdentityExpectation.ANDROID_CONTACTS_AUDIENCE,
        issuedAt: Instant = now.minusSeconds(60),
        expiresAt: Instant = now.plusSeconds(600),
    ) = ContactsIdentityProof(
        principalId = principalId,
        audience = audience,
        issuedAt = issuedAt,
        expiresAt = expiresAt,
    )

    @Test
    fun canonicalIdentityContractCandidateIsPinnedExactly() {
        assertEquals(
            "goreecloud.identity.native-application-session/v1",
            ContactsIdentityContractReference.SCHEMA,
        )
        assertEquals(
            "62ad109809f2e479cf71a6327ffd0d4537a6b3df",
            ContactsIdentityContractReference.CANDIDATE_REVISION,
        )
    }

    @Test
    fun missingProofFailsClosed() {
        assertEquals(
            ContactsIdentityBindingDecision.MissingProof,
            ContactsIdentityBindingPolicy.evaluate(null, expectation, now),
        )
    }

    @Test
    fun exactPrincipalAndAudienceCanBind() {
        val decision = ContactsIdentityBindingPolicy.evaluate(proof(), expectation, now)
        assertTrue(decision is ContactsIdentityBindingDecision.Bound)
        decision as ContactsIdentityBindingDecision.Bound
        assertEquals("user-42", decision.principalId)
    }

    @Test
    fun identityValuesAreRejectedRatherThanNormalized() {
        assertEquals(
            ContactsIdentityBindingDecision.InvalidProof,
            ContactsIdentityBindingPolicy.evaluate(proof(principalId = " user-42"), expectation, now),
        )
        assertEquals(
            ContactsIdentityBindingDecision.InvalidProof,
            ContactsIdentityBindingPolicy.evaluate(proof(audience = "goreecloud-contacts-android\n"), expectation, now),
        )
    }

    @Test
    fun principalAndAudienceMismatchFailIndependently() {
        assertEquals(
            ContactsIdentityBindingDecision.PrincipalMismatch,
            ContactsIdentityBindingPolicy.evaluate(proof(principalId = "user-41"), expectation, now),
        )
        assertEquals(
            ContactsIdentityBindingDecision.AudienceMismatch,
            ContactsIdentityBindingPolicy.evaluate(proof(audience = "goreecloud-calendar-android"), expectation, now),
        )
    }

    @Test
    fun invalidFutureAndExpiredLifetimeFailClosed() {
        assertEquals(
            ContactsIdentityBindingDecision.InvalidProof,
            ContactsIdentityBindingPolicy.evaluate(
                proof(issuedAt = now, expiresAt = now),
                expectation,
                now,
            ),
        )
        assertEquals(
            ContactsIdentityBindingDecision.NotYetValid,
            ContactsIdentityBindingPolicy.evaluate(
                proof(issuedAt = now.plusSeconds(1), expiresAt = now.plusSeconds(600)),
                expectation,
                now,
            ),
        )
        assertEquals(
            ContactsIdentityBindingDecision.Expired,
            ContactsIdentityBindingPolicy.evaluate(proof(expiresAt = now), expectation, now),
        )
    }

    @Test
    fun malformedExpectationCannotGrantAuthority() {
        assertEquals(
            ContactsIdentityBindingDecision.InvalidExpectation,
            ContactsIdentityBindingPolicy.evaluate(
                proof(),
                expectation.copy(principalId = "user-42 "),
                now,
            ),
        )
    }
}
