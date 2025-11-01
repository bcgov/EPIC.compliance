import AppendicesContainer from "@/components/App/Inspections/Profile/Requirements/Appendices/AppendicesContainer";
import ImagesContainer from "@/components/App/Inspections/Profile/Requirements/Images/ImagesContainer";
import RequirementRelatedDocumentModal from "@/components/App/Inspections/Profile/Requirements/RequirementSource/RequirementRelatedDocumentModal";
import RequirementSourceCard from "@/components/App/Inspections/Profile/Requirements/RequirementSource/RequirementSourceCard";
import RequirementSourceModal from "@/components/App/Inspections/Profile/Requirements/RequirementSource/RequirementSourceModal";
import {
  ImageTypeEnum,
  groupRequirementSourcesByType,
  requirementSourceNumberType,
} from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { useAppendicesData } from "@/hooks/useAppendices";
import {
  RequirementRelatedDocumentData,
  RequirementRelatedDocumentSectionData,
  RequirementSourceFormData,
} from "@/models/InspectionRequirementSource";
import { useModal } from "@/store/modalStore";
import { AddRounded } from "@mui/icons-material";
import { Box, Button } from "@mui/material";
import { FC, useEffect, useMemo, useState } from "react";
import { useRequirementStore } from "./requirementStore";
import { CaseFile } from "@/models/CaseFile";
import { MODAL_WIDTHS } from "@/utils/constants";
import { useRequirementDocumentImages, useRequirementSourceImages } from "@/hooks/useInspectionRequirements";

interface RequirementFormRightProps {
  onDataChange: (data: RequirementSourceFormData[]) => void;
  requirementSourceFormDataList: RequirementSourceFormData[];
  inspectionId: number;
  caseFile: CaseFile;
  requirementId: number;
  isRegulatoryConsideration: boolean;
  isRequirementEditable?: boolean;
}

const RequirementFormRight: FC<RequirementFormRightProps> = ({
  onDataChange,
  requirementSourceFormDataList,
  inspectionId,
  caseFile,
  requirementId,
  isRegulatoryConsideration,
  isRequirementEditable = true,
}) => {
  const { setOpen, setClose } = useModal();

  // Helper function to synchronize requirementSourceTitle across all items
  const syncRequirementSourceTitle = (items: RequirementSourceFormData[]) => {
    const firstItemTitle = items[0]?.requirementSourceTitle;
    if (firstItemTitle) {
      items.forEach(item => {
        item.requirementSourceTitle = firstItemTitle;
      });
    }
    return items;
  };

  // Helper function to synchronize document titles across all related documents within the same requirement source
  const syncDocumentTitles = (items: RequirementSourceFormData[]) => {
    items.forEach(item => {
      if (item.relatedDocuments && item.relatedDocuments.length > 0) {
        const firstDocumentTitle = item.relatedDocuments[0]?.documentTitle;
        if (firstDocumentTitle) {
          item.relatedDocuments.forEach(doc => {
            doc.documentTitle = firstDocumentTitle;
          });
        }
      }
    });
    return items;
  };
  const [requirementSourceFormData, setRequirementSourceFormData] = useState<
    RequirementSourceFormData[]
  >(requirementSourceFormDataList);
  const { data: appendixList } = useAppendicesData(inspectionId);
  const { data: requirementSourceImages } = useRequirementSourceImages(
    inspectionId,
    requirementId
  );
  const { data: requirementDocumentImages } = useRequirementDocumentImages(
    inspectionId,
    requirementId
  );
  const { setIsDataChanged } = useRequirementStore();

  useEffect(() => {
    onDataChange(requirementSourceFormData);
  }, [requirementSourceFormData, onDataChange]);

  const closeModal = () => {
    setClose();
    setIsDataChanged(true);
  };

  const handleOnAddSubmit = (data: RequirementSourceFormData) => {
    setRequirementSourceFormData((prevData) => {
      const updated = syncRequirementSourceTitle([...prevData, data]);
      onDataChange(updated);
      return updated;
    });
    closeModal();
  };

  const handleOnEditSubmit = (data: RequirementSourceFormData) => {
    setRequirementSourceFormData((prevData) => {
      const mapped = prevData.map((item) => {
        if (item.id !== data.id) return item;

        // Merge arrays explicitly to avoid losing existing entries when undefined
        const mergedImages =
          data.images !== undefined ? data.images : item.images;
        const mergedRelatedDocs =
          data.relatedDocuments !== undefined
            ? data.relatedDocuments
            : item.relatedDocuments;

        return {
          ...item,
          ...data,
          images: mergedImages,
          relatedDocuments: mergedRelatedDocs,
        };
      });
      const updated = syncRequirementSourceTitle(mapped);
      // Trigger onDataChange immediately with the updated data
      onDataChange(updated);
      return updated;
    });
    closeModal();
  };

  const handleOnDeleteSubmit = (data: RequirementSourceFormData) => {
    setRequirementSourceFormData((prevData) => {
      const filtered = prevData.filter((item) => item.id !== data.id);
      const updated = syncRequirementSourceTitle(filtered);
      onDataChange(updated);
      return updated;
    });
    closeModal();
  };

  const handleOnAddRelatedDocumentSubmit = (
    data: RequirementRelatedDocumentData
  ) => {
    setRequirementSourceFormData((prevData) => {
      const mapped = prevData.map((item) => {
        if (item.id === data.sourceFormId) {
          const existingDocumentIndex = item.relatedDocuments?.findIndex(
            (doc) => doc.id === data.id
          );
          if (
            item.relatedDocuments &&
            existingDocumentIndex !== undefined &&
            existingDocumentIndex >= 0
          ) {
            item.relatedDocuments[existingDocumentIndex] = data;
          } else {
            if (!item.relatedDocuments) {
              item.relatedDocuments = [];
            }
            item.relatedDocuments.push(data);
          }
          return item;
        }
        return item;
      });
      const titleSynced = syncRequirementSourceTitle(mapped);
      const updated = syncDocumentTitles(titleSynced);
      onDataChange(updated);
      return updated;
    });
    closeModal();
  };

  const handleOnDeleteRelatedDocumentSectionSubmit = (
    data: RequirementRelatedDocumentSectionData
  ) => {
    setRequirementSourceFormData((prevData) => {
      const mapped = prevData.map((item) => {
        if (item.id === data.sourceFormId) {
          return {
            ...item,
            relatedDocuments: item.relatedDocuments
              ?.map((doc) => {
                if (doc.id === data.relatedDocumentFormId) {
                  const updatedSections = doc.sections?.filter(
                    (section) => section.id !== data.id
                  );
                  return updatedSections?.length === 0
                    ? null
                    : { ...doc, sections: updatedSections };
                }
                return doc;
              })
              .filter((doc) => doc !== null),
          };
        }
        return item;
      });
      const titleSynced = syncRequirementSourceTitle(mapped);
      const updated = syncDocumentTitles(titleSynced);
      onDataChange(updated);
      return updated;
    });
    closeModal();
  };
  const handleAddRequirementSource = () => {
    setOpen({
      content: (
        <RequirementSourceModal
          onSubmit={handleOnAddSubmit}
          caseFile={caseFile}
          inspectionId={inspectionId}
          appendixList={appendixList}
        />
      ),
      width: MODAL_WIDTHS.REQUIREMENT_SOURCE,
    });
  };

  const handleEditRequirementSource = (
    data: RequirementSourceFormData,
    index: number
  ) => {
    setOpen({
      content: (
        <RequirementSourceModal
          onSubmit={handleOnEditSubmit}
          caseFile={caseFile}
          inspectionId={inspectionId}
          requirementSourceFormData={data}
          appendixList={appendixList}
          requirementSourceImages={
            requirementSourceImages?.filter(
              (image) => image.req_detail_id === data.id
            ) ?? []
          }
          isSectionModal={index > 0}
        />
      ),
      width: MODAL_WIDTHS.REQUIREMENT_SOURCE,
    });
  };

  const handleDeleteRequirementSource = (data: RequirementSourceFormData) => {
    const requirementSourceDetails = groupedData.get(
      data.requirementSource?.id ?? ""
    );
    const isLastSectionItem =
      requirementSourceDetails && requirementSourceDetails.length === 1;
    const sourceNumberType = requirementSourceNumberType(
      data.requirementSource?.id ?? ""
    ).toLowerCase();
    const sourceNumber =
      data[`${sourceNumberType}Number` as keyof RequirementSourceFormData];
    const description = isLastSectionItem
      ? `You are about to delete ${data.requirementSource?.name}.
      This is the primary requirement source. 
      Deleting it will also permanently remove all associated documents. 
      Are you sure you want to proceed?`
      : data.relatedDocuments?.length
        ? `You are about to delete ${sourceNumber} - ${data.title}.
        This ${sourceNumberType} has associated documents.
        Deleting this ${sourceNumberType} will also remove all associated documents from the system.
        Are you sure you want to proceed?`
        : `You are about to delete ${sourceNumber} - ${data.title}.
        Are you sure you want to proceed?`;
    setOpen({
      content: (
        <ConfirmationModal
          title="Delete Requirement Source?"
          description={description}
          confirmButtonText="Delete"
          onConfirm={() => handleOnDeleteSubmit(data)}
        />
      ),
    });
  };

  const handleAddRequirementSourceSection = (
    data: RequirementSourceFormData
  ) => {
    setOpen({
      content: (
        <RequirementSourceModal
          onSubmit={handleOnAddSubmit}
          caseFile={caseFile}
          inspectionId={inspectionId}
          requirementSource={data.requirementSource}
          requirementSourceTitle={data.requirementSourceTitle}
          order={data.order}
          appendixList={appendixList}
          isSectionModal={true}
        />
      ),
      width: MODAL_WIDTHS.REQUIREMENT_SOURCE,
    });
  };

  const handleAddRequirementRelatedDocument = (
    data: RequirementSourceFormData
  ) => {
    setOpen({
      content: (
        <RequirementRelatedDocumentModal
          onSubmit={handleOnAddRelatedDocumentSubmit}
          inspectionId={inspectionId}
          requirementSourceData={data}
          appendixList={appendixList}
        />
      ),
      width: MODAL_WIDTHS.REQUIREMENT_SOURCE,
    });
  };

  const handleAddRelatedDocumentSection = (
    docData: RequirementRelatedDocumentData,
    srcData: RequirementSourceFormData
  ) => {
    setOpen({
      content: (
        <RequirementRelatedDocumentModal
          onSubmit={handleOnAddRelatedDocumentSubmit}
          inspectionId={inspectionId}
          requirementSourceData={srcData}
          relatedDocumentData={docData}
          appendixList={appendixList}
          isEditSection={true}
        />
      ),
      width: MODAL_WIDTHS.REQUIREMENT_SOURCE,
    });
  };

  const filterSourceData = (data: RequirementRelatedDocumentSectionData) => {
    const srcData = requirementSourceFormData.find(
      (item) => item.id === data.sourceFormId
    );
    const docData = srcData?.relatedDocuments?.find(
      (doc) => doc.id === data.relatedDocumentFormId
    );
    return { srcData, docData };
  };

  const handleEditRelatedDocumentSection = (
    data: RequirementRelatedDocumentSectionData,
    sectionIndex: number
  ) => {
    const { srcData, docData } = filterSourceData(data);
    setOpen({
      content: (
        <RequirementRelatedDocumentModal
          onSubmit={handleOnAddRelatedDocumentSubmit}
          inspectionId={inspectionId}
          requirementSourceData={srcData!}
          relatedDocumentData={docData!}
          relatedDocumentSectionData={data}
          appendixList={appendixList}
          relatedDocumentImages={requirementDocumentImages?.filter(
            (image) => image.req_detail_doc_id === data.id
          ) ?? []}
          isEditSection={true}
          isSectionModal={sectionIndex > 0}
        />
      ),
      width: MODAL_WIDTHS.REQUIREMENT_SOURCE,
    });
  };

  const handleDeleteRequirementRelatedDocumentSection = (
    data: RequirementRelatedDocumentSectionData
  ) => {
    const { docData } = filterSourceData(data);
    const description = `You are about to delete this section: #${data.sectionNumber} - ${data.sectionTitle}.
    ${docData?.sections?.length === 1 ? "This will result in deleting the whole document." : ""}
    Are you sure you want to proceed?`;
    setOpen({
      content: (
        <ConfirmationModal
          title="Delete Section?"
          description={description}
          confirmButtonText="Delete"
          onConfirm={() => handleOnDeleteRelatedDocumentSectionSubmit(data)}
        />
      ),
    });
  };

  // Using the utility function instead of local implementation
  const groupedData = useMemo(
    () => groupRequirementSourcesByType(requirementSourceFormData),
    [requirementSourceFormData]
  );

  return (
    <Box
      sx={{
        padding: "1.5rem 1rem",
        width: "510px",
        overflow: "auto",
        boxSizing: "border-box",
      }}
    >
      {!isRegulatoryConsideration && isRequirementEditable && (
        <Button
          color="secondary"
          onClick={handleAddRequirementSource}
          startIcon={<AddRounded />}
        >
          Requirement Source
        </Button>
      )}
      {[...groupedData].map(([sourceId, items], index) => (
        <RequirementSourceCard
          key={sourceId}
          data={items}
          index={index}
          onEdit={handleEditRequirementSource}
          onDelete={handleDeleteRequirementSource}
          onAddSection={handleAddRequirementSourceSection}
          onAddRelatedDocument={handleAddRequirementRelatedDocument}
          onAddRelatedDocumentSection={handleAddRelatedDocumentSection}
          onEditRelatedDocumentSection={handleEditRelatedDocumentSection}
          onDeleteRelatedDocumentSection={
            handleDeleteRequirementRelatedDocumentSection
          }
          requirementSourceImages={requirementSourceImages}
          requirementDocumentImages={requirementDocumentImages}
          isRequirementEditable={isRequirementEditable}
        />
      ))}
      <ImagesContainer
        imageType={ImageTypeEnum.PHOTO}
        inspectionId={inspectionId}
        requirementId={requirementId}
        isRegulatoryConsideration={isRegulatoryConsideration}
        isRequirementEditable={isRequirementEditable}
      />
      <ImagesContainer
        imageType={ImageTypeEnum.FIGURE}
        inspectionId={inspectionId}
        requirementId={requirementId}
        isRegulatoryConsideration={isRegulatoryConsideration}
        isRequirementEditable={isRequirementEditable}
      />
      <AppendicesContainer
        inspectionId={inspectionId}
        isRequirementEditable={isRequirementEditable}
      />
    </Box>
  );
};

export default RequirementFormRight;
