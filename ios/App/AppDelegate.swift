import UIKit
import WebKit
import GameKit
import StoreKit

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

    // going to the background: fade the sound out and pause it, so nothing crackles or hisses on the way out
    func applicationWillResignActive(_ application: UIApplication) {
        (window?.rootViewController as? GameViewController)?.hush()
    }

    // back from the background: let the game check that its sound still works (it restarts itself if not)
    func applicationDidBecomeActive(_ application: UIApplication) {
        (window?.rootViewController as? GameViewController)?.wake()
    }
}

final class GameViewController: UIViewController, WKScriptMessageHandler {
    private var webView: WKWebView!

    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask { .portrait }

    func hush() {
        webView?.evaluateJavaScript("window.__hush && window.__hush()", completionHandler: nil)
    }

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
        config.userContentController.add(self, name: "gc")

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
        signIn()
    }

    // Game Center: sign in once at launch, then send up whatever was earned before sign-in
    private func signIn() {
        GKLocalPlayer.local.authenticateHandler = { [weak self] viewController, _ in
            guard let self = self else { return }
            if let viewController = viewController {
                self.present(viewController, animated: true)
            } else if GKLocalPlayer.local.isAuthenticated {
                self.webView?.evaluateJavaScript("window.__scSync && window.__scSync()", completionHandler: nil)
            }
        }
    }

    // the game reports an achievement: {t: 'ach', id: 'sc.<name>'}; or asks for a rating: {t: 'rate'}
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        if message.name == "gc", let body = message.body as? [String: Any], body["t"] as? String == "rate" {
            askRating(); return
        }
        if message.name == "gc", let body = message.body as? [String: Any], body["t"] as? String == "rateDebug" {
            debugRating(); return
        }
        guard message.name == "gc", let body = message.body as? [String: Any], body["t"] as? String == "ach",
              let id = body["id"] as? String, GKLocalPlayer.local.isAuthenticated else { return }
        let achievement = GKAchievement(identifier: id)
        achievement.percentComplete = 100
        achievement.showsCompletionBanner = true
        GKAchievement.report([achievement], withCompletionHandler: nil)
    }

    // the App Store rating sheet, once ever (iOS also skips it for anyone who has already rated, and limits it to 3 a year)
    private func askRating() {
        let key = "ratingAsked"
        guard !UserDefaults.standard.bool(forKey: key),
              let scene = view.window?.windowScene else { return }
        UserDefaults.standard.set(true, forKey: key)
        SKStoreReviewController.requestReview(in: scene)
    }

    // developer mode: ask now, whatever the once-only flag says, then tell the game whether the sheet came up.
    // iOS gives no answer of its own, so look for the sheet's window a moment later; TestFlight builds never show it.
    private func debugRating() {
        if Bundle.main.appStoreReceiptURL?.lastPathComponent == "sandboxReceipt" { reportRating("testflight"); return }
        guard let scene = view.window?.windowScene else { reportRating("rated"); return }
        SKStoreReviewController.requestReview(in: scene)
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            let shown = scene.windows.contains { !$0.isHidden && String(describing: type(of: $0)).contains("SKStoreReview") }
            self?.reportRating(shown ? "shown" : "rated")
        }
    }

    private func reportRating(_ result: String) {
        webView?.evaluateJavaScript("window.__rateResult && window.__rateResult('\(result)')", completionHandler: nil)
    }
}
