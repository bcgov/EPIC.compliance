import { FC, useState } from "react";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Button,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  DeleteOutlineRounded,
  EditOutlined,
  ExpandMoreRounded,
} from "@mui/icons-material";
import { AddRounded } from "@mui/icons-material";
import { BCDesignTokens } from "epic.theme";
import { ExpandLessRounded } from "@mui/icons-material";
import {
  RequirementRelatedDocumentData,
  RequirementRelatedDocumentSectionData,
} from "@/models/InspectionRequirementSource";
import ParagraphWithReadMore from "@/components/Shared/ParagraphWithReadMore";
import { generateHtmlWithEmbeddedImages } from "../RequirementUtils";
import { RequirementImage } from "@/models/Image";

interface RequirementRelatedDocumentCardProps {
  relatedDocument: RequirementRelatedDocumentData;
  index: number;
  onAddRelatedDocumentSection: () => void;
  onDeleteRelatedDocumentSection: (
    data: RequirementRelatedDocumentSectionData
  ) => void;
  onEditRelatedDocumentSection: (
    data: RequirementRelatedDocumentSectionData
  ) => void;
  relatedDocumentImages?: RequirementImage[];
  isRequirementEditable?: boolean;
}

const RequirementRelatedDocumentCard: FC<
  RequirementRelatedDocumentCardProps
> = ({
  index,
  relatedDocument,
  onAddRelatedDocumentSection,
  onDeleteRelatedDocumentSection,
  onEditRelatedDocumentSection,
  relatedDocumentImages,
  isRequirementEditable = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <Accordion
      key={index}
      expanded={isExpanded}
      onChange={(_, expanded) => {
        setIsExpanded(expanded);
      }}
      sx={{
        border: 0,
        borderRadius: "0 !important",
        backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
        borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        "&.Mui-expanded": {
          margin: "0",
        },
      }}
    >
      <AccordionSummary
        aria-controls={`panel${index}-content`}
        id={`requirement-related-document-panel${index}-header`}
        sx={{
          "&.Mui-expanded": {
            minHeight: "48px",
            padding: "0.875rem 1rem",
            borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
            backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
            "& .MuiAccordionSummary-content": {
              margin: "0",
            },
          },
          "& .MuiAccordionSummary-content": {
            display: "flex",
            justifyContent: "space-between",
            gap: "1rem",
          },
        }}
      >
        <Box display={"flex"} alignItems={"flex-start"} gap={0.5}>
          {isExpanded ? <ExpandLessRounded /> : <ExpandMoreRounded />}
          <Typography variant="body2">
            <strong>{relatedDocument.documentTitle}</strong>
            {relatedDocument.appendix &&
              ` (Appendix ${relatedDocument.appendix.appendix_no})`}
          </Typography>
        </Box>
        {isExpanded && isRequirementEditable && (
          <Button
            variant="text"
            color="secondary"
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onAddRelatedDocumentSection();
            }}
            startIcon={<AddRounded />}
            sx={{
              backgroundColor: "transparent",
              paddingY: 0,
              height: "auto",
              "& .MuiButton-startIcon": {
                mr: 0,
              },
            }}
            data-testid={`requirement-related-document-add-section-${index}`}
          >
            Section
          </Button>
        )}
      </AccordionSummary>
      <AccordionDetails sx={{ padding: "0" }}>
        {relatedDocument.sections?.map((section, idx) => (
          <Box
            key={idx}
            sx={{
              padding: "1rem",
              borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
            }}
          >
            {isRequirementEditable && (
              <Box
                display={"flex"}
                justifyContent={"flex-start"}
                gap={".25rem"}
              >
                <Tooltip title="Edit" arrow>
                  <IconButton
                    size="small"
                    color="secondary"
                    onClick={() => onEditRelatedDocumentSection(section)}
                    data-testid={`requirement-related-document-edit-${index}-${idx}`}
                  >
                    <EditOutlined />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete" arrow>
                  <IconButton
                    size="small"
                    color="secondary"
                    onClick={() => onDeleteRelatedDocumentSection(section)}
                    data-testid={`requirement-related-document-delete-${index}-${idx}`}
                  >
                    <DeleteOutlineRounded />
                  </IconButton>
                </Tooltip>
              </Box>
            )}
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                gap: "1rem",
                marginBottom: ".5rem",
              }}
            >
              <Box>
                <Typography
                  variant="subtitle2"
                  color={BCDesignTokens.typographyColorPlaceholder}
                >
                  Section #:
                </Typography>
                <Typography variant="body2" fontWeight={700}>
                  {section.sectionNumber}
                </Typography>
              </Box>
              <Box>
                <Typography
                  variant="subtitle2"
                  color={BCDesignTokens.typographyColorPlaceholder}
                >
                  Section Title:
                </Typography>
                <Typography variant="body2">{section.sectionTitle}</Typography>
              </Box>
            </Box>
            <Box>
              <Typography
                variant="subtitle2"
                color={BCDesignTokens.typographyColorPlaceholder}
              >
                Description:
              </Typography>
              <ParagraphWithReadMore
                key={`req-related-doc-card-desc-${section.id}`}
                maxHeight={84}
                isFormatted={true}
                renderTypography={
                  <Box
                    dangerouslySetInnerHTML={{
                      __html: generateHtmlWithEmbeddedImages(
                        section.description?.html ?? "",
                        relatedDocumentImages?.filter(
                          (image) => image.req_detail_doc_id === section.id
                        ) ?? []
                      ),
                    }}
                  />
                }
              />
            </Box>
          </Box>
        ))}
      </AccordionDetails>
    </Accordion>
  );
};

export default RequirementRelatedDocumentCard;
