import React from "react";
import { PendingItem } from "@/models/Inspection";

interface InspectionPendingEnforcementsDescriptionProps {
  pendingEnforcements: PendingItem[] | undefined;
}

interface PendingItemsListProps {
  items: PendingItem[];
  filterCondition: (item: PendingItem) => boolean;
}

const PendingItemsList: React.FC<PendingItemsListProps> = ({ items, filterCondition }) => {
  const filteredItems = items.filter(filterCondition);
  
  return (
    <ul style={{ paddingLeft: "30px", marginBottom: "16px" }}>
      {Array.from(new Set(filteredItems.map(item => item.item.name)))
        .map((itemName, index) => {
          const itemsWithSameName = filteredItems.filter(item => item.item.name === itemName);
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
  );
};

const InspectionPendingEnforcementsDescription: React.FC<
  InspectionPendingEnforcementsDescriptionProps
> = ({ pendingEnforcements }) => {
  if (!pendingEnforcements || pendingEnforcements.length === 0) {
    return <div>No pending items found.</div>;
  }
  
  // Check to see at least one item is not created
  const nonCreatedItems = pendingEnforcements.some(
    (item) => item.is_created === false
  );
  
  // Check to see at least one item is not issued
  const nonIssuedItems = pendingEnforcements.some(
    (item) => item.is_issued === false
  );

  return (
    <div>      
      {nonCreatedItems && (
        <>
          <div style={{ marginBottom: "16px" }}>
        One or more Enforcement actions are incomplete.
      </div>
          <PendingItemsList 
            items={pendingEnforcements} 
            filterCondition={(item) => item.is_created === false} 
          />
        </>
      )}
      
      {nonIssuedItems && (
        <>
          <div style={{ marginBottom: "16px" }}>
            Following Enforcement documents have not been issued:
          </div>
          <PendingItemsList 
            items={pendingEnforcements} 
            filterCondition={(item) => item.is_issued === false} 
          />
        </>
      )}
      
      <div>
        Please resolve these items and try again.
      </div>
    </div>
  );
};

export default InspectionPendingEnforcementsDescription;
