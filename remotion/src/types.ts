export type Visual = {
  kind: "image" | "shapes" | "text-only";
  imagePrompt?: string;
  imageFile?: string;
  kenBurns?: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "none";
};

export type Scene = {
  id: string;
  type: "title" | "content" | "diagram" | "outro";
  durationSec: number;
  transition: "fade" | "slide" | "zoom" | "none";
  narration: string;
  audioFile?: string;
  visual: Visual;
  headline?: string;
  bullets?: string[];
  caption?: string;
};

export type Storyboard = {
  jobId: string;
  title: string;
  fps: number;
  width: number;
  height: number;
  totalDurationSec: number;
  music?: string;
  scenes: Scene[];
};
