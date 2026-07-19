import type { ToolFrontendModule } from "@toolverse/tool-sdk";
import { toolsBySlug } from "./tools.generated";

export function getToolBySlug(slug: string): ToolFrontendModule | undefined {
  return toolsBySlug[slug];
}

export function getAllTools(): ToolFrontendModule[] {
  return Object.values(toolsBySlug).sort(
    (a, b) => (a.manifest.order ?? 0) - (b.manifest.order ?? 0),
  );
}

export function getToolsByCategory(category: string): ToolFrontendModule[] {
  return getAllTools().filter((t) => t.manifest.category === category);
}

export function getFeaturedTools(limit = 6): ToolFrontendModule[] {
  return getAllTools().slice(0, limit);
}

export { toolsBySlug };
