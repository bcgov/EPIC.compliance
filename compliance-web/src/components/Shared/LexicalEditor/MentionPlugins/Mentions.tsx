/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import type { JSX } from "react";

import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import {
  LexicalTypeaheadMenuPlugin,
  MenuOption,
  MenuTextMatch,
  useBasicTypeaheadTriggerMatch,
} from "@lexical/react/LexicalTypeaheadMenuPlugin";
import {
  TextNode,
  COMMAND_PRIORITY_LOW,
  createCommand,
  LexicalCommand,
  NodeKey,
  $getNodeByKey,
  $createRangeSelection,
  $setSelection,
  SELECTION_CHANGE_COMMAND,
  $getSelection,
  $getRoot,
  LexicalNode,
  ElementNode,
} from "lexical";
import { useCallback, useEffect, useState } from "react";
import { $createMentionNode, MentionNode } from "./MentionNode";
import ReactDOM from "react-dom";
import { Box, Typography } from "@mui/material";
import { MentionData } from "../LexicalUtils";
import { RequirementImage } from "@/models/Image";

const PUNCTUATION =
  "\\.,\\+\\*\\?\\$\\@\\|#{}\\(\\)\\^\\-\\[\\]\\\\/!%'\"~=<>_:;";
const NAME = "\\b[A-Z][^\\s" + PUNCTUATION + "]";

const DocumentMentionsRegex = {
  NAME,
  PUNCTUATION,
};

const PUNC = DocumentMentionsRegex.PUNCTUATION;

const TRIGGERS = ["@"].join("");

// Chars we expect to see in a mention (non-space, non-punctuation).
const VALID_CHARS = "[^" + TRIGGERS + PUNC + "\\s]";

// Non-standard series of chars. Each series must be preceded and followed by
// a valid char.
const VALID_JOINS =
  "(?:" +
  "\\.[ |$]|" + // E.g. "r. " in "Mr. Smith"
  " |" + // E.g. " " in "Josh Duck"
  "[" +
  PUNC +
  "]|" + // E.g. "-' in "Salier-Hellendag"
  ")";

const LENGTH_LIMIT = 75;

const AtSignMentionsRegex = new RegExp(
  "(^|\\s|\\()(" +
    "[" +
    TRIGGERS +
    "]" +
    "((?:" +
    VALID_CHARS +
    VALID_JOINS +
    "){0," +
    LENGTH_LIMIT +
    "})" +
    ")$"
);

// 50 is the longest alias length limit.
const ALIAS_LENGTH_LIMIT = 50;

// Regex used to match alias.
const AtSignMentionsRegexAliasRegex = new RegExp(
  "(^|\\s|\\()(" +
    "[" +
    TRIGGERS +
    "]" +
    "((?:" +
    VALID_CHARS +
    "){0," +
    ALIAS_LENGTH_LIMIT +
    "})" +
    ")$"
);

// At most, 5 suggestions are shown in the popup.
const SUGGESTION_LIST_LENGTH_LIMIT = 5;

const mentionsCache = new Map();

const mentionLookupService = {
  search(
    string: string,
    callback: (results: Array<MentionData>) => void,
    mentionsList: MentionData[]
  ): void {
    setTimeout(() => {
      const results = mentionsList.filter((mention) =>
        mention.name.toLowerCase().includes(string.toLowerCase())
      );
      callback(results);
    }, 100);
  },
};

function useMentionLookupService(
  mentionString: string | null,
  mentionsList: MentionData[]
) {
  const [results, setResults] = useState<Array<MentionData>>([]);

  useEffect(() => {
    // Clear the cache when mentionsList changes to ensure we always use the latest data
    if (mentionsList.length > 0) {
      mentionsCache.clear();
    }

    const cachedResults = mentionsCache.get(mentionString);

    if (mentionString == null) {
      setResults([]);
      return;
    }

    if (cachedResults === null) {
      return;
    } else if (cachedResults !== undefined) {
      setResults(cachedResults);
      return;
    }

    mentionsCache.set(mentionString, null);
    mentionLookupService.search(
      mentionString,
      (newResults) => {
        mentionsCache.set(mentionString, newResults);
        setResults(newResults);
      },
      mentionsList
    );
  }, [mentionString, mentionsList]);

  return results;
}

function checkForAtSignMentions(
  text: string,
  minMatchLength: number
): MenuTextMatch | null {
  let match = AtSignMentionsRegex.exec(text);

  if (match === null) {
    match = AtSignMentionsRegexAliasRegex.exec(text);
  }
  if (match !== null) {
    // The strategy ignores leading whitespace but we need to know it's
    // length to add it to the leadOffset
    const maybeLeadingWhitespace = match[1];

    const matchingString = match[3];
    if (matchingString.length >= minMatchLength) {
      return {
        leadOffset: match.index + maybeLeadingWhitespace.length,
        matchingString,
        replaceableString: match[2],
      };
    }
  }
  return null;
}

function getPossibleQueryMatch(text: string): MenuTextMatch | null {
  return checkForAtSignMentions(text, 1);
}

class MentionTypeaheadOption extends MenuOption {
  mentionData: MentionData;
  picture: JSX.Element;

  constructor(mentionData: MentionData, picture: JSX.Element) {
    super(mentionData.name);
    this.mentionData = mentionData;
    this.picture = picture;
  }
}

function MentionsTypeaheadMenuItem({
  index,
  isSelected,
  onClick,
  onMouseEnter,
  option,
}: {
  index: number;
  isSelected: boolean;
  onClick: () => void;
  onMouseEnter: () => void;
  option: MentionTypeaheadOption;
}) {
  let className = "item";
  if (isSelected) {
    className += " selected";
  }
  return (
    <Box
      component="li"
      key={option.key}
      tabIndex={-1}
      className={className}
      ref={option.setRefElement}
      role="option"
      aria-selected={isSelected}
      id={"typeahead-item-" + index}
      onMouseEnter={onMouseEnter}
      onClick={onClick}
    >
      <Box sx={{ display: "flex", my: 1 }}>
        <Typography variant="subtitle2" mr={2}>
          {option.mentionData.name}
        </Typography>
        <Box
          component="img"
          src={option.mentionData.imageUrl ?? ""}
          alt={option.mentionData.name}
          sx={{ width: 100 }}
        />
      </Box>
    </Box>
  );
}

// Define commands for mention node interactions
const REMOVE_MENTION_COMMAND: LexicalCommand<{ key: NodeKey }> = createCommand(
  "REMOVE_MENTION_COMMAND"
);

const MOVE_SELECTION_AFTER_MENTION_COMMAND: LexicalCommand<{ key: NodeKey }> =
  createCommand("MOVE_SELECTION_AFTER_MENTION_COMMAND");

const NAVIGATE_FROM_MENTION_COMMAND: LexicalCommand<{
  key: NodeKey;
  direction: "left" | "right";
}> = createCommand("NAVIGATE_FROM_MENTION_COMMAND");

// Define a command for updating mentions when images are updated
const UPDATE_MENTIONS_COMMAND: LexicalCommand<{
  images: Array<RequirementImage>;
}> = createCommand("UPDATE_MENTIONS_COMMAND");

export default function MentionsPlugin({
  mentionsList,
}: {
  mentionsList: MentionData[];
}): JSX.Element | null {
  const [editor] = useLexicalComposerContext();

  const [queryString, setQueryString] = useState<string | null>(null);

  const results = useMentionLookupService(queryString, mentionsList);

  const checkForSlashTriggerMatch = useBasicTypeaheadTriggerMatch("/", {
    minLength: 0,
  });

  const options = results
    .map(
      (result) =>
        new MentionTypeaheadOption(result, <i className="icon user" />)
    )
    .slice(0, SUGGESTION_LIST_LENGTH_LIMIT);

  const onSelectOption = useCallback(
    (
      selectedOption: MentionTypeaheadOption,
      nodeToReplace: TextNode | null,
      closeMenu: () => void
    ) => {
      editor.update(() => {
        const mentionNode = $createMentionNode(
          selectedOption.mentionData.name,
          undefined,
          selectedOption.mentionData.imageUrl,
          selectedOption.mentionData.id
        );

        // Check if there's a node to replace (from @ typing)
        if (nodeToReplace) {
          nodeToReplace.replace(mentionNode);
        } else {
          const selection = $getSelection();
          if (selection) {
            selection.insertNodes([mentionNode]);
          }
        }
        const parent = mentionNode.getParent();
        if (parent) {
          const indexAfterMention = mentionNode.getIndexWithinParent() + 1;
          const selectionAfter = $createRangeSelection();
          selectionAfter.anchor.set(
            parent.getKey(),
            indexAfterMention,
            "element"
          );
          selectionAfter.focus.set(
            parent.getKey(),
            indexAfterMention,
            "element"
          );
          $setSelection(selectionAfter);
        }

        closeMenu();
      });
    },
    [editor]
  );

  const checkForMentionMatch = useCallback(
    (text: string) => {
      const slashMatch = checkForSlashTriggerMatch(text, editor);
      if (slashMatch !== null) {
        return null;
      }
      return getPossibleQueryMatch(text);
    },
    [checkForSlashTriggerMatch, editor]
  );

  // Register command listeners for mention node interactions
  useEffect(() => {
    // Command to remove a mention node
    const removeListener = editor.registerCommand(
      REMOVE_MENTION_COMMAND,
      (payload) => {
        editor.update(() => {
          const nodeKey = payload.key;
          const mentionNode = $getNodeByKey(nodeKey);

          if (mentionNode) {
            // Get parent and check surrounding nodes for spaces
            const parent = mentionNode.getParent();
            if (parent) {
              const siblings = parent.getChildren();
              const nodeIndex = siblings.indexOf(mentionNode);

              // Check for space nodes before and after
              const prevNode = nodeIndex > 0 ? siblings[nodeIndex - 1] : null;
              const nextNode =
                nodeIndex < siblings.length - 1
                  ? siblings[nodeIndex + 1]
                  : null;

              // Check if we have spaces on both sides
              const hasPrevSpace =
                prevNode instanceof TextNode &&
                prevNode.getTextContent() === " ";
              const hasNextSpace =
                nextNode instanceof TextNode &&
                nextNode.getTextContent() === " ";

              // Remove the mention node
              mentionNode.remove();

              // If there were spaces on both sides, remove one to avoid double spaces
              if (hasPrevSpace && hasNextSpace && prevNode && nextNode) {
                prevNode.remove();

                // Set selection after the remaining space
                nextNode.select(0, 0);
              } else if (hasPrevSpace && prevNode) {
                // Just set selection after the space before
                prevNode.select(
                  prevNode.getTextContentSize(),
                  prevNode.getTextContentSize()
                );
              } else if (hasNextSpace && nextNode) {
                // Set selection before the space after
                nextNode.select(0, 0);
              }
            } else {
              // Fallback - just remove the node
              mentionNode.remove();
            }
          }
        });
        return true;
      },
      COMMAND_PRIORITY_LOW
    );

    // Command to move selection after a mention node
    const moveSelectionListener = editor.registerCommand(
      MOVE_SELECTION_AFTER_MENTION_COMMAND,
      (payload) => {
        editor.update(() => {
          const nodeKey = payload.key;
          const mentionNode = $getNodeByKey(nodeKey);

          if (mentionNode) {
            // Check if there's a space after the mention node
            const parent = mentionNode.getParent();
            if (parent) {
              const siblings = parent.getChildren();
              const nodeIndex = siblings.indexOf(mentionNode);
              const nextNode =
                nodeIndex < siblings.length - 1
                  ? siblings[nodeIndex + 1]
                  : null;

              if (
                nextNode &&
                nextNode instanceof TextNode &&
                nextNode.getTextContent().startsWith(" ")
              ) {
                // If there's a space after, put cursor after the space
                nextNode.select(1, 1);
              } else {
                // If no space after, put cursor right after the mention
                const selection = $createRangeSelection();
                selection.anchor.set(
                  mentionNode.getKey(),
                  mentionNode.getTextContentSize(),
                  "text"
                );
                selection.focus.set(
                  mentionNode.getKey(),
                  mentionNode.getTextContentSize(),
                  "text"
                );
                $setSelection(selection);
              }
            } else {
              // Fallback to putting cursor right after the mention
              const selection = $createRangeSelection();
              selection.anchor.set(
                mentionNode.getKey(),
                mentionNode.getTextContentSize(),
                "text"
              );
              selection.focus.set(
                mentionNode.getKey(),
                mentionNode.getTextContentSize(),
                "text"
              );
              $setSelection(selection);
            }
          }
        });
        return true;
      },
      COMMAND_PRIORITY_LOW
    );

    // Command to navigate from a mention node using arrow keys
    const navigateListener = editor.registerCommand(
      NAVIGATE_FROM_MENTION_COMMAND,
      (payload) => {
        const { key, direction } = payload;

        editor.update(() => {
          const mentionNode = $getNodeByKey(key);
          if (!mentionNode) return;

          const parent = mentionNode.getParent();
          if (parent) {
            const siblings = parent.getChildren();
            const nodeIndex = siblings.indexOf(mentionNode);

            if (direction === "left") {
              // Check for space before the mention
              const prevNode = nodeIndex > 0 ? siblings[nodeIndex - 1] : null;

              if (
                prevNode &&
                prevNode instanceof TextNode &&
                prevNode.getTextContent().endsWith(" ")
              ) {
                // If there's a space before, put cursor before the space
                prevNode.select(
                  prevNode.getTextContentSize() - 1,
                  prevNode.getTextContentSize() - 1
                );
              } else {
                // Otherwise position cursor before the mention node
                const selection = $createRangeSelection();
                selection.anchor.set(mentionNode.getKey(), 0, "text");
                selection.focus.set(mentionNode.getKey(), 0, "text");
                $setSelection(selection);
              }
            } else if (direction === "right") {
              // Check for space after the mention
              const nextNode =
                nodeIndex < siblings.length - 1
                  ? siblings[nodeIndex + 1]
                  : null;

              if (
                nextNode &&
                nextNode instanceof TextNode &&
                nextNode.getTextContent().startsWith(" ")
              ) {
                // If there's a space after, put cursor after the space
                nextNode.select(1, 1);
              } else {
                // Otherwise position cursor after the mention node
                const selection = $createRangeSelection();
                const textContentSize = mentionNode.getTextContentSize();
                selection.anchor.set(
                  mentionNode.getKey(),
                  textContentSize,
                  "text"
                );
                selection.focus.set(
                  mentionNode.getKey(),
                  textContentSize,
                  "text"
                );
                $setSelection(selection);
              }
            }
          } else {
            // Fallback to default behavior
            const selection = $createRangeSelection();

            if (direction === "left") {
              selection.anchor.set(mentionNode.getKey(), 0, "text");
              selection.focus.set(mentionNode.getKey(), 0, "text");
            } else {
              selection.anchor.set(
                mentionNode.getKey(),
                mentionNode.getTextContentSize(),
                "text"
              );
              selection.focus.set(
                mentionNode.getKey(),
                mentionNode.getTextContentSize(),
                "text"
              );
            }

            $setSelection(selection);
          }
        });

        // Dispatch selection change to update UI
        setTimeout(() => {
          editor.dispatchCommand(SELECTION_CHANGE_COMMAND, undefined);
        }, 0);

        return true;
      },
      COMMAND_PRIORITY_LOW
    );

    // Command to update mentions when images are updated
    const updateMentionsListener = editor.registerCommand(
      UPDATE_MENTIONS_COMMAND,
      (payload) => {
        const { images } = payload;

        editor.update(() => {
          // Get the root node of the editor
          const root = $getRoot();

          // Function to update a mention node if it matches
          function updateMentionIfNeeded(node: LexicalNode) {
            if (node instanceof MentionNode) {
              const imageId = node.__imageId;

              // Find the corresponding image in the updated images list
              const updatedImage = images.find((img) => img.id === imageId);

              if (updatedImage) {
                // Update the mention node with new values
                const newName = `${updatedImage.image_type} ${updatedImage.sort_order}`;

                // Instead of directly modifying properties, create a new node and replace the old one
                const newMentionNode = $createMentionNode(
                  newName,
                  newName,
                  updatedImage.url || "",
                  updatedImage.id
                );

                // Replace the old node with the new one
                node.replace(newMentionNode);
              } else {
                // If no matching image is found, delete the mention node
                // First, check if the node has a parent
                const parent = node.getParent();

                if (parent) {
                  // Check if there are spaces around the mention node that should be handled
                  const siblings = parent.getChildren();
                  const nodeIndex = siblings.indexOf(node);

                  // Check for space nodes before and after
                  const prevNode =
                    nodeIndex > 0 ? siblings[nodeIndex - 1] : null;
                  const nextNode =
                    nodeIndex < siblings.length - 1
                      ? siblings[nodeIndex + 1]
                      : null;

                  // Check if we have spaces on both sides
                  const hasPrevSpace =
                    prevNode instanceof TextNode &&
                    prevNode.getTextContent() === " ";
                  const hasNextSpace =
                    nextNode instanceof TextNode &&
                    nextNode.getTextContent() === " ";

                  // Remove the mention node
                  node.remove();

                  // If there were spaces on both sides, remove one to avoid double spaces
                  if (hasPrevSpace && hasNextSpace && prevNode) {
                    prevNode.remove();
                  }
                } else {
                  // Just remove the node if it has no parent
                  node.remove();
                }
              }
            }
          }

          // Traverse all nodes in the editor recursively using a safer approach
          const nodes: LexicalNode[] = [];
          root.getChildren().forEach((child) => nodes.push(child));

          while (nodes.length > 0) {
            const node = nodes.shift();
            if (!node) continue;

            // Process the current node
            updateMentionIfNeeded(node);

            // Add children if this is an element node
            if (node instanceof ElementNode) {
              node.getChildren().forEach((child) => nodes.push(child));
            }
          }
        }, { discrete: true });

        return true;
      },
      COMMAND_PRIORITY_LOW
    );

    // Register a listener for the custom DOM events
    const handleCustomEvent = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail?.type === "remove-mention") {
        editor.dispatchCommand(REMOVE_MENTION_COMMAND, {
          key: customEvent.detail.key,
        });
      } else if (customEvent.detail?.type === "move-selection-after-mention") {
        editor.dispatchCommand(MOVE_SELECTION_AFTER_MENTION_COMMAND, {
          key: customEvent.detail.key,
        });
      } else if (customEvent.detail?.type === "navigate-from-mention") {
        editor.dispatchCommand(NAVIGATE_FROM_MENTION_COMMAND, {
          key: customEvent.detail.key,
          direction: customEvent.detail.direction,
        });
      } else if (customEvent.detail?.type === "update-mentions") {
        editor.dispatchCommand(UPDATE_MENTIONS_COMMAND, {
          images: customEvent.detail.images,
        });
      }
    };

    // Get the editor element to attach the event listener
    const editorElement = editor.getRootElement();
    if (editorElement) {
      editorElement.addEventListener("lexical-command", handleCustomEvent);
    }

    // Clean up when the component unmounts
    return () => {
      if (editorElement) {
        editorElement.removeEventListener("lexical-command", handleCustomEvent);
      }
      removeListener();
      moveSelectionListener();
      navigateListener();
      updateMentionsListener(); // Clean up the new listener
    };
  }, [editor]);

  return (
    <LexicalTypeaheadMenuPlugin<MentionTypeaheadOption>
      onQueryChange={setQueryString}
      onSelectOption={onSelectOption}
      triggerFn={checkForMentionMatch}
      options={options}
      menuRenderFn={(
        anchorElementRef,
        { selectedIndex, selectOptionAndCleanUp, setHighlightedIndex }
      ) =>
        anchorElementRef.current && results.length
          ? ReactDOM.createPortal(
              <Box className="typeahead-popover mentions-menu">
                <Box component="ul">
                  {options.map((option, i: number) => (
                    <MentionsTypeaheadMenuItem
                      index={i}
                      isSelected={selectedIndex === i}
                      onClick={() => {
                        setHighlightedIndex(i);
                        selectOptionAndCleanUp(option);
                      }}
                      onMouseEnter={() => {
                        setHighlightedIndex(i);
                      }}
                      key={option.key}
                      option={option}
                    />
                  ))}
                </Box>
              </Box>,
              anchorElementRef.current
            )
          : null
      }
    />
  );
}
