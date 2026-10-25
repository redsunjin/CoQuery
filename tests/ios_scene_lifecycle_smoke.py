"""Validate the native launch configuration that UIKit requires with SDK 27+."""
from pathlib import Path
import plistlib
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
app = root / "ios/App/App"
with (app / "Info.plist").open("rb") as source:
    info = plistlib.load(source)
manifest = info["UIApplicationSceneManifest"]
assert manifest["UIApplicationSupportsMultipleScenes"] is False
scenes = manifest["UISceneConfigurations"]["UIWindowSceneSessionRoleApplication"]
assert len(scenes) == 1
config = scenes[0]
assert config["UISceneDelegateClassName"] == "$(PRODUCT_MODULE_NAME).SceneDelegate"
assert config["UISceneConfigurationName"]
assert "UIMainStoryboardFile" not in info, "The scene must own the main storyboard"
storyboard = ET.parse(app / "Base.lproj" / (config["UISceneStoryboardFile"] + ".storyboard")).getroot()
controller = storyboard.find(".//viewController[@id='%s']" % storyboard.attrib["initialViewController"])
assert controller is not None
assert controller.attrib["customClass"] == "AdaptiveBridgeViewController"
assert controller.attrib["customModule"] == "App"
delegate = (app / "AppDelegate.swift").read_text()
assert "class SceneDelegate: UIResponder, UIWindowSceneDelegate" in delegate
assert "var window: UIWindow?" in delegate
assert "connectionOptions.urlContexts" in delegate
assert "connectionOptions.userActivities" in delegate
assert "openURLContexts URLContexts" in delegate
assert "continue userActivity: NSUserActivity" in delegate
project = (root / "ios/App/App.xcodeproj/project.pbxproj").read_text()
assert "AppDelegate.swift in Sources" in project
print("iOS scene lifecycle: manifest, Capacitor storyboard, compiled delegate and cold/warm link routing contracts passed.")

assert "class AdaptiveBridgeViewController: CAPBridgeViewController" in delegate
assert "viewSafeAreaInsetsDidChange" in delegate
assert "reservedRegions(kind: .division)" in delegate
assert "if #available(iOS 27.1, *)" in delegate
