import { FC, memo, useState } from "react";
import {
  Box,
  Typography,
  Button,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Grid,
} from "@mui/material";
import {
  AddRounded,
  DeleteOutlineRounded,
  EditOutlined,
  ExpandLessRounded,
  ExpandMoreRounded,
} from "@mui/icons-material";
import {
  RequirementRelatedDocumentData,
  RequirementRelatedDocumentSectionData,
  RequirementSourceFormData,
} from "@/models/InspectionRequirementSource";
import { BCDesignTokens } from "epic.theme";
import ParagraphWithReadMore from "@/components/Shared/ParagraphWithReadMore";
import { RequirementSourceEnum } from "@/utils/constants";
import RequirementRelatedDocumentCard from "./RequirementRelatedDocumentCard";
import {
  requirementSourceNumberType,
  generateHtmlWithEmbeddedImages,
} from "../RequirementUtils";
import { RequirementImage } from "@/models/Image";
import { sanitizeHtml } from "@/utils/sanitizeHtml";

type RequirementSourceCardProps = {
  data: RequirementSourceFormData[];
  index: number;
  onEdit: (data: RequirementSourceFormData, index: number) => void;
  onDelete: (data: RequirementSourceFormData) => void;
  onAddSection: (data: RequirementSourceFormData) => void;
  onAddRelatedDocument: (data: RequirementSourceFormData) => void;
  onAddRelatedDocumentSection: (
    docData: RequirementRelatedDocumentData,
    srcData: RequirementSourceFormData
  ) => void;
  onEditRelatedDocumentSection: (
    data: RequirementRelatedDocumentSectionData,
    sectionIndex: number
  ) => void;
  onDeleteRelatedDocumentSection: (
    data: RequirementRelatedDocumentSectionData
  ) => void;
  requirementSourceImages?: RequirementImage[];
  requirementDocumentImages?: RequirementImage[];
  isRequirementEditable?: boolean;
};

const RequirementSourceCard: FC<RequirementSourceCardProps> = memo(
  ({
    data,
    index,
    onEdit,
    onDelete,
    onAddSection,
    onAddRelatedDocument,
    onAddRelatedDocumentSection,
    onDeleteRelatedDocumentSection,
    onEditRelatedDocumentSection,
    requirementSourceImages,
    requirementDocumentImages,
    isRequirementEditable = true,
  }) => {
    const [isExpanded, setIsExpanded] = useState(true);

    const requirementSource = data[0].requirementSource;
    const appendix = data[0].appendix;
    const sourceNumberType = requirementSourceNumberType(
      requirementSource?.id ?? ""
    );
    const isOrder = requirementSource?.id === RequirementSourceEnum.ORDER;
    const isRegulation =
      requirementSource?.id === RequirementSourceEnum.REGULATION;

    return (
      <Accordion
        expanded={isExpanded}
        onChange={(_, expanded) => {
          setIsExpanded(expanded);
        }}
        sx={{
          marginTop: "1rem",
          border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
          borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
          "&.Mui-expanded:first-of-type": {
            marginTop: "1rem",
          },
        }}
      >
        <AccordionSummary
          aria-controls={`panel${index}-content`}
          id={`requirement-source-panel${index}-header`}
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
              <strong>
                {requirementSource?.name}
                {isOrder && ` — ${data[0].order?.order_number ?? ""}`}
                {requirementSource?.id === RequirementSourceEnum.EACA &&
                  ` #${data[0].amendmentNumber}`}
              </strong>
              {appendix && ` (Appendix ${appendix.appendix_no})`}
            </Typography>
          </Box>
          {isExpanded && !isOrder && isRequirementEditable && (
            <Button
              variant="text"
              color="secondary"
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onAddSection(data[0]);
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
            >
              {sourceNumberType}
            </Button>
          )}
        </AccordionSummary>
        <AccordionDetails sx={{ padding: "0" }}>
          <Stack>
            {data.map((item, idx) => (
              <Box key={idx}>
                <Box
                  sx={{
                    padding: "0.5rem 1rem 1rem",
                    borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
                  }}
                >
                  {isRequirementEditable && (
                    <Box
                      display={"flex"}
                      justifyContent={"space-between"}
                      gap={".25rem"}
                    >
                      <Box display={"flex"} gap={".25rem"}>
                        <Tooltip title="Edit" arrow>
                          <IconButton
                            size="small"
                            color="secondary"
                            onClick={() => onEdit(item, idx)}
                            data-testid={`requirement-source-edit-${index}`}
                          >
                            <EditOutlined />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete" arrow>
                          <IconButton
                            size="small"
                            color="secondary"
                            onClick={() => onDelete(item)}
                            data-testid={`requirement-source-delete-${index}`}
                          >
                            <DeleteOutlineRounded />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      <Tooltip
                        title={`Add an extract from ${
                          !isOrder ? "a management plan or" : ""
                        } other document to support this requirement`}
                        arrow
                      >
                        <Button
                          variant="text"
                          color="secondary"
                          size="small"
                          onClick={() => onAddRelatedDocument(item)}
                          startIcon={<AddRounded />}
                          data-testid={`requirement-source-add-related-document-${index}`}
                          sx={{
                            backgroundColor: "transparent",
                            paddingY: 0,
                            height: "auto",
                            "& .MuiButton-startIcon": {
                              mr: 0,
                            },
                          }}
                        >
                          {isOrder || isRegulation
                            ? "Other Document"
                            : "Management Plan / Other Document"}
                        </Button>
                      </Tooltip>
                    </Box>
                  )}
                  {isRegulation && (
                    <Grid container spacing={2} mb={1}>
                      <Grid item xs={4}>
                        <Typography
                          variant="subtitle2"
                          color={BCDesignTokens.typographyColorPlaceholder}
                        >
                          Regulation #
                        </Typography>
                        <Typography variant="body2" fontWeight={700}>
                          {item.regulationNumber}
                        </Typography>
                      </Grid>
                      <Grid item xs={8}>
                        <Typography
                          variant="subtitle2"
                          color={BCDesignTokens.typographyColorPlaceholder}
                        >
                          Title:
                        </Typography>
                        <Typography variant="body2">
                          {item.requirementSourceTitle}
                        </Typography>
                      </Grid>
                    </Grid>
                  )}
                  {!isOrder && (
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography
                          variant="subtitle2"
                          color={BCDesignTokens.typographyColorPlaceholder}
                        >
                          {sourceNumberType} #:
                        </Typography>
                        <Typography variant="body2" fontWeight={700}>
                          {String(
                            item[
                              `${sourceNumberType.toLowerCase()}Number` as keyof RequirementSourceFormData
                            ] ?? ""
                          )}
                        </Typography>
                      </Grid>
                      <Grid item xs={8}>
                        <Typography
                          variant="subtitle2"
                          color={BCDesignTokens.typographyColorPlaceholder}
                        >
                          Title:
                        </Typography>
                        <Typography variant="body2">{item.title}</Typography>
                      </Grid>
                    </Grid>
                  )}
                  <Box sx={{ marginTop: ".5rem" }}>
                    <Typography
                      variant="subtitle2"
                      color={BCDesignTokens.typographyColorPlaceholder}
                    >
                      Description:
                    </Typography>
                    <ParagraphWithReadMore
                      key={`req-src-card-desc-${item.id}`}
                      maxHeight={84}
                      isFormatted={true}
                      renderTypography={
                        <Box
                          sx={{
                            fontSize: "0.875rem",
                            color: BCDesignTokens.typographyColorPrimary,
                          }}
                          dangerouslySetInnerHTML={{
                            __html: sanitizeHtml(generateHtmlWithEmbeddedImages(
                              item.description?.html ?? "",
                              requirementSourceImages?.filter(
                                (image) => image.req_detail_id === item.id
                              ) ?? []
                            )),
                          }}
                        />
                      }
                    />
                  </Box>
                </Box>
                {item.relatedDocuments?.map((relatedDocument, index) => (
                  <RequirementRelatedDocumentCard
                    key={index}
                    index={index}
                    relatedDocument={relatedDocument}
                    relatedDocumentImages={requirementDocumentImages ?? []}
                    onAddRelatedDocumentSection={() =>
                      onAddRelatedDocumentSection(relatedDocument, item)
                    }
                    onDeleteRelatedDocumentSection={
                      onDeleteRelatedDocumentSection
                    }
                    onEditRelatedDocumentSection={(section, sectionIndex) => onEditRelatedDocumentSection(section, sectionIndex)}
                    isRequirementEditable={isRequirementEditable}
                  />
                ))}
              </Box>
            ))}
          </Stack>
        </AccordionDetails>
      </Accordion>
    );
  }
);

export default RequirementSourceCard;
