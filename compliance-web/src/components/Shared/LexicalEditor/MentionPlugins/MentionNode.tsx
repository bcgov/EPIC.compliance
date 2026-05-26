/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import { Popover } from "@mui/material";
import {
  $applyNodeReplacement,
  type DOMConversionMap,
  type DOMConversionOutput,
  type DOMExportOutput,
  type EditorConfig,
  type LexicalNode,
  type NodeKey,
  type SerializedTextNode,
  type Spread,
  TextNode,
  $createRangeSelection,
  $setSelection,
  type RangeSelection,
  $getSelection,
} from "lexical";
import React from "react";

export type SerializedMentionNode = Spread<
  {
    mentionName: string;
    imageUrl: string;
    imageId: number;
  },
  SerializedTextNode
>;

function $convertMentionElement(
  domNode: HTMLElement
): DOMConversionOutput | null {
  const textContent = domNode.textContent;
  const mentionName = domNode.getAttribute("data-lexical-mention-name");
  const imageUrl = domNode.getAttribute("data-imageurl");
  const imageId = domNode.getAttribute("data-imageid");

  if (textContent !== null) {
    const node = $createMentionNode(
      typeof mentionName === "string" ? mentionName : textContent,
      textContent,
      imageUrl ?? undefined,
      imageId ? parseInt(imageId) : undefined
    );

    return {
      node,
    };
  }

  return null;
}

export class MentionNode extends TextNode {
  __mention: string;
  __imageUrl: string;
  __imageId: number;

  static getType(): string {
    return "mention";
  }

  static clone(node: MentionNode): MentionNode {
    return new MentionNode(
      node.__mention,
      node.__text,
      node.__imageUrl,
      node.__imageId,
      node.__key
    );
  }
  static importJSON(serializedNode: SerializedMentionNode): MentionNode {
    return $createMentionNode(serializedNode.mentionName).updateFromJSON(
      serializedNode
    );
  }

  constructor(
    mentionName: string,
    text?: string,
    imageUrl?: string,
    imageId?: number,
    key?: NodeKey
  ) {
    super(text ?? mentionName, key);
    this.__mention = mentionName;
    this.__imageUrl = imageUrl ?? "";
    this.__imageId = imageId ?? 0;
  }

  exportJSON(): SerializedMentionNode {
    return {
      ...super.exportJSON(),
      mentionName: this.__mention,
      imageUrl: this.__imageUrl,
      imageId: this.__imageId,
    };
  }

  createDOM(config: EditorConfig): HTMLElement {
    const dom = super.createDOM(config);

    // Style as a chip instead of just text with background
    dom.style.cssText = `
      display: inline-flex;
      align-items: center;
      background-color: rgba(24, 119, 232, 0.2);
      border-radius: 8px;
      padding: 0 8px 0 8px;
      margin: 0 2px;
      height: 24px;
      font-size: 0.875rem;
      font-weight: bold;
      line-height: 1.2;
      cursor: default;
      user-select: none;
      -webkit-user-select: none;
      white-space: nowrap;
      pointer-events: all;
    `;
    dom.className = "mention-chip";
    dom.spellcheck = false;
    dom.contentEditable = "false";
    dom.dataset.imageurl = this.__imageUrl;
    dom.dataset.mention = this.__mention;
    dom.dataset.imageid = this.__imageId.toString();

    // Create wrapper for positioning
    const wrapper = document.createElement("span");
    wrapper.style.position = "relative";
    wrapper.style.display = "inline-flex";
    wrapper.style.alignItems = "center";
    wrapper.style.userSelect = "none";
    wrapper.contentEditable = "false";
    wrapper.appendChild(dom);

    // Add click handler to move cursor to end of mention node
    dom.addEventListener("click", (e) => {
      e.stopPropagation();

      // Reference to this node
      const nodeKey = this.__key;

      // Find the editor
      const editorElement = dom.closest(".editor-input");
      if (editorElement) {
        // Dispatch a custom event to handle the selection correctly
        const event = new CustomEvent("lexical-command", {
          bubbles: true,
          cancelable: true,
          detail: {
            type: "move-selection-after-mention",
            key: nodeKey,
          },
        });
        editorElement.dispatchEvent(event);
      }
    });

    // Handle keyboard navigation
    dom.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.stopPropagation();

        // Reference to this node
        const nodeKey = this.__key;

        // Find the editor
        const editorElement = dom.closest(".editor-input");
        if (editorElement) {
          // Dispatch a custom event to handle the navigation correctly
          const event = new CustomEvent("lexical-command", {
            bubbles: true,
            cancelable: true,
            detail: {
              type: "navigate-from-mention",
              key: nodeKey,
              direction: e.key === "ArrowLeft" ? "left" : "right",
            },
          });
          editorElement.dispatchEvent(event);
        }
      }
    });

    // Create a close button that appears on hover
    const closeButton = document.createElement("span");
    closeButton.innerHTML = "✕";
    closeButton.style.cssText = `
      cursor: pointer;
      padding-left: 4px;
      font-size: inherit;
      color: #666;
      display: none;
      opacity: 0;
      transition: opacity 0.2s;
      user-select: none;
      pointer-events: all;
      display: inline;
      position: absolute;
      right: -12px;
      background: rgb(213, 229, 251);
      padding: 4px 6px;
      border-top-right-radius: 8px;
      border-bottom-right-radius: 8px;
    `;
    closeButton.className = "mention-close-btn";

    // Show/hide close button on hover
    dom.addEventListener("mouseenter", () => {
      closeButton.style.visibility = "visible";
      setTimeout(() => {
        closeButton.style.opacity = "1";
      }, 10);
    });

    dom.addEventListener("mouseleave", () => {
      closeButton.style.opacity = "0";
      setTimeout(() => {
        if (closeButton.style.opacity === "0") {
          closeButton.style.visibility = "hidden";
        }
      }, 200);
    });

    // Handle close button click - remove the mention node
    closeButton.addEventListener("click", (e) => {
      e.stopPropagation();

      // Store a reference to this node
      const nodeKey = this.__key;

      // Find the editor - all nodes are connected to their editor via DOM
      const editorElement = dom.closest(".editor-input");
      if (editorElement) {
        // Dispatch a custom command to remove this node
        const event = new CustomEvent("lexical-command", {
          bubbles: true,
          cancelable: true,
          detail: { type: "remove-mention", key: nodeKey },
        });
        editorElement.dispatchEvent(event);
      }
    });

    // Append close button to chip
    dom.appendChild(closeButton);

    // Add image preview on hover functionality
    if (this.__imageUrl) {
      // Create a unique ID for this mention element
      const mentionId = `mention-${Math.random().toString(36).substring(2, 11)}`;
      dom.id = mentionId;

      // Create React component with Popover - using global React reference
      const PopoverComponent = React.lazy(() =>
        Promise.resolve({
          default: () => {
            const MentionPopover = () => {
              const [anchorEl, setAnchorEl] =
                React.useState<HTMLElement | null>(null);
              const open = Boolean(anchorEl);

              React.useEffect(() => {
                const mentionElement = document.getElementById(mentionId);

                const handleMouseEnter = (event: MouseEvent) => {
                  setAnchorEl(event.currentTarget as HTMLElement);
                };

                const handleMouseLeave = () => {
                  setAnchorEl(null);
                };

                if (mentionElement) {
                  mentionElement.addEventListener(
                    "mouseenter",
                    handleMouseEnter
                  );
                  mentionElement.addEventListener(
                    "mouseleave",
                    handleMouseLeave
                  );
                }

                return () => {
                  if (mentionElement) {
                    mentionElement.removeEventListener(
                      "mouseenter",
                      handleMouseEnter
                    );
                    mentionElement.removeEventListener(
                      "mouseleave",
                      handleMouseLeave
                    );
                  }
                };
              }, []);

              return (
                <Popover
                  open={open}
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: "top",
                    horizontal: "center",
                  }}
                  transformOrigin={{
                    vertical: "bottom",
                    horizontal: "center",
                  }}
                  onClose={() => setAnchorEl(null)}
                  disableRestoreFocus
                  disablePortal={false}
                  disableAutoFocus
                  disableEnforceFocus
                  sx={{
                    pointerEvents: "none",
                  }}
                  slotProps={{
                    paper: {
                      elevation: 2,
                      sx: {
                        pointerEvents: "none",
                        outline: "none",
                        tabIndex: -1,
                      },
                    },
                  }}
                  container={document.body}
                >
                  <img
                    src={this.__imageUrl}
                    alt={this.__mention}
                    style={{
                      maxWidth: "300px",
                      maxHeight: "240px",
                      objectFit: "contain",
                      borderRadius: "4px",
                      padding: "4px",
                      paddingBottom: "0px",
                    }}
                    tabIndex={-1}
                  />
                </Popover>
              );
            };

            return <MentionPopover />;
          },
        })
      );

      // Use MUI's global PopoverService
      // This leverages the existing portal support in MUI
      if (typeof window !== "undefined") {
        // Add a data attribute to track this popover instance
        dom.dataset.hasPopover = "true";

        // Use a simple registry to track popover components
        if (!window.__mentionPopovers) {
          window.__mentionPopovers = new Map();
        }

        // Store the component reference
        window.__mentionPopovers.set(mentionId, {
          Component: PopoverComponent,
          remove: () => {
            // Cleanup function
            if (window.__mentionPopovers) {
              window.__mentionPopovers.delete(mentionId);
            }
          },
        });
      }

      // Clean up when the element is removed
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (
            mutation.type === "childList" &&
            Array.from(mutation.removedNodes).includes(wrapper)
          ) {
            // Clean up the popover reference
            if (window.__mentionPopovers) {
              const popover = window.__mentionPopovers.get(mentionId);
              if (popover && popover.remove) {
                popover.remove();
              }
            }
            observer.disconnect();
          }
        });
      });

      // Start observing the DOM for changes to clean up properly
      observer.observe(wrapper.parentNode || document.body, {
        childList: true,
      });

      return wrapper;
    }

    return wrapper; // Return wrapper even without image
  }

  exportDOM(): DOMExportOutput {
    const element = document.createElement("span");
    element.setAttribute("data-lexical-mention", "true");
    element.setAttribute("data-imageurl", this.__imageUrl);
    element.setAttribute("data-mention", this.__mention);
    element.setAttribute("data-imageid", this.__imageId.toString());
    if (this.__text !== this.__mention) {
      element.setAttribute("data-lexical-mention-name", this.__mention);
    }

    element.textContent = this.__text;
    return { element };
  }

  static importDOM(): DOMConversionMap | null {
    return {
      span: (domNode: HTMLElement) => {
        if (!domNode.hasAttribute("data-lexical-mention")) {
          return null;
        }
        return {
          conversion: $convertMentionElement,
          priority: 1,
        };
      },
    };
  }

  isTextEntity(): true {
    return true;
  }

  canInsertTextBefore(): boolean {
    return false;
  }

  canInsertTextAfter(): boolean {
    return false;
  }

  // Override the select method to always put the cursor at the end of the mention
  select(/* anchorOffset?: number, focusOffset?: number */): RangeSelection {
    // Check if there's a space after the mention node
    const parent = this.getParent();
    if (parent) {
      const siblings = parent.getChildren();
      const nodeIndex = siblings.indexOf(this);
      const nextNode =
        nodeIndex < siblings.length - 1 ? siblings[nodeIndex + 1] : null;

      if (
        nextNode &&
        nextNode instanceof TextNode &&
        nextNode.getTextContent().startsWith(" ")
      ) {
        // If there's a space after, put cursor after the space
        nextNode.select(1, 1);
        return $getSelection() as RangeSelection;
      }
    }

    // Otherwise put cursor right after the mention node
    const selection = $createRangeSelection();
    const textContentSize = this.getTextContentSize();
    selection.anchor.set(this.getKey(), textContentSize, "text");
    selection.focus.set(this.getKey(), textContentSize, "text");
    $setSelection(selection);
    return selection;
  }

  // Override the selectPrevious method to ensure proper selection behavior
  selectPrevious(anchorOffset?: number, focusOffset?: number): RangeSelection {
    // Check if there's a space before the mention node
    const parent = this.getParent();
    if (parent) {
      const siblings = parent.getChildren();
      const nodeIndex = siblings.indexOf(this);
      const prevNode = nodeIndex > 0 ? siblings[nodeIndex - 1] : null;

      if (
        prevNode &&
        prevNode instanceof TextNode &&
        prevNode.getTextContent().endsWith(" ")
      ) {
        // If there's a space before, put cursor before the space
        const prevContentSize = prevNode.getTextContentSize();
        prevNode.select(prevContentSize - 1, prevContentSize - 1);
        return $getSelection() as RangeSelection;
      }
    }

    // Place cursor at the start of the node or at the specified offset
    const selection = $createRangeSelection();
    const startOffset = anchorOffset !== undefined ? anchorOffset : 0;
    const endOffset = focusOffset !== undefined ? focusOffset : startOffset;
    selection.anchor.set(this.getKey(), startOffset, "text");
    selection.focus.set(this.getKey(), endOffset, "text");
    $setSelection(selection);
    return selection;
  }

  // Override the selectNext method to ensure proper selection behavior
  selectNext(anchorOffset?: number, focusOffset?: number): RangeSelection {
    // Check if there's a space after the mention node
    const parent = this.getParent();
    if (parent) {
      const siblings = parent.getChildren();
      const nodeIndex = siblings.indexOf(this);
      const nextNode =
        nodeIndex < siblings.length - 1 ? siblings[nodeIndex + 1] : null;

      if (
        nextNode &&
        nextNode instanceof TextNode &&
        nextNode.getTextContent().startsWith(" ")
      ) {
        // If there's a space after, put cursor after the space
        nextNode.select(1, 1);
        return $getSelection() as RangeSelection;
      }
    }

    // Place cursor at the end of the node or at the specified offset
    const selection = $createRangeSelection();
    const textContentSize = this.getTextContentSize();
    const startOffset =
      anchorOffset !== undefined ? anchorOffset : textContentSize;
    const endOffset = focusOffset !== undefined ? focusOffset : startOffset;
    selection.anchor.set(this.getKey(), startOffset, "text");
    selection.focus.set(this.getKey(), endOffset, "text");
    $setSelection(selection);
    return selection;
  }
}

export function $createMentionNode(
  mentionName: string,
  textContent?: string,
  imageUrl?: string,
  imageId?: number
): MentionNode {
  const mentionNode = new MentionNode(
    mentionName,
    textContent,
    imageUrl,
    imageId
  );
  mentionNode.setMode("segmented").toggleDirectionless();
  return $applyNodeReplacement(mentionNode);
}

export function $isMentionNode(
  node: LexicalNode | null | undefined
): node is MentionNode {
  return node instanceof MentionNode;
}
