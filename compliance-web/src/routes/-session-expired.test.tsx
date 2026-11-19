// @vitest-environment jsdom
import { act, ComponentType } from "react";
import { createRoot, Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useDrawer } from "@/store/drawerStore";
import { useModal } from "@/store/modalStore";
import { usePopover } from "@/store/popoverStore";
import { Route } from "./session-expired";

vi.mock("react-oidc-context", () => ({
  useAuth: () => ({ signinRedirect: vi.fn() }),
}));

const SessionExpired = Route.options.component as ComponentType;

describe("SessionExpired", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    (
      globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }
    ).IS_REACT_ACT_ENVIRONMENT = true;
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  it("closes the drawer, modal and popover left open by the expired session", async () => {
    await useDrawer.getState().setOpen({ content: <div>Order drawer</div> });
    await useModal.getState().setOpen({ content: <div>Modal</div> });
    await usePopover.getState().setOpen({
      anchorEl: document.body,
      content: <div>Popover</div>,
    });

    act(() => root.render(<SessionExpired />));

    expect(useDrawer.getState().isOpen).toBe(false);
    expect(useDrawer.getState().drawerContent).toBeNull();
    expect(useModal.getState().isOpen).toBe(false);
    expect(useModal.getState().modalContent).toBeNull();
    expect(usePopover.getState().anchorEl).toBeNull();
    expect(usePopover.getState().popoverContent).toBeNull();
  });
});
