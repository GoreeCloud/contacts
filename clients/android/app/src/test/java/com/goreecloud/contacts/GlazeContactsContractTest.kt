package com.goreecloud.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class GlazeContactsContractTest {
    @Test
    fun currentStableGlazeReferenceIsPinned() {
        assertEquals("1.4.0", GlazeContactsContract.VERSION)
        assertEquals(
            "84cb3db4884042f0fa25ed6d475a127fb110f596",
            GlazeContactsContract.REFERENCE_REVISION,
        )
        assertEquals("ADOPTION_IN_PROGRESS", GlazeContactsContract.ADOPTION_STATE)
    }

    @Test
    fun opticalAndHumanAcceptanceRemainFailClosed() {
        assertFalse(GlazeContactsContract.OPTICAL_ENGINE_ACCEPTED)
        assertFalse(GlazeContactsContract.REDUCED_TRANSPARENCY_ACCEPTED)
        assertFalse(GlazeContactsContract.INCREASED_CONTRAST_ACCEPTED)
        assertFalse(GlazeContactsContract.PHYSICAL_DEVICE_ACCEPTED)
        assertFalse(GlazeContactsContract.HUMAN_VISUAL_ACCEPTED)
    }
}
