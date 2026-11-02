import UIKit
import WebKit
import GameKit

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

    private let sky = CAGradientLayer()

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        sky.frame = view.bounds
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        // the game's daytime sky behind the web view, so nothing dark shows while the page loads
        let rgb: [[CGFloat]] = [[226, 150, 130], [214, 166, 156], [204, 150, 148]]
        sky.colors = rgb.map { UIColor(red: $0[0] / 255, green: $0[1] / 255, blue: $0[2] / 255, alpha: 1).cgColor }
        sky.frame = view.bounds
        view.layer.insertSublayer(sky, at: 0)

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
        webView.backgroundColor = .clear
        webView.scrollView.backgroundColor = .clear
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
                self.webView?.evaluateJavaScript("window.__gcSync && window.__gcSync()", completionHandler: nil)
            }
        }
    }

    // messages from the game: an achievement and the best streak
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "gc", let body = message.body as? [String: Any], let type = body["t"] as? String else { return }
        switch type {
        case "ach":
            guard GKLocalPlayer.local.isAuthenticated, let id = body["id"] as? String else { return }
            let achievement = GKAchievement(identifier: id)
            achievement.percentComplete = 100
            achievement.showsCompletionBanner = true
            GKAchievement.report([achievement], withCompletionHandler: nil)
        case "score":
            guard GKLocalPlayer.local.isAuthenticated, let value = (body["v"] as? NSNumber)?.intValue else { return }
            GKLeaderboard.submitScore(value, context: 0, player: GKLocalPlayer.local, leaderboardIDs: ["pc.total_wins"], completionHandler: { _ in })
        default:
            break
        }
    }
}
