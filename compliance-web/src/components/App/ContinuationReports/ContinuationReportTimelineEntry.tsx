import ParagraphWithReadMore from "@/components/Shared/ParagraphWithReadMore";
import { CRKeys } from "@/models/ContinuationReport";
import { CR_CONTEXT_LINK, CR_CONTEXT_TYPE } from "@/utils/constants";
import { sanitizeHtml } from "@/utils/sanitizeHtml";
import TimelineContent from "@mui/lab/TimelineContent";
import { Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";

export default function ContinuationReportTimelineEntry({
  renderText,
  keys,
  createdByUser,
  isSystemGenerated,
  searchText,
}: {
  renderText: string;
  keys: CRKeys[];
  createdByUser?: string;
  isSystemGenerated: boolean;
  searchText?: string;
}) {
  const applyNavigationLinks = () => {
    if (keys && keys.length > 0) {
      keys.forEach((key) => {
        if (key.key_context !== CR_CONTEXT_TYPE.CASEFILE) {
          const regEx = new RegExp(key.key, "gi");
          renderText = renderText.replace(
            regEx,
            `<a href="${CR_CONTEXT_LINK[key.key_context]}/${key.key}">${key.key}</a>`
          );
        }
      });
    }
    return renderText;
  };
  const getFormattedText = () => {
    renderText = applyNavigationLinks();
    if (!searchText) return sanitizeHtml(renderText);

    // Create a temporary DOM element to parse the HTML
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = sanitizeHtml(renderText);

    // Function to highlight text in a text node
    const highlightTextNode = (node: Text) => {
      const regex = new RegExp(`(${searchText})`, "gi");
      const matches = node.textContent?.match(regex);
      if (!matches) return;

      const fragment = document.createDocumentFragment();
      let lastIndex = 0;
      let match;

      regex.lastIndex = 0; // Reset regex state
      while ((match = regex.exec(node.textContent || "")) !== null) {
        // Add text before match
        fragment.appendChild(
          document.createTextNode(
            node.textContent?.substring(lastIndex, match.index) || ""
          )
        );

        // Add highlighted match
        const highlight = document.createElement("span");
        highlight.style.backgroundColor = "yellow";
        highlight.textContent = match[0];
        fragment.appendChild(highlight);

        lastIndex = regex.lastIndex;
      }

      // Add remaining text
      fragment.appendChild(
        document.createTextNode(node.textContent?.substring(lastIndex) || "")
      );
      node.parentNode?.replaceChild(fragment, node);
    };

    // Recursive function to traverse DOM
    const traverse = (node: Node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        highlightTextNode(node as Text);
      } else {
        node.childNodes.forEach(traverse);
      }
    };

    traverse(tempDiv);
    return sanitizeHtml(tempDiv.innerHTML);
  };

  return (
    <TimelineContent sx={{ p: "4px 0px 8px 8px" }}>
      <ParagraphWithReadMore
        maxHeight={150}
        expand={!!searchText}
        isFormatted={true}
        renderTypography={
          <>
            <Typography
              variant="subtitle2"
              component={"div"}
              sx={{
                "& p": {
                  my: 0,
                },
              }}
              dangerouslySetInnerHTML={{ __html: getFormattedText() }}
            />
            {!isSystemGenerated && createdByUser && (
              <Typography
                variant="subtitle2"
                color={BCDesignTokens.typographyColorDisabled}
              >
                Created by {createdByUser}
              </Typography>
            )}
          </>
        }
      />
    </TimelineContent>
  );
}
