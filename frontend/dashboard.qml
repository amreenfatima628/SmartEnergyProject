import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    visible: true
    width: 1000
    height: 850
    color: "#0a0a0a"
    title: "Smart Energy Dashboard Pro"
    
    property var dataPoints: []

    Popup {
        id: alertPopup
        x: (parent.width - width) / 2
        y: 20
        width: 400
        height: 50
        padding: 0
        background: Rectangle { color: "#d32f2f"; radius: 10; border.color: "#ff8a80"; border.width: 1 }
        Text { id: alertTxt; anchors.centerIn: parent; color: "white"; font.bold: true; font.pixelSize: 14 }
    }

    Connections {
        target: backend
        function onNotificationRequested(msg) { 
            alertTxt.text = msg
            alertPopup.open()
            closeTimer.restart()
        }
    }

    Timer { id: closeTimer; interval: 4000; onTriggered: alertPopup.close() }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 25
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "⚙️ SETTINGS"
                onClicked: settingsPopup.open()
                background: Rectangle { color: "#1a1a1a"; radius: 5; border.color: "#333" }
                contentItem: Text { text: parent.text; color: "#00f2ff"; padding: 8; font.bold: true }
            }
            Item { Layout.fillWidth: true }
            Text { text: "SMART ENERGY PRO"; color: "#222"; font.bold: true; font.letterSpacing: 2 }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 150 
            Item { Layout.preferredWidth: 200 } 
            Item { Layout.fillWidth: true }
            Rectangle {
                width: 140; height: 140; radius: 70; color: "#111"
                border.color: (backend && backend.isOverload) ? "#ff4444" : ((backend && backend.isPeakMode) ? "#e67e22" : "#00f2ff")
                border.width: 4
                Column {
                    anchors.centerIn: parent
                    Text { text: "TOTAL LOAD"; color: "#666"; font.pixelSize: 10; anchors.horizontalCenter: parent.horizontalCenter }
                    Text { 
                        text: (backend ? backend.currentWatts.toFixed(0) : "0") + " W"
                        color: (backend && backend.isOverload) ? "#ff4444" : "white"
                        font.pixelSize: 24; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter 
                    }
                }
            }
            Item { Layout.fillWidth: true }
            Rectangle {
                width: 200; height: 80; radius: 12; color: "#161616"
                border.color: (backend && backend.isPeakMode) ? "#e67e22" : "#333"; border.width: 2
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 8; spacing: 0
                    Text {
                        text: (backend && backend.isPeakMode) ? "⚡ PEAK ACTIVE" : "⏲️ NEXT PEAK"
                        color: (backend && backend.isPeakMode) ? "#e67e22" : "#888"
                        font.pixelSize: 10; font.bold: true; Layout.alignment: Qt.AlignHCenter
                    }
                    Text { text: (backend && backend.isPeakMode) ? "ENDS IN" : "STARTS IN"; color: "white"; font.pixelSize: 11; Layout.alignment: Qt.AlignHCenter }
                    Text {
                        text: backend ? backend.peakCountdown : "00:00:00"
                        color: (backend && backend.isPeakMode) ? "#e67e22" : "#00f2ff"
                        font.pixelSize: 20; font.bold: true; font.family: "Monospace"; Layout.alignment: Qt.AlignHCenter
                    }
                }
            }
        }

        Text { text: "DEVICE COMMAND CENTER"; color: "#888"; font.bold: true; font.pixelSize: 12 }
        
        GridView {
            id: deviceGrid
            Layout.fillWidth: true; Layout.preferredHeight: 250
            cellWidth: width / 4; cellHeight: 125
            model: backend ? backend.deviceNames : []
            interactive: false 
            delegate: Item {
                width: deviceGrid.cellWidth; height: 125
                property var devInfo: (backend && backend.deviceData && backend.deviceData[modelData]) ? backend.deviceData[modelData] : { "watts": 0.0, "status": "OFF", "essential": false }
                Rectangle {
                    anchors.fill: parent; anchors.margins: 5; color: "#161616"; radius: 10
                    border.color: devInfo.status === "ON" ? "#00f2ff" : "#333"; border.width: 1
                    ColumnLayout {
                        anchors.fill: parent; anchors.margins: 10; spacing: 5
                        Text { text: (devInfo.essential ? "⭐ " : "") + modelData; color: "white"; font.bold: true; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                        Text { text: devInfo.watts.toFixed(1) + " W"; color: devInfo.status === "ON" ? "#00f2ff" : "#444"; font.pixelSize: 16; font.bold: true }
                        Button {
                            id: controlBtn
                            Layout.fillWidth: true; Layout.preferredHeight: 28
                            text: devInfo.status === "ON" ? "TURN OFF" : "TURN ON"
                            onClicked: backend.toggleDevice(modelData)
                            contentItem: Text { text: controlBtn.text; color: "white"; font.bold: true; font.pixelSize: 9; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            background: Rectangle { color: devInfo.status === "ON" ? "#d32f2f" : "#2e7d32"; radius: 5 }
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 20
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; color: "#111"; radius: 15; border.color: "#222"
                Column {
                    anchors.centerIn: parent; spacing: 15
                    Text { text: "LIFETIME BILLING"; color: "#555"; font.bold: true; font.pixelSize: 14; anchors.horizontalCenter: parent.horizontalCenter }
                    Text { text: "Rs. " + (backend ? backend.currentCost.toFixed(2) : "0.00"); color: "#00ff88"; font.pixelSize: 42; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }
                    Text { text: "Rate: " + (backend ? backend.unitRate : "0") + " PKR/unit"; color: "#333"; font.pixelSize: 12; anchors.horizontalCenter: parent.horizontalCenter }
                }
            }
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; color: "#111"; radius: 15; clip: true; border.color: "#222"
                Text { anchors.top: parent.top; anchors.left: parent.left; anchors.margins: 15; text: "LIVE CONSUMPTION GRAPH"; color: "#555"; font.bold: true; font.pixelSize: 12 }
                Canvas {
                    id: usageCanvas; anchors.fill: parent; anchors.margins: 25; anchors.topMargin: 50
                    onPaint: {
                        var ctx = getContext("2d"); ctx.clearRect(0, 0, width, height);
                        ctx.strokeStyle = "#1a1a1a"; ctx.lineWidth = 1;
                        for(var i=0; i<5; i++){ var y = (height/4) * i; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(width,y); ctx.stroke(); }
                        if(root.dataPoints.length > 1){
                            ctx.strokeStyle = (backend && backend.isPeakMode) ? "#e67e22" : "#00f2ff"; ctx.lineWidth = 3; ctx.beginPath();
                            for(var j=0; j<root.dataPoints.length; j++){
                                var x = (width / 49) * j; var pointY = height - (Math.min(root.dataPoints[j], 4000) / 4000) * height;
                                if(j === 0) ctx.moveTo(x, pointY); else ctx.lineTo(x, pointY);
                            } ctx.stroke();
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: backend
        function onDataUpdated() {
            if(backend) {
                root.dataPoints.push(backend.currentWatts);
                if(root.dataPoints.length > 50) root.dataPoints.shift();
                usageCanvas.requestPaint();
            }
        }
    }

    Popup {
        id: settingsPopup
        x: 25; y: 70
        width: 320; height: 580 
        modal: true; focus: true
        background: Rectangle { color: "#0f0f0f"; radius: 15; border.color: "#333"; border.width: 2 }
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 12
            Text { text: "SYSTEM SETTINGS"; color: "white"; font.bold: true; font.pixelSize: 18 }
            
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "Unit Rate (PKR)"; color: "#888"; font.pixelSize: 12 }
                TextField { 
                    id: rateField
                    text: activeFocus ? text : (backend ? backend.unitRate.toString() : "0")
                    onAccepted: { if(backend) backend.setUnitRate(parseFloat(text)); focus = false; }
                    Layout.fillWidth: true; color: "white"; background: Rectangle { color: "#1a1a1a"; radius: 5; border.color: activeFocus ? "#00f2ff" : "#333" } 
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "Overload Limit (Watts)"; color: "#888"; font.pixelSize: 12 }
                TextField { 
                    id: limitField
                    text: activeFocus ? text : (backend ? backend.overloadLimit.toString() : "0")
                    onAccepted: { if(backend) backend.setOverloadLimit(parseFloat(text)); focus = false; }
                    Layout.fillWidth: true; color: "white"; background: Rectangle { color: "#1a1a1a"; radius: 5; border.color: activeFocus ? "#00f2ff" : "#333" } 
                }
            }

            RowLayout {
                Layout.fillWidth: true; spacing: 10
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "Peak Start (0-23)"; color: "#888"; font.pixelSize: 11 }
                    TextField { 
                        id: startField
                        text: activeFocus ? text : (backend ? backend.peakStart.toString() : "0")
                        onAccepted: { if(backend) backend.setPeakStart(parseInt(text)); focus = false; }
                        Layout.fillWidth: true; color: "white"; background: Rectangle { color: "#1a1a1a"; radius: 5; border.color: activeFocus ? "#00f2ff" : "#333" } 
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "Peak End (0-23)"; color: "#888"; font.pixelSize: 11 }
                    TextField { 
                        id: endField
                        text: activeFocus ? text : (backend ? backend.peakEnd.toString() : "0")
                        onAccepted: { if(backend) backend.setPeakEnd(parseInt(text)); focus = false; }
                        Layout.fillWidth: true; color: "white"; background: Rectangle { color: "#1a1a1a"; radius: 5; border.color: activeFocus ? "#00f2ff" : "#333" } 
                    }
                }
            }

            Rectangle { height: 1; color: "#222"; Layout.fillWidth: true }

            Button {
                text: "📜 VIEW HISTORY"; Layout.fillWidth: true; Layout.preferredHeight: 40
                onClicked: { settingsPopup.close(); historyPopup.open(); }
                background: Rectangle { color: "#1a1a1a"; radius: 8; border.color: "#333" }
                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }

            Button {
                text: "📑 EXPORT PDF REPORT"; Layout.fillWidth: true; Layout.preferredHeight: 40
                onClicked: { if(backend) backend.exportPDF(); }
                background: Rectangle { color: "#1a1a1a"; radius: 8; border.color: "#00f2ff" }
                contentItem: Text { text: parent.text; color: "white"; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }

            Button {
                text: "🚪 LOGOUT SESSION"; Layout.fillWidth: true; Layout.preferredHeight: 40
                onClicked: { settingsPopup.close(); if(backend) backend.logout(); }
                background: Rectangle { color: "#2d1010"; radius: 8; border.color: "#d32f2f" }
                contentItem: Text { text: parent.text; color: "#ff8a80"; horizontalAlignment: Text.AlignHCenter; font.bold: true }
            }

            Item { Layout.fillHeight: true }
            Button { text: "CLOSE"; Layout.alignment: Qt.AlignHCenter; onClicked: settingsPopup.close(); flat: true }
        }
    }

    Rectangle {
        id: loginOverlay; anchors.fill: parent; color: "#0a0a0a"; z: 999
        MouseArea { anchors.fill: parent }
        ColumnLayout {
            anchors.centerIn: parent; spacing: 20
            Text { text: "SMART HOME LOGIN"; color: "#00f2ff"; font.pixelSize: 24; font.bold: true; Layout.alignment: Qt.AlignHCenter }
            TextField { id: userField; placeholderText: "Username"; Layout.preferredWidth: 300; color: "white"; background: Rectangle { radius: 5; color: "#1a1a1a"; border.color: "#333" } }
            TextField { id: passField; placeholderText: "Password"; echoMode: TextInput.Password; Layout.preferredWidth: 300; color: "white"; background: Rectangle { radius: 5; color: "#1a1a1a"; border.color: "#333" } }
            Button {
                text: "ACCESS DASHBOARD"; Layout.preferredWidth: 300; Layout.preferredHeight: 40; 
                onClicked: { if(backend) backend.login(userField.text, passField.text); }
                contentItem: Text { text: parent.text; color: "white"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 5; color: "#00f2ff" }
            }
        }
        Connections { 
            target: backend 
            function onLoginSuccess() { 
                loginOverlay.visible = false 
                userField.text = ""
                passField.text = ""
            }
            function onLogoutTriggered() { loginOverlay.visible = true }
        }
    }

    Popup {
        id: historyPopup; x: (parent.width - width) / 2; y: 100; width: 600; height: 500; modal: true; focus: true
        background: Rectangle { color: "#111"; radius: 15; border.color: "#333" }
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20
            Text { text: "CONSUMPTION HISTORY"; color: "#00f2ff"; font.bold: true; font.pixelSize: 18 }
            ListView {
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true; 
                model: backend ? backend.historyLogs : []
                spacing: 10
                delegate: Rectangle {
                    width: parent.width; height: 50; color: "#1a1a1a"; radius: 8
                    RowLayout {
                        anchors.fill: parent; anchors.margins: 15
                        Text { text: modelData.date; color: "#888"; Layout.fillWidth: true }
                        Text { text: modelData.kwh + " kWh"; color: "white"; font.bold: true }
                        Text { text: "Rs. " + modelData.cost; color: "#00ff88"; font.bold: true }
                    }
                }
            }
            Button { text: "CLOSE"; Layout.alignment: Qt.AlignRight; onClicked: historyPopup.close() }
        }
    }
}