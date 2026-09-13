package com.goreecloud.contacts

import java.time.Instant

object ContactsIdentityContractReference {
    const val SCHEMA = "goreecloud.identity.native-application-session/v1"
    const val CANDIDATE_REVISION = "62ad109809f2e479cf71a6327ffd0d4537a6b3df"
}

/**
 * Non-secret proof metadata that a future GoreeCloud Identity exchange must establish for the
 * native Contacts client. This model intentionally contains no token, cookie, password, CardDAV
 * credential, refresh secret, or transport implementation.
 */
data class ContactsIdentityProof(
    val principalId: String,
    val audience: String,
    val issuedAt: Instant,
    val expiresAt: Instant,
)

data class ContactsIdentityExpectation(
    val principalId: String,
    val audience: String = ANDROID_CONTACTS_AUDIENCE,
) {
    companion object {
        const val ANDROID_CONTACTS_AUDIENCE = "goreecloud-contacts-android"
    }
}

sealed interface ContactsIdentityBindingDecision {
    /** Metadata binding is valid; native session exchange and network transport remain separate. */
    data class Bound(
        val principalId: String,
        val expiresAt: Instant,
    ) : ContactsIdentityBindingDecision

    data object MissingProof : ContactsIdentityBindingDecision
    data object InvalidExpectation : ContactsIdentityBindingDecision
    data object InvalidProof : ContactsIdentityBindingDecision
    data object PrincipalMismatch : ContactsIdentityBindingDecision
    data object AudienceMismatch : ContactsIdentityBindingDecision
    data object NotYetValid : ContactsIdentityBindingDecision
    data object Expired : ContactsIdentityBindingDecision
}

/**
 * Pure, fail-closed consumer acceptance policy aligned to the pinned GoreeCloud Identity
 * native-application-session source contract candidate. A Bound result is not authentication and
 * does not authorize CardDAV access or expand Contacts authority.
 */
object ContactsIdentityBindingPolicy {
    fun evaluate(
        proof: ContactsIdentityProof?,
        expectation: ContactsIdentityExpectation,
        now: Instant,
    ): ContactsIdentityBindingDecision {
        if (!isExactIdentity(expectation.principalId) || !isExactIdentity(expectation.audience)) {
            return ContactsIdentityBindingDecision.InvalidExpectation
        }

        proof ?: return ContactsIdentityBindingDecision.MissingProof

        if (!isExactIdentity(proof.principalId) ||
            !isExactIdentity(proof.audience) ||
            !proof.issuedAt.isBefore(proof.expiresAt)
        ) {
            return ContactsIdentityBindingDecision.InvalidProof
        }

        if (proof.principalId != expectation.principalId) {
            return ContactsIdentityBindingDecision.PrincipalMismatch
        }
        if (proof.audience != expectation.audience) {
            return ContactsIdentityBindingDecision.AudienceMismatch
        }
        if (now.isBefore(proof.issuedAt)) {
            return ContactsIdentityBindingDecision.NotYetValid
        }
        if (!now.isBefore(proof.expiresAt)) {
            return ContactsIdentityBindingDecision.Expired
        }

        return ContactsIdentityBindingDecision.Bound(
            principalId = proof.principalId,
            expiresAt = proof.expiresAt,
        )
    }

    private fun isExactIdentity(value: String): Boolean =
        value.isNotBlank() && value == value.trim() && value.none(Char::isISOControl)
}
