import React from "react";
import { PendingItem } from "@/models/Inspection";

interface InspectionPendingEnforcementsDescriptionProps {
  pendingEnforcements: PendingItem[] | undefined;
}

const InspectionPendingEnforcementsDescription: React.FC<
  InspectionPendingEnforcementsDescriptionProps
> = ({ pendingEnforcements }) => {
  if (!pendingEnforcements || pendingEnforcements.length === 0) {
    return <div>No pending items found.</div>;
  }
  // Check to see at least one item is not issued
  const nonIssuedItems = pendingEnforcements.some(
    (item) => !item.is_issued
  );

  return (
    <div>
      <div style={{ marginBottom: "16px" }}>
        One or more Enforcement actions are incomplete.
      </div>
      {nonIssuedItems && <div style={{ marginBottom: "16px" }}>
        Following Enforcement documents have not been issued:
      </div>}
      <ul style={{ paddingLeft: "20px", margin: 0 }}>
        {Array.from(new Set(pendingEnforcements.map(item => item.item.name)))
          .map((itemName, index) => {
            const itemsWithSameName = pendingEnforcements.filter(item => item.item.name === itemName);
            const itemNumbers = itemsWithSameName
              .map(item => item.item_number)
              .filter(Boolean)
              .join(", ");
            
            return (
              <li key={index} style={{ marginBottom: "4px" }}>
                <span style={{ fontWeight: "bold" }}>
                  {itemName}
                </span>{" "}
                {itemNumbers && (
                  <span>
                    {itemNumbers}
                  </span>
                )}
              </li>
            );
          })}
      </ul>
      <div style={{ marginTop: "16px" }}>
        Please resolve these items and try again.
      </div>
    </div>
  );
};

export default InspectionPendingEnforcementsDescription;
