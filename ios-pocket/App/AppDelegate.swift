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

final class GameViewController: UIViewController, WKScriptMessageHandler, GKGameCenterControllerDelegate {
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

    // TestFlight only (a sandbox receipt): a Game Center failure shows as a small note at the top for a few seconds;
    // nothing shows when all goes well, and the App Store build never shows it
    private let isTestFlight = Bundle.main.appStoreReceiptURL?.lastPathComponent == "sandboxReceipt"

    private func testNote(_ text: String) {
        guard isTestFlight else { return }
        guard let data = try? JSONSerialization.data(withJSONObject: [text]), let arg = String(data: data, encoding: .utf8) else { return }
        let js = "(function(t){var d=document.createElement('div');d.textContent=t[0];d.style.cssText='position:fixed;left:50%;top:calc(env(safe-area-inset-top) + 10px);transform:translateX(-50%);z-index:99999;max-width:88%;padding:7px 11px;border-radius:9px;background:rgba(0,0,0,.8);color:#fff;font:12px -apple-system,sans-serif;pointer-events:none';document.body.appendChild(d);setTimeout(function(){d.remove()},6000)})(\(arg))"
        DispatchQueue.main.async { self.webView?.evaluateJavaScript(js, completionHandler: nil) }
    }

    // messages from the game: an achievement and the total wins
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "gc", let body = message.body as? [String: Any], let type = body["t"] as? String else { return }
        switch type {
        case "ach":
            guard let id = body["id"] as? String else { return }
            guard GKLocalPlayer.local.isAuthenticated else { return testNote("Game Center: not signed in, \(id) not sent") }
            let achievement = GKAchievement(identifier: id)
            achievement.percentComplete = 100
            achievement.showsCompletionBanner = true
            GKAchievement.report([achievement]) { [weak self] error in
                if let error = error { self?.testNote("Game Center refused \(id): \(error.localizedDescription)") }
            }
        case "score":
            guard GKLocalPlayer.local.isAuthenticated, let value = (body["v"] as? NSNumber)?.intValue else { return }
            GKLeaderboard.submitScore(value, context: 0, player: GKLocalPlayer.local, leaderboardIDs: ["pc.total_wins"]) { [weak self] error in
                if let error = error { self?.testNote("Game Center refused the score \(value): \(error.localizedDescription)") }
            }
        case "board":
            showBoard()
        default:
            break
        }
    }

    // the capsule at the top of the lobby: Apple's own Game Center screen, opened on the Most Wins leaderboard.
    // Signed out, it asks for sign-in first (the system sheet), then opens the board.
    private func showBoard() {
        guard presentedViewController == nil else { return }
        let open = { [weak self] in
            guard let self = self, self.presentedViewController == nil else { return }
            let vc = GKGameCenterViewController(leaderboardID: "pc.total_wins", playerScope: .global, timeScope: .allTime)
            vc.gameCenterDelegate = self
            self.present(vc, animated: true)
        }
        if GKLocalPlayer.local.isAuthenticated { return open() }
        GKLocalPlayer.local.authenticateHandler = { [weak self] viewController, _ in
            guard let self = self else { return }
            if let viewController = viewController { self.present(viewController, animated: true) }
            else if GKLocalPlayer.local.isAuthenticated {
                self.webView?.evaluateJavaScript("window.__gcSync && window.__gcSync()", completionHandler: nil)
                open()
            } else { self.testNote("Game Center: not signed in") }
        }
    }

    func gameCenterViewControllerDidFinish(_ gameCenterViewController: GKGameCenterViewController) {
        gameCenterViewController.dismiss(animated: true)
    }
}
