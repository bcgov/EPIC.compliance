// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { $generateHtmlFromNodes, $generateNodesFromDOM } from "@lexical/html";
import { ListItemNode, ListNode } from "@lexical/list";
import { TableCellNode, TableNode, TableRowNode } from "@lexical/table";
import { $getRoot, createEditor } from "lexical";
import { LexicalHtmlConfig, LexicalTheme } from "./LexicalUtils";

/**
 * Loads saved HTML into an editor configured like the shared one, then exports
 * it again — the round trip a user makes by saving content and reopening it.
 */
const reopen = (html: string) => {
  const editor = createEditor({
    namespace: "EAOComplianceEditor",
    theme: LexicalTheme,
    html: LexicalHtmlConfig,
    nodes: [ListNode, ListItemNode, TableNode, TableRowNode, TableCellNode],
    onError: (error) => {
      throw error;
    },
  });

  editor.update(
    () => {
      const dom = new DOMParser().parseFromString(html, "text/html");
      $getRoot().clear();
      $getRoot().append(...$generateNodesFromDOM(editor, dom));
    },
    { discrete: true }
  );

  let exported = "";
  editor.getEditorState().read(() => {
    exported = $generateHtmlFromNodes(editor);
  });
  return exported;
};

describe("highlight round trip", () => {
  it("keeps highlighting when saved content is reopened", () => {
    const exported = reopen("<p><mark>Highlighted</mark></p>");
    expect(exported).toContain("<mark");
    expect(exported).toContain("Highlighted");
  });

  it("keeps highlighting combined with bold", () => {
    const exported = reopen("<p><mark><strong>Bold and highlighted</strong></mark></p>");
    expect(exported).toContain("<mark");
    expect(exported).toContain("<strong");
  });

  it("keeps highlighting inside list items", () => {
    const exported = reopen("<ul><li><mark>Highlighted item</mark></li></ul>");
    expect(exported).toContain("<mark");
  });

  it("leaves unhighlighted text alone", () => {
    const exported = reopen("<p>Plain text</p>");
    expect(exported).not.toContain("<mark");
  });
});
