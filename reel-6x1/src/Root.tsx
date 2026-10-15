import { Composition } from "remotion";
import { Cover } from "./Cover";
import { CaptionsOnly, Main, MainProps } from "./Main";
import { FPS, H, TOTAL_FRAMES, W } from "./util";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Reel"
      component={Main}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={W}
      height={H}
      defaultProps={{ captions: true, audio: true } as MainProps}
    />
    <Composition id="Capa" component={Cover} durationInFrames={1} fps={FPS} width={W} height={H} />
    <Composition id="Legendas" component={CaptionsOnly} durationInFrames={TOTAL_FRAMES} fps={FPS} width={W} height={H} />
  </>
);
