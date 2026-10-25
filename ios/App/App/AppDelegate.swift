import UIKit
import Capacitor
import WebKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        // Called when the app was launched with a url. Feel free to add additional processing here,
        // but if you want the App API to support tracking app url opens, make sure to keep this call
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        // Called when the app was launched with an activity, including Universal Links.
        // Feel free to add additional processing here, but if you want the App API to support
        // tracking app url opens, make sure to keep this call
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }

}

// UIKit owns the window through a scene; Main keeps the existing Capacitor UI.
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        forward(connectionOptions.urlContexts)
        for activity in connectionOptions.userActivities {
            _ = ApplicationDelegateProxy.shared.application(UIApplication.shared, continue: activity, restorationHandler: { _ in })
        }
    }

    func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
        forward(URLContexts)
    }

    func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
        _ = ApplicationDelegateProxy.shared.application(UIApplication.shared, continue: userActivity, restorationHandler: { _ in })
    }

    private func forward(_ contexts: Set<UIOpenURLContext>) {
        for context in contexts {
            _ = ApplicationDelegateProxy.shared.application(UIApplication.shared, open: context.url, options: [
                .sourceApplication: context.options.sourceApplication as Any,
                .annotation: context.options.annotation as Any,
                .openInPlace: context.options.openInPlace
            ])
        }
    }
}

// Publish actual window insets to the custom web UI; no screen/device assumptions.
class AdaptiveBridgeViewController: CAPBridgeViewController {
    private var lastGeometry = ""
    private var geometryHandler: GeometryMessageHandler?

    override func capacitorDidLoad() {
        guard let content = webView?.configuration.userContentController else { return }
        let handler = GeometryMessageHandler(owner: self)
        geometryHandler = handler
        content.add(handler, name: "coqueryGeometry")
        let script = """
        window.coqueryNativeLayout = function(g) {
          window.coqueryWindowGeometry = g;
          const root = document.documentElement;
          if (!root || !g.width) return;
          const ratio = window.innerWidth / g.width;
          ['top','right','bottom','left'].forEach(function(edge) {
            root.style.setProperty('--safe-area-' + edge, Math.max(0,g.insets[edge]*ratio) + 'px');
          });
          window.dispatchEvent(new CustomEvent('coquery:geometry', {detail:g}));
        };
        document.addEventListener('DOMContentLoaded',function() {
          window.webkit.messageHandlers.coqueryGeometry.postMessage('ready');
        });
        """
        content.addUserScript(WKUserScript(source: script, injectionTime: .atDocumentStart, forMainFrameOnly: true))
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        publishGeometry()
    }

    override func viewSafeAreaInsetsDidChange() {
        super.viewSafeAreaInsetsDidChange()
        publishGeometry()
    }

    func publishGeometry(force: Bool = false) {
        guard let webView = webView, webView.bounds.width > 0 else { return }
        let inset = webView.safeAreaInsets
        var divisions: [[String: CGFloat]] = []
        if #available(iOS 27.1, *) {
            divisions = webView.reservedRegions(kind: .division).map { region in
                ["x": region.frame.minX, "y": region.frame.minY,
                 "width": region.frame.width, "height": region.frame.height]
            }
        }
        let geometry: [String: Any] = [
            "width":webView.bounds.width,"height":webView.bounds.height,
            "insets":["top":inset.top,"right":inset.right,"bottom":inset.bottom,"left":inset.left],
            "divisions": divisions
        ]
        guard let data = try? JSONSerialization.data(withJSONObject:geometry,options:.sortedKeys),
              let json = String(data:data,encoding:.utf8), force || json != lastGeometry else { return }
        lastGeometry = json
        webView.evaluateJavaScript("window.coqueryNativeLayout?.(\(json));",completionHandler:nil)
        #if DEBUG
        print("[CoQuery geometry] \(json)")
        #endif
    }
}

private class GeometryMessageHandler: NSObject, WKScriptMessageHandler {
    weak var owner: AdaptiveBridgeViewController?
    init(owner: AdaptiveBridgeViewController) { self.owner = owner }
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.frameInfo.isMainFrame, message.body as? String == "ready" else { return }
        owner?.publishGeometry(force:true)
    }
}
