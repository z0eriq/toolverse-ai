import { describe, expect, it } from "vitest";
import { cn, localize } from "@/lib/utils";

describe("utils", () => {
  it("merges class names", () => {
    expect(cn("px-2", "px-4", false && "hidden")).toBe("px-4");
  });

  it("localizes strings", () => {
    expect(localize({ en: "Hello", ar: "مرحبا" }, "ar")).toBe("مرحبا");
    expect(localize({ en: "Hello" }, "ar")).toBe("Hello");
    expect(localize("plain", "en")).toBe("plain");
  });
});
