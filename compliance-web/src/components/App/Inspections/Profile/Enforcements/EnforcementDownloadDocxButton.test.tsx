// @vitest-environment jsdom
import { act } from "react";
import { createRoot, Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { EnforcementActionEnum } from "@/utils/constants";
import EnforcementDownloadDocxButton from "./EnforcementDownloadDocxButton";

type OnSuccess = (data: Blob) => void;
type OnError = (error: { message?: string }) => void;

const mocks = vi.hoisted(() => ({
  orderMutate: vi.fn(),
  warningLetterMutate: vi.fn(),
  downloadFile: vi.fn(),
  notifyError: vi.fn(),
  orderCallbacks: {} as { onSuccess?: OnSuccess; onError?: OnError },
  warningLetterCallbacks: {} as { onSuccess?: OnSuccess; onError?: OnError },
}));

vi.mock("@/hooks/useInspectionOrders", () => ({
  useInspectionOrderRendered: (onSuccess: OnSuccess, onError: OnError) => {
    mocks.orderCallbacks.onSuccess = onSuccess;
    mocks.orderCallbacks.onError = onError;
    return { mutate: mocks.orderMutate };
  },
}));

vi.mock("@/hooks/useInspectionWarningLetters", () => ({
  useWarningLetterRendered: (onSuccess: OnSuccess, onError: OnError) => {
    mocks.warningLetterCallbacks.onSuccess = onSuccess;
    mocks.warningLetterCallbacks.onError = onError;
    return { mutate: mocks.warningLetterMutate };
  },
}));

vi.mock("@/utils/appUtils", () => ({
  downloadFile: mocks.downloadFile,
}));

vi.mock("@/store/snackbarStore", () => ({
  notify: { error: mocks.notifyError },
}));

describe("EnforcementDownloadDocxButton", () => {
  let container: HTMLDivElement;
  let root: Root;

  const render = (enforcementType: EnforcementActionEnum, fileNumber: string) => {
    act(() => {
      root.render(
        <EnforcementDownloadDocxButton
          enforcementId={7}
          fileNumber={fileNumber}
          enforcementType={enforcementType}
        />
      );
    });
    return container.querySelector("button") as HTMLButtonElement;
  };

  beforeEach(() => {
    (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    vi.clearAllMocks();
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  it("is labelled Download DOCX", () => {
    const button = render(EnforcementActionEnum.ORDER, "EAO-1");
    expect(button.textContent).toBe("Download DOCX");
    expect(button.disabled).toBe(false);
  });

  it("requests an order as docx and saves it with a .docx name", () => {
    const button = render(EnforcementActionEnum.ORDER, "EAO-1");
    act(() => button.click());

    expect(mocks.orderMutate).toHaveBeenCalledWith({
      inspectionOrderId: 7,
      format: "docx",
    });
    expect(mocks.warningLetterMutate).not.toHaveBeenCalled();

    const blob = new Blob(["docx"]);
    act(() => mocks.orderCallbacks.onSuccess?.(blob));
    expect(mocks.downloadFile).toHaveBeenCalledWith(blob, "EAO-1.docx");
  });

  it("requests a warning letter as docx and saves it with a .docx name", () => {
    const button = render(EnforcementActionEnum.WARNING_LETTER, "WL-1");
    act(() => button.click());

    expect(mocks.warningLetterMutate).toHaveBeenCalledWith({
      inspectionWarningLetterId: 7,
      format: "docx",
    });
    expect(mocks.orderMutate).not.toHaveBeenCalled();

    const blob = new Blob(["docx"]);
    act(() => mocks.warningLetterCallbacks.onSuccess?.(blob));
    expect(mocks.downloadFile).toHaveBeenCalledWith(blob, "WL-1.docx");
  });

  it("shows a disabled loading state until the download arrives", () => {
    const button = render(EnforcementActionEnum.ORDER, "EAO-1");
    act(() => button.click());
    expect(button.textContent).toBe("Loading...");
    expect(button.disabled).toBe(true);

    act(() => mocks.orderCallbacks.onSuccess?.(new Blob(["docx"])));
    expect(button.textContent).toBe("Download DOCX");
    expect(button.disabled).toBe(false);
  });

  it("reports a failure and re-enables the button", () => {
    const button = render(EnforcementActionEnum.ORDER, "EAO-1");
    act(() => button.click());
    act(() => mocks.orderCallbacks.onError?.({}));

    expect(mocks.notifyError).toHaveBeenCalledWith("Error downloading DOCX");
    expect(mocks.downloadFile).not.toHaveBeenCalled();
    expect(button.disabled).toBe(false);
  });
});
