import React from "react";
import { AbsoluteFill, Audio, useVideoConfig, staticFile } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { Storyboard, Scene } from "./types";
import { TitleScene } from "./scenes/TitleScene";
import { ContentScene } from "./scenes/ContentScene";
import { DiagramScene } from "./scenes/DiagramScene";
import { OutroScene } from "./scenes/OutroScene";

const TRANSITION_FRAMES = 15;

const SceneComponent: React.FC<{ scene: Scene }> = ({ scene }) => {
  switch (scene.type) {
    case "title": return <TitleScene scene={scene} />;
    case "outro": return <OutroScene scene={scene} />;
    case "diagram": return <DiagramScene scene={scene} />;
    default: return <ContentScene scene={scene} />;
  }
};

export const Video: React.FC<Storyboard> = (storyboard) => {
  const { fps } = useVideoConfig();
  const scenes = storyboard.scenes;
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020" }}>
      <TransitionSeries>
        {scenes.map((sc, i) => (
          <React.Fragment key={sc.id}>
            <TransitionSeries.Sequence durationInFrames={Math.max(1, Math.round(sc.durationSec * fps))}>
              <SceneComponent scene={sc} />
              {sc.audioFile && <Audio src={staticFile(sc.audioFile)} />}
            </TransitionSeries.Sequence>
            {i < scenes.length - 1 && (
              <TransitionSeries.Transition
                presentation={sc.transition === "slide" ? slide() : fade()}
                timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
              />
            )}
          </React.Fragment>
        ))}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
