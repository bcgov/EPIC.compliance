import { beforeEach, describe, expect, it, vi } from "vitest";
import { useInspectionOrderRendered } from "./useInspectionOrders";
import { useWarningLetterRendered } from "./useInspectionWarningLetters";

const mocks = vi.hoisted(() => ({ request: vi.fn() }));

vi.mock("@/utils/axiosUtils", () => ({ request: mocks.request }));

// Hand the mutation options straight back so the request each hook builds can be inspected
vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => options,
  useQuery: vi.fn(),
}));

type RenderFn<T> = { mutationFn: (variables: T) => unknown };

const useOrderRenderFn = () =>
  (
    useInspectionOrderRendered(vi.fn(), vi.fn()) as unknown as RenderFn<{
      inspectionOrderId: number;
      format: "html" | "pdf" | "docx";
    }>
  ).mutationFn;

const useWarningLetterRenderFn = () =>
  (
    useWarningLetterRendered(vi.fn(), vi.fn()) as unknown as RenderFn<{
      inspectionWarningLetterId: number;
      format: "html" | "pdf" | "docx";
    }>
  ).mutationFn;

describe("enforcement render requests", () => {
  beforeEach(() => {
    mocks.request.mockReset();
  });

  it.each(["docx", "pdf"] as const)(
    "asks for an order %s as a blob",
    (format) => {
      useOrderRenderFn()({ inspectionOrderId: 7, format });
      expect(mocks.request).toHaveBeenCalledWith({
        method: "POST",
        url: "/orders/7/render",
        data: { output_format: format },
        responseType: "blob",
      });
    }
  );

  it("asks for an order preview as json", () => {
    useOrderRenderFn()({ inspectionOrderId: 7, format: "html" });
    expect(mocks.request).toHaveBeenCalledWith(
      expect.objectContaining({ responseType: "json" })
    );
  });

  it.each(["docx", "pdf"] as const)(
    "asks for a warning letter %s as a blob",
    (format) => {
      useWarningLetterRenderFn()({ inspectionWarningLetterId: 9, format });
      expect(mocks.request).toHaveBeenCalledWith({
        method: "POST",
        url: "/warning-letters/9/render",
        data: { output_format: format },
        responseType: "blob",
      });
    }
  );

  it("asks for a warning letter preview as json", () => {
    useWarningLetterRenderFn()({ inspectionWarningLetterId: 9, format: "html" });
    expect(mocks.request).toHaveBeenCalledWith(
      expect.objectContaining({ responseType: "json" })
    );
  });
});
