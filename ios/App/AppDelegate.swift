import UIKit
import WebKit

// Thin native shell: the whole game is the bundled web/index.html, shown full screen in a WKWebView.
@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        let window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = GameViewController()
        window.makeKeyAndVisible()
        self.window = window
        return true
    }

    // back from the background: let the game check that its sound still works (it restarts itself if not)
    func applicationDidBecomeActive(_ application: UIApplication) {
        (window?.rootViewController as? GameViewController)?.wake()
    }
}

final class GameViewController: UIViewController {
    private var webView: WKWebView!

    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { .portrait }

    func wake() {
        webView?.evaluateJavaScript("window.__wake && window.__wake()", completionHandler: nil)
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 14 / 255, green: 12 / 255, blue: 36 / 255, alpha: 1)

        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        // no long-press callout / text selection inside the game
        let css = "*{-webkit-touch-callout:none;-webkit-user-select:none}"
        let js = "var s=document.createElement('style');s.textContent='\(css)';document.documentElement.appendChild(s);"
        config.userContentController.addUserScript(
            WKUserScript(source: js, injectionTime: .atDocumentEnd, forMainFrameOnly: true))

        webView = WKWebView(frame: view.bounds, configuration: config)
        webView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        webView.isOpaque = false
        webView.backgroundColor = view.backgroundColor
        webView.scrollView.backgroundColor = view.backgroundColor
        webView.scrollView.isScrollEnabled = false
        webView.scrollView.bounces = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.allowsLinkPreview = false
        view.addSubview(webView)

        guard let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "web") else {
            fatalError("web/index.html missing from the app bundle")
        }
        webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
    }
}
