import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import { mergeRegister } from "@lexical/utils";
import {
  BorderColorRounded,
  FormatBoldRounded,
  FormatItalicRounded,
  FormatStrikethroughRounded,
  FormatUnderlinedRounded,
  RedoRounded,
  UndoRounded,
  FormatIndentDecreaseRounded,
  FormatIndentIncreaseRounded,
  FormatListBulletedRounded,
  FormatListNumberedRounded,
  TableChartOutlined,
} from "@mui/icons-material";
import {
  $getSelection,
  $isRangeSelection,
  CAN_REDO_COMMAND,
  CAN_UNDO_COMMAND,
  FORMAT_ELEMENT_COMMAND,
  FORMAT_TEXT_COMMAND,
  REDO_COMMAND,
  SELECTION_CHANGE_COMMAND,
  UNDO_COMMAND,
  INDENT_CONTENT_COMMAND,
  OUTDENT_CONTENT_COMMAND,
  ElementFormatType,
} from "lexical";
import {
  INSERT_ORDERED_LIST_COMMAND,
  INSERT_UNORDERED_LIST_COMMAND,
} from "@lexical/list";
import { INSERT_TABLE_COMMAND } from "@lexical/table";
import { useCallback, useEffect, useRef, useState } from "react";
import { Box, IconButton, Tooltip } from "@mui/material";
import LexicalToolbarAlign from "./LexicalToolbarAlign";

const LowPriority = 1;

function Divider() {
  return <div className="divider" />;
}

interface ToolbarIconButtonProps {
  disabled?: boolean;
  onClick: () => void;
  isActive?: boolean;
  ariaLabel: string;
  icon: React.ComponentType;
}

function ToolbarIconButton({
  disabled = false,
  onClick,
  isActive = false,
  ariaLabel,
  icon: Icon,
}: ToolbarIconButtonProps) {
  return (
    <Tooltip title={ariaLabel}>
      <span>
        <IconButton
          disabled={disabled}
          onClick={onClick}
          className={`toolbar-item ${isActive ? "active" : ""}`}
          aria-label={ariaLabel}
        >
          <Icon />
        </IconButton>
      </span>
    </Tooltip>
  );
}

export default function ToolbarPlugin({ isAdvanced }: { isAdvanced: boolean }) {
  const [editor] = useLexicalComposerContext();
  const toolbarRef = useRef(null);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [isUnderline, setIsUnderline] = useState(false);
  const [isStrikethrough, setIsStrikethrough] = useState(false);
  const [isHighlight, setIsHighlight] = useState(false);

  const $updateToolbar = useCallback(() => {
    const selection = $getSelection();
    if ($isRangeSelection(selection)) {
      // Update text format
      setIsBold(selection.hasFormat("bold"));
      setIsItalic(selection.hasFormat("italic"));
      setIsUnderline(selection.hasFormat("underline"));
      setIsStrikethrough(selection.hasFormat("strikethrough"));
      setIsHighlight(selection.hasFormat("highlight"));
    }
  }, []);

  useEffect(() => {
    return mergeRegister(
      editor.registerUpdateListener(({ editorState }) => {
        editorState.read(() => {
          $updateToolbar();
        });
      }),
      editor.registerCommand(
        SELECTION_CHANGE_COMMAND,
        () => {
          $updateToolbar();
          return false;
        },
        LowPriority
      ),
      editor.registerCommand(
        CAN_UNDO_COMMAND,
        (payload) => {
          setCanUndo(payload);
          return false;
        },
        LowPriority
      ),
      editor.registerCommand(
        CAN_REDO_COMMAND,
        (payload) => {
          setCanRedo(payload);
          return false;
        },
        LowPriority
      )
    );
  }, [editor, $updateToolbar]);

  const handleAlignmentChange = (newAlignment: ElementFormatType) => {
    editor.dispatchCommand(FORMAT_ELEMENT_COMMAND, newAlignment);
  };

  return (
    <Box className="toolbar" ref={toolbarRef}>
      <ToolbarIconButton
        disabled={!canUndo}
        onClick={() => editor.dispatchCommand(UNDO_COMMAND, undefined)}
        ariaLabel="Undo"
        icon={UndoRounded}
      />
      <ToolbarIconButton
        disabled={!canRedo}
        onClick={() => editor.dispatchCommand(REDO_COMMAND, undefined)}
        ariaLabel="Redo"
        icon={RedoRounded}
      />
      <Divider />
      <ToolbarIconButton
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, "bold")}
        isActive={isBold}
        ariaLabel="Bold"
        icon={FormatBoldRounded}
      />
      <ToolbarIconButton
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, "italic")}
        isActive={isItalic}
        ariaLabel="Italic"
        icon={FormatItalicRounded}
      />
      <ToolbarIconButton
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, "underline")}
        isActive={isUnderline}
        ariaLabel="Underline"
        icon={FormatUnderlinedRounded}
      />
      <ToolbarIconButton
        onClick={() =>
          editor.dispatchCommand(FORMAT_TEXT_COMMAND, "strikethrough")
        }
        isActive={isStrikethrough}
        ariaLabel="Strikethrough"
        icon={FormatStrikethroughRounded}
      />
      <ToolbarIconButton
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, "highlight")}
        isActive={isHighlight}
        ariaLabel="Highlight"
        icon={BorderColorRounded}
      />
      <Divider />
      <ToolbarIconButton
        onClick={() =>
          editor.dispatchCommand(OUTDENT_CONTENT_COMMAND, undefined)
        }
        ariaLabel="Decrease Indent"
        icon={FormatIndentDecreaseRounded}
      />
      <ToolbarIconButton
        onClick={() =>
          editor.dispatchCommand(INDENT_CONTENT_COMMAND, undefined)
        }
        ariaLabel="Increase Indent"
        icon={FormatIndentIncreaseRounded}
      />
      <Divider />
      <ToolbarIconButton
        onClick={() =>
          editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined)
        }
        ariaLabel="Bulleted List"
        icon={FormatListBulletedRounded}
      />
      <ToolbarIconButton
        onClick={() =>
          editor.dispatchCommand(INSERT_ORDERED_LIST_COMMAND, undefined)
        }
        ariaLabel="Numbered List"
        icon={FormatListNumberedRounded}
      />
      {isAdvanced && (
        <>
          <Divider />
          <LexicalToolbarAlign onAlignmentChange={handleAlignmentChange} />
          <ToolbarIconButton
            onClick={() =>
              editor.dispatchCommand(INSERT_TABLE_COMMAND, {
                rows: "3",
                columns: "3",
              })
            }
            ariaLabel="Table"
            icon={TableChartOutlined}
          />
        </>
      )}
    </Box>
  );
}
