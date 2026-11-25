import React from "react";
import { Composition, CalculateMetadataFunction } from "remotion";
import { z } from "zod";
import { HelloVideo } from "./HelloVideo";
import { Video } from "./Video";
import { Storyboard } from "./types";

const storyboardSchema = z.object({
  jobId: z.string(),
  title: z.string(),
  fps: z.number(),
  width: z.number(),
  height: z.number(),
  totalDurationSec: z.number(),
  music: z.string().nullish(),
  scenes: z.array(z.any()),
});

const calcMetadata: CalculateMetadataFunction<Storyboard> = ({ props }) => {
  const fps = props.fps || 30;
  const totalFrames = Math.max(
    1,
    Math.round((props.totalDurationSec || 10) * fps) - (Math.max(0, props.scenes.length - 1) * 15)
  );
  return {
    durationInFrames: totalFrames,
    fps,
    width: props.width || 1920,
    height: props.height || 1080,
    props,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Hello" component={HelloVideo} durationInFrames={150} fps={30} width={1920} height={1080} />
      <Composition
        id="Explainer"
        component={Video}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        schema={storyboardSchema}
        calculateMetadata={calcMetadata}
        defaultProps={{
          jobId: "demo",
          title: "Demo",
          fps: 30,
          width: 1920,
          height: 1080,
          totalDurationSec: 10,
          scenes: [],
        } as Storyboard}
      />
    </>
  );
};
