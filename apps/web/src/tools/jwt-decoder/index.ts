import type { ToolFrontendModule } from "@toolverse/tool-sdk";
import { manifest } from "./manifest";
import { Tool } from "./Tool";

const mod: ToolFrontendModule = { manifest, Component: Tool };
export default mod;
export { manifest };
