import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';

const DOMAIN = 0x0000;
const TAG = 'RamenPuzzle';

// Thin native shell, like the Android one: the whole game is the bundled rawfile/index.html, shown full screen.
export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    hilog.info(DOMAIN, TAG, 'onCreate reason=%{public}d', launchParam.launchReason);
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.getMainWindow().then((win: window.Window) => {
      // draw under the status bar and the camera cutout, and hide the system bars: the game fills the whole screen
      win.setWindowLayoutFullScreen(true);
      win.setSpecificSystemBarEnabled('status', false);
      win.setSpecificSystemBarEnabled('navigationIndicator', false);
      win.setWindowBackgroundColor('#0E0C24');
      win.setWindowKeepScreenOn(false);
      // the page keeps its buttons clear of the cutout with --sat (as on Android): measure it here, in vp
      const cut = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_CUTOUT);
      AppStorage.setOrCreate('safeTopPx', cut.topRect.top + cut.topRect.height);
    }).catch((err: Error) => hilog.error(DOMAIN, TAG, 'main window: %{public}s', err.message));
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, TAG, 'loadContent failed code=%{public}d %{public}s', err.code, err.message);
      }
    });
  }
}
