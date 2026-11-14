// GoreeCloud Contacts: optional Qt Quick 6.12.0 migration preview.
// GC UI alpha Iris/light semantic values from gc-ui/tokens/gc.tokens.json,
// blob 5ea0b8f0b1d4c9f7c3593d58daeb1b75e6ec980e. Not UI acceptance.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 960
    height: 680
    minimumWidth: 520
    minimumHeight: 380
    title: qsTr("GoreeCloud Contacts — Qt Quick preview")
    color: "#F6F7FB"

    readonly property color gcBrand: "#5146C8"
    readonly property color gcText: "#1B2030"
    readonly property color gcMuted: "#505B70"
    readonly property color gcSurface: "#FFFFFF"
    readonly property color gcOutline: "#CED3DF"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    text: qsTr("GoreeCloud Contacts")
                    font.pixelSize: 27
                    font.bold: true
                    color: root.gcText
                }
                Label {
                    text: contactsBackend.sourceLabel
                    color: root.gcMuted
                    font.pixelSize: 13
                }
            }
            Rectangle {
                radius: 12
                color: "#E8E5FF"
                implicitWidth: previewCaption.implicitWidth + 24
                implicitHeight: 36
                Label {
                    id: previewCaption
                    anchors.centerIn: parent
                    text: qsTr("Read-only preview")
                    color: "#30266F"
                    font.bold: true
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            TextField {
                id: query
                Layout.fillWidth: true
                placeholderText: qsTr("Search contacts, phone, email, or organization")
                Accessible.name: qsTr("Search local contacts")
                onTextChanged: searchDelay.restart()
            }
            CheckBox {
                id: favorites
                text: qsTr("Favorites only")
                Accessible.name: qsTr("Show favorite contacts only")
                onToggled: contactsBackend.applyFilter(query.text, checked)
            }
        }

        Timer {
            id: searchDelay
            interval: 180
            repeat: false
            onTriggered: contactsBackend.applyFilter(query.text, favorites.checked)
        }

        Label {
            Layout.fillWidth: true
            text: qsTr("%1 contacts displayed").arg(contactsBackend.rows.length)
            color: root.gcMuted
            font.pixelSize: 13
        }

        Label {
            Layout.fillWidth: true
            visible: contactsBackend.rows.length === 0
            text: qsTr("No matching contacts.")
            color: root.gcMuted
            Accessible.role: Accessible.StaticText
        }

        ListView {
            id: contactList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 12
            boundsBehavior: Flickable.StopAtBounds
            model: contactsBackend.rows
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Rectangle {
                id: card
                required property var modelData
                property var person: modelData
                width: contactList.width - 4
                height: Math.max(115, itemBody.implicitHeight + 28)
                radius: 18
                color: root.gcSurface
                border.color: root.gcOutline
                border.width: 1
                Accessible.role: Accessible.ListItem
                Accessible.name: String(person.name || "") + ", " +
                                 String(person.organization || "") + ", " +
                                 String(person.phone || "") + ", " +
                                 String(person.email || "")
                RowLayout {
                    id: itemBody
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 14
                    Rectangle {
                        Layout.alignment: Qt.AlignTop
                        width: 50
                        height: 50
                        radius: 14
                        color: "#E8E5FF"
                        Label {
                            anchors.centerIn: parent
                            text: String(card.person.name || "?").slice(0, 1).toUpperCase()
                            font.pixelSize: 21
                            font.bold: true
                            color: "#30266F"
                        }
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                Layout.fillWidth: true
                                text: String(card.person.name || "")
                                font.pixelSize: 17
                                font.bold: true
                                color: root.gcText
                                elide: Text.ElideRight
                            }
                            Label {
                                text: card.person.favorite ? qsTr("★ Favorite") : ""
                                visible: card.person.favorite
                                color: root.gcBrand
                                font.bold: true
                            }
                        }
                        Label {
                            text: String(card.person.organization || "")
                            visible: text.length > 0
                            color: root.gcMuted
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Label {
                            text: [String(card.person.phone || ""), String(card.person.email || "")]
                                  .filter(function(value) { return value.length > 0 }).join("  ·  ")
                            color: root.gcMuted
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }

        Label {
            Layout.fillWidth: true
            text: qsTr("Offline • No network calls • Editing and import/export stay in the existing GTK preview until migrated")
            font.pixelSize: 12
            wrapMode: Text.WordWrap
            color: root.gcMuted
        }
    }
}
