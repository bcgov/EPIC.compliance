import { CaseFileOpenItems } from "@/models/CaseFileOpenItems";
import { InspectionStatusEnum } from "@/utils/constants";
import { Box, Link, Typography } from "@mui/material";
import React from "react";

interface CaseFileOpenItemsDescriptionProps {
  caseFileOpenItems: CaseFileOpenItems | undefined;
  onOpenItemClick: (url: string, params: { [key: string]: string }) => void;
}

const CaseFileOpenItemsDescription: React.FC<CaseFileOpenItemsDescriptionProps> = ({
  caseFileOpenItems,
  onOpenItemClick,
}) => {

  if (!caseFileOpenItems?.has_open_items) {
    return (
      <div>
        Are you sure you want to close this case file? This action cannot be
        undone without reopening the case file.
      </div>
    );
  }

  const linkToInspection = (inspectionNumber?: string) => {
    if (!inspectionNumber) return null;
    
    return (
      <>
        <br />
        <Typography variant="caption">
          Linked to inspection:{" "}
          <Link
            underline="hover"
            sx={{ cursor: "pointer" }}
            onClick={() => {
              onOpenItemClick("/ce-database/inspections/$inspectionNumber", {
                inspectionNumber: inspectionNumber,
              });
            }}
          >
            {inspectionNumber}
          </Link>
        </Typography>
      </>
    );
  };

  const openInspections = caseFileOpenItems.inspections.filter(i => i.status.name === InspectionStatusEnum.OPEN);

  return (
    <Box sx={{ overflow: "auto", maxHeight: "570px" }}>
      <Typography variant="body1" mb={2}>
        This case file contains open items that must be closed before
        proceeding:
      </Typography>

      {openInspections.length > 0 && (
        <Box>
          <strong>Inspections:</strong>
          <ul style={{ marginTop: 8 }}>
            {openInspections.map((inspection, index) => (
              <li key={index}>
                <Link
                  underline="hover"
                  sx={{ cursor: "pointer" }}
                  onClick={() => {
                    onOpenItemClick(
                      "/ce-database/inspections/$inspectionNumber",
                      { inspectionNumber: inspection.number }
                    );
                  }}
                >
                  {inspection.number}
                </Link>
              </li>
            ))}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.complaints.length > 0 && (
        <Box>
          <strong>Complaints:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.complaints.map((complaint, index) => (
              <li key={index}>
                <Link
                  underline="hover"
                  sx={{ cursor: "pointer" }}
                  onClick={() => {
                    onOpenItemClick(
                      "/ce-database/complaints/$complaintNumber",
                      { complaintNumber: complaint.number }
                    );
                  }}
                >
                  {complaint.number}
                </Link>
              </li>
            ))}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.orders.length > 0 && (
        <Box>
          <strong>Orders:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.orders.map((order, index) => (
                <li key={index}>
                  {order.number}
                  {linkToInspection(order.ir_number)}
                </li>
            ))}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.warning_letters.length > 0 && (
        <Box>
          <strong>Warning Letters:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.warning_letters.map((warningLetter, index) => (
                <li key={index}>
                  {warningLetter.number}
                  {linkToInspection(warningLetter.ir_number)}
                </li>
            ))}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.violation_tickets.length > 0 && (
        <Box>
          <strong>Violation Tickets:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.violation_tickets.map(
              (violationTicket, index) => (
                <li key={index}>
                  {violationTicket.number}
                  {linkToInspection(violationTicket.ir_number)}
                </li>
              )
            )}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.administrative_penalties.length > 0 && (
        <Box>
          <strong>Administrative Penalties:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.administrative_penalties.map(
              (administrativePenalty, index) => (
                <li key={index}>
                  {administrativePenalty.number}
                  {linkToInspection(administrativePenalty.ir_number)}
                </li>
              )
            )}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.charge_recommendations.length > 0 && (
        <Box>
          <strong>Charge Recommendations:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.charge_recommendations.map(
              (chargeRecommendation, index) => (
                <li key={index}>
                  {chargeRecommendation.number}
                  {linkToInspection(chargeRecommendation.ir_number)}
                </li>
              )
            )}
          </ul>
        </Box>
      )}

      {caseFileOpenItems.restorative_justice.length > 0 && (
        <Box>
          <strong>Restorative Justice:</strong>
          <ul style={{ marginTop: 8 }}>
            {caseFileOpenItems.restorative_justice.map(
              (restorativeJustice, index) => (
                <li key={index}>
                  {restorativeJustice.number}
                  {linkToInspection(restorativeJustice.ir_number)}
                </li>
              )
            )}
          </ul>
        </Box>
      )}

      <Typography variant="body1" pt={1}>
        Please close these items and try again.
      </Typography>
    </Box>
  );
};

export default CaseFileOpenItemsDescription;
