package com.goreecloud.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class GlazeContactsContractTest {
    @Test
    fun currentStableGlazeReferenceIsPinned() {
        assertEquals("1.4.1", GlazeContactsContract.VERSION)
        assertEquals(
            "4fab9da0fad2e5c974e0e66ec88632c61745751c",
            GlazeContactsContract.REFERENCE_REVISION,
        )
        assertEquals("1.4.0", GlazeContactsContract.ROLLBACK_VERSION)
        assertEquals("ADOPTION_IN_PROGRESS", GlazeContactsContract.ADOPTION_STATE)
    }

    @Test
    fun sharedStableQualificationDoesNotCreateContactsAcceptance() {
        assertFalse(GlazeContactsContract.OPTICAL_ENGINE_ACCEPTED)
        assertFalse(GlazeContactsContract.REDUCED_TRANSPARENCY_ACCEPTED)
        assertFalse(GlazeContactsContract.INCREASED_CONTRAST_ACCEPTED)
        assertFalse(GlazeContactsContract.PHYSICAL_DEVICE_ACCEPTED)
        assertFalse(GlazeContactsContract.HUMAN_VISUAL_ACCEPTED)
    }
}
