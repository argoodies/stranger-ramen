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
    // iPhone: portrait only; iPad: any way round
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        UIDevice.current.userInterfaceIdiom == .pad ? .all : .portrait
    }

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
        // (from then on the page reports its sky as it changes — see the "sky" message — so this tracks dusk and night too)
        let rgb: [[CGFloat]] = [[226, 150, 130], [214, 166, 156], [204, 150, 148]]
        sky.colors = rgb.map { UIColor(red: $0[0] / 255, green: $0[1] / 255, blue: $0[2] / 255, alpha: 1).cgColor }
        sky.locations = [0, 0.5, 1]
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

    // messages from the game: an achievement, the total wins, and a request for your rank
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "gc", let body = message.body as? [String: Any], let type = body["t"] as? String else { return }
        switch type {
        case "ach":
            guard let id = body["id"] as? String else { return }
            guard GKLocalPlayer.local.isAuthenticated else { return }
            let achievement = GKAchievement(identifier: id)
            achievement.percentComplete = 100
            achievement.showsCompletionBanner = true
            GKAchievement.report([achievement], withCompletionHandler: nil)
        case "score":
            guard GKLocalPlayer.local.isAuthenticated, let value = (body["v"] as? NSNumber)?.intValue else { return }
            GKLeaderboard.submitScore(value, context: 0, player: GKLocalPlayer.local, leaderboardIDs: ["pc.total_wins"], completionHandler: { _ in })
        case "rank":
            loadRank()
        case "sky":
            // the game's current sky (top, middle, bottom), so whatever a rotation uncovers behind the web view matches it
            guard let c = body["c"] as? [[NSNumber]], c.count == 3, c.allSatisfy({ $0.count == 3 }) else { return }
            CATransaction.begin(); CATransaction.setDisableActions(true)
            sky.colors = c.map { UIColor(red: CGFloat($0[0].doubleValue) / 255, green: CGFloat($0[1].doubleValue) / 255, blue: CGFloat($0[2].doubleValue) / 255, alpha: 1).cgColor }
            CATransaction.commit()
        default:
            break
        }
    }

    // the ball in the lobby (after a win) asks for your place on the Most Wins board, to say it in a bubble: no Game Center screen.
    // Signed out, offline or never ranked: null, and the ball says your wins alone.
    private func loadRank() {
        guard GKLocalPlayer.local.isAuthenticated else { return replyRank(nil) }
        GKLeaderboard.loadLeaderboards(IDs: ["pc.total_wins"]) { [weak self] boards, _ in
            guard let board = boards?.first else { self?.replyRank(nil); return }
            board.loadEntries(for: [GKLocalPlayer.local], timeScope: .allTime) { local, _, _ in
                self?.replyRank(local)
            }
        }
    }

    private func replyRank(_ entry: GKLeaderboard.Entry?) {
        let arg = entry.map { "{rank:\($0.rank),score:\($0.score)}" } ?? "null"
        DispatchQueue.main.async { [weak self] in
            self?.webView?.evaluateJavaScript("window.__gcRank && window.__gcRank(\(arg))", completionHandler: nil)
        }
    }
}
