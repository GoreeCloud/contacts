package com.goreecloud.contacts

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Locale

/**
 * Real emulator acceptance for permission-denied navigation and lifecycle.
 *
 * Intentionally NEVER grants or revokes the OS permission, launches the
 * permission prompt, queries ContactsProvider or reads a real contact. A
 * permission-revocation test needs an independent disposable-device process
 * lifecycle gate because Android may terminate the package on revocation.
 */
@RunWith(AndroidJUnit4::class)
class ContactsDeniedPermissionUiTest {
    private fun strings(view: View, result: MutableList<String>) {
        if (view is TextView) result.add(view.text.toString())
        if (view is ViewGroup) for (i in 0 until view.childCount) strings(view.getChildAt(i), result)
    }

    private fun findTab(view: View, label: String): View? {
        val desc = view.contentDescription?.toString()?.substringBefore(",")?.trim()
        if (desc == label && view.isClickable) return view
        if (view is ViewGroup) {
            for (i in 0 until view.childCount) {
                val candidate = findTab(view.getChildAt(i), label)
                if (candidate != null) return candidate
            }
        }
        return null
    }

    private fun assertPermissionGate(activity: ContactsActivity) {
        assertTrue(activity.checkSelfPermission(Manifest.permission.READ_CONTACTS) !=
            PackageManager.PERMISSION_GRANTED)
        val root = activity.findViewById<ViewGroup>(android.R.id.content)
        val visible = mutableListOf<String>()
        strings(root, visible)
        assertTrue("Permission-denied privacy explanation missing",
            visible.any { it == "Your contacts stay yours" })
        assertTrue("Read-only permission disclosure missing",
            visible.any { it.contains("Allow read-only access to show contacts") })
        assertTrue("No-upload disclosure missing",
            visible.any { it.contains("No names or numbers are uploaded") })
        assertTrue("Explicit permission action missing",
            visible.any { it == "Allow contact access" })
        assertFalse("Directory loading must not be triggered without consent",
            visible.any { it == "Opening your directory" })
        assertFalse("Provider-derived directory should not be displayed without permission",
            visible.any { it == "PEOPLE, ORGANIZED" || it == "Directory unavailable" })
    }

    @Test fun deniedPermissionRemainsGatedAcrossTabsAndActivityRecreation() {
        val hardware = Build.HARDWARE.lowercase(Locale.ROOT)
        assumeTrue("Disposable hosted emulator only",
            hardware.contains("ranchu") || hardware.contains("goldfish"))
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        assumeTrue("Never run on a package with real Contacts access",
            context.checkSelfPermission(Manifest.permission.READ_CONTACTS) !=
                PackageManager.PERMISSION_GRANTED)

        ActivityScenario.launch(ContactsActivity::class.java).use { scenario ->
            scenario.onActivity { activity ->
                assertPermissionGate(activity)
                for (label in listOf("Favorites", "Groups", "Tools", "People")) {
                    val item = findTab(
                        activity.findViewById(android.R.id.content), label)
                    assertNotNull("Missing native navigation tab: $label", item)
                    assertTrue("Native tab not keyboard/accessibility clickable: $label",
                        item!!.isFocusable && item.isClickable)
                    item.performClick()
                    assertPermissionGate(activity)
                }
            }
            scenario.recreate()
            scenario.onActivity { activity ->
                assertPermissionGate(activity)
            }
        }
    }
}
