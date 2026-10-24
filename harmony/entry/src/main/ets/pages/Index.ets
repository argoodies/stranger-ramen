import { webview } from '@kit.ArkWeb';

@Entry
@Component
struct Index {
  private controller: webview.WebviewController = new webview.WebviewController();
  @StorageProp('safeTopPx') safeTopPx: number = 0;

  private run(js: string): void {
    try {
      this.controller.runJavaScript(js);
    } catch (e) {
      // the page is not ready yet: nothing to do
    }
  }

  private pushSafeTop(): void {
    this.run(`document.documentElement.style.setProperty('--sat','${Math.round(px2vp(this.safeTopPx))}px')`);
  }

  // back from the background: let the game check that its sound still works (it restarts itself if not)
  onPageShow(): void {
    this.run('window.__wake && window.__wake()');
  }

  // fade the sound out before the app is frozen, so nothing crackles on the way out
  onPageHide(): void {
    this.run('window.__hush && window.__hush()');
  }

  build() {
    Stack() {
      Web({ src: $rawfile('index.html'), controller: this.controller })
        .javaScriptAccess(true)
        .domStorageAccess(true)
        .fileAccess(true)
        .mediaPlayGestureAccess(false)
        .zoomAccess(false)
        .textZoomRatio(100)
        .overScrollMode(OverScrollMode.NEVER)
        .horizontalScrollBarAccess(false)
        .verticalScrollBarAccess(false)
        .backgroundColor('#0E0C24')
        .width('100%')
        .height('100%')
        .expandSafeArea([SafeAreaType.SYSTEM, SafeAreaType.CUTOUT], [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM])
        .onPageEnd(() => this.pushSafeTop())
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0E0C24')
    .expandSafeArea([SafeAreaType.SYSTEM, SafeAreaType.CUTOUT], [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM])
  }
}
