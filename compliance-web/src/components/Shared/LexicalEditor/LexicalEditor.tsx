import { LexicalComposer } from "@lexical/react/LexicalComposer";
import { ContentEditable } from "@lexical/react/LexicalContentEditable";
import { RichTextPlugin } from "@lexical/react/LexicalRichTextPlugin";
import { OnChangePlugin } from "@lexical/react/LexicalOnChangePlugin";
import { HistoryPlugin } from "@lexical/react/LexicalHistoryPlugin";
import { LexicalErrorBoundary } from "@lexical/react/LexicalErrorBoundary";
import { ListPlugin } from "@lexical/react/LexicalListPlugin";
import { Box, Grid, InputLabel, Tooltip } from "@mui/material";
import LexicalToolbar from "./LexicalToolbar";
import { EditorState, LexicalEditor as Editor } from "lexical";
import { $getRoot, $createParagraphNode, $createTextNode } from "lexical";
import { $generateNodesFromDOM } from "@lexical/html";
import { BCDesignTokens } from "epic.theme";
import { ListNode, ListItemNode } from "@lexical/list";
import { TabIndentationPlugin } from "@lexical/react/LexicalTabIndentationPlugin";
import { TablePlugin } from "@lexical/react/LexicalTablePlugin";
import { TableCellNode, TableNode, TableRowNode } from "@lexical/table";
import { useState, useMemo } from "react";
import TableCellResizerPlugin from "./TablePlugins/TableCellResizer";
import TableCellActionMenuPlugin from "./TablePlugins/TableActionMenu";
import TableHoverActionsPlugin from "./TablePlugins/TableHoverActions";
import { MentionNode } from "./MentionPlugins/MentionNode";
import MentionsPlugin from "./MentionPlugins/Mentions";
import { LexicalTheme, MentionData } from "./LexicalUtils";
import { PopoverManager } from "./MentionPlugins/PopoverManager";

export type TextEditorValue = {
  html: string;
  text: string;
};

type LexicalEditorProps = {
  errorMsg?: string;
  placeholder: string;
  defaultHtml?: string;
  label?: string;
  name?: string;
  height?: string;
  isAdvanced?: boolean;
  mentionsList?: MentionData[];
  onChange: (editorState: EditorState, editor: Editor) => void;
  isRequired?: boolean;
  disabled?: boolean;
};

const LexicalEditor = ({
  errorMsg,
  placeholder,
  defaultHtml = "",
  label = "",
  name,
  height,
  mentionsList,
  onChange,
  isAdvanced = false,
  isRequired = false,
  disabled = false,
}: LexicalEditorProps) => {
  // Lexical Editor Configuration
  const editorConfig = {
    namespace: "EAOComplianceEditor",
    theme: LexicalTheme,
    nodes: [
      ListNode,
      ListItemNode,
      TableNode,
      TableRowNode,
      TableCellNode,
      MentionNode,
    ],
    onError(error: unknown) {
      // eslint-disable-next-line no-console
      console.error(error);
    },
    editorState: (editor: Editor) => {
      const parser = new DOMParser();
      editor.update(() => {
        // Clear the editor content first
        $getRoot().clear();

        if (defaultHtml) {
          // Parse the HTML string into DOM
          const dom = parser.parseFromString(defaultHtml, "text/html");
          // Convert DOM nodes to Lexical nodes
          const nodes = $generateNodesFromDOM(editor, dom);
          // Insert the nodes
          $getRoot().append(...nodes);
        } else {
          // If no default HTML, create an empty paragraph
          const paragraph = $createParagraphNode();
          paragraph.append($createTextNode(""));
          $getRoot().append(paragraph);
        }
      });
    },
    editable: !disabled,
  };

  const [floatingAnchorElem, setFloatingAnchorElem] =
    useState<HTMLDivElement | null>(null);

  const onRef = (_floatingAnchorElem: HTMLDivElement) => {
    if (_floatingAnchorElem !== null) {
      setFloatingAnchorElem(_floatingAnchorElem);
    }
  };

  // Memoize the mentionsList to prevent unnecessary re-renders
  // but ensure it updates when the mentionsList changes
  const memoizedMentionsList = useMemo(
    () => mentionsList || [],
    [mentionsList]
  );

  return (
    <LexicalComposer initialConfig={editorConfig}>
      <Grid container>
        <Grid item xs={2}>
          <Tooltip title={label} arrow>
            <span>
              <InputLabel
                sx={{
                  position: "static",
                  transform: "none",
                  fontSize: "0.875rem",
                  lineHeight: "1.5rem",
                  color: errorMsg
                    ? BCDesignTokens.typographyColorDanger
                    : BCDesignTokens.typographyColorPrimary,
                  fontWeight: isRequired ? "bold" : "normal",
                }}
                htmlFor={name}
                size="small"
              >
                {label}
              </InputLabel>
            </span>
          </Tooltip>
        </Grid>
        <Grid item xs={10} sx={{ textAlign: "right" }}>
          {!disabled && <LexicalToolbar isAdvanced={isAdvanced} />}
        </Grid>
      </Grid>
      <Box
        className="editor-container"
        sx={{
          border: errorMsg
            ? `1px solid ${BCDesignTokens.supportBorderColorDanger}`
            : `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
          height: height ? height : "auto",
          overflowY: "auto",
          backgroundColor: disabled
            ? BCDesignTokens.surfaceColorFormsDisabled
            : BCDesignTokens.surfaceColorFormsDefault,
        }}
      >
        <Box className="editor-inner editor-content">
          <RichTextPlugin
            contentEditable={
              <div ref={onRef}>
                <ContentEditable
                  className="editor-input"
                  aria-placeholder={placeholder}
                  placeholder={
                    <div className="editor-placeholder">{placeholder}</div>
                  }
                  disabled={disabled}
                />
              </div>
            }
            ErrorBoundary={LexicalErrorBoundary}
          />
          <OnChangePlugin onChange={onChange} />
          <ListPlugin />
          <TabIndentationPlugin maxIndent={7} />
          <TablePlugin
            hasCellMerge
            hasCellBackgroundColor
            hasHorizontalScroll
          />
          <TableCellResizerPlugin />
          {floatingAnchorElem && (
            <>
              <TableCellActionMenuPlugin
                anchorElem={floatingAnchorElem}
                cellMerge={true}
              />
              <TableHoverActionsPlugin anchorElem={floatingAnchorElem} />
            </>
          )}
          {memoizedMentionsList.length > 0 && (
            <MentionsPlugin
              mentionsList={memoizedMentionsList}
              key={`mentions-plugin-${memoizedMentionsList.length}`}
            />
          )}
          <HistoryPlugin />
        </Box>
      </Box>
      <PopoverManager />
    </LexicalComposer>
  );
};

export default LexicalEditor;
