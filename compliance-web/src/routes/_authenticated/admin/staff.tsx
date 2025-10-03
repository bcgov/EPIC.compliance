import StaffModal from "@/components/App/Staff/StaffModal";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import Unauthorized from "@/components/Shared/Unauthorized";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useDeleteStaff, useStaffUsersData } from "@/hooks/useStaff";
import { StaffUser } from "@/models/Staff";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import { DeleteOutlineRounded, EditOutlined } from "@mui/icons-material";
import { Box, Chip, IconButton } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { MRT_ColumnDef } from "material-react-table";
import { useEffect, useMemo, useState } from "react";

export const Route = createFileRoute("/_authenticated/admin/staff")({
  component: AuthorizedStaffComponent,
});

function AuthorizedStaffComponent() {
  const isRouteAllowed = useIsRolesAllowed([
    KC_USER_GROUPS.SUPERUSER,
    KC_USER_GROUPS.ADMIN,
  ]);

  if (isRouteAllowed) {
    return <Staff />;
  } else {
    return <Unauthorized />;
  }
}

const STAFF_MODAL_WIDTH = "520px";

export function Staff() {
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useModal();
  const { data: staffUsersList, isLoading } = useStaffUsersData({
    isActive: false,
    otherPositions: false,
  });

  const [positionList, setPositionList] = useState<string[]>([]);
  const [supervisorList, setSupervisorList] = useState<string[]>([]);
  const [deputyList, setDeputyList] = useState<string[]>([]);
  const [permissionList, setPermissionList] = useState<string[]>([]);

  useEffect(() => {
    setPositionList(
      [
        ...new Set(staffUsersList?.map((staff) => staff.position?.name ?? "")),
      ].filter(Boolean)
    );
    setSupervisorList(
      [
        ...new Set(
          staffUsersList?.map((staff) => staff.supervisor?.name ?? "")
        ),
      ].filter(Boolean)
    );
    setDeputyList(
      [
        ...new Set(
          staffUsersList?.map((staff) => staff.deputy_director?.name ?? "")
        ),
      ].filter(Boolean)
    );
    setPermissionList(
      [
        ...new Set(
          staffUsersList?.map((staff) => staff.permission?.name ?? "")
        ),
      ].filter(Boolean)
    );
  }, [staffUsersList]);

  const handleOnSubmit = (submitMsg: string) => {
    queryClient.invalidateQueries({ queryKey: ["staff-users"] });
    setClose();
    notify.success(submitMsg);
  };

  const handleAddStaffModal = () => {
    setOpen({
      content: <StaffModal onSubmit={handleOnSubmit} />,
      width: STAFF_MODAL_WIDTH,
    });
  };

  const handleEdit = (staff: StaffUser) => {
    setOpen({
      content: <StaffModal staff={staff} onSubmit={handleOnSubmit} />,
      width: STAFF_MODAL_WIDTH,
    });
  };

  /** Staff Deletion START */

  const onDeleteSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ["staff-users"] });
    setClose();
    notify.success("Staff deleted successfully!");
  };

  const { mutate: deleteUser } = useDeleteStaff(onDeleteSuccess);

  const handleDelete = (id: number) => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Delete Staff User?"
          description="You are about to delete this staff user. Are you sure?"
          confirmButtonText="Delete"
          onConfirm={() => {
            if (id !== null) {
              deleteUser(id);
            }
          }}
        />
      ),
    });
  };

  /** Staff Deletion END */

  const columns = useMemo<MRT_ColumnDef<StaffUser>[]>(
    () => [
      {
        accessorKey: "name",
        header: "Name",
        filterFn: "contains",
      },
      {
        accessorKey: "position.name",
        header: "Position",
        filterVariant: "multi-select",
        filterSelectOptions: positionList,
      },
      {
        accessorFn: (row) => row.supervisor?.name,
        id: "supervisor.name",
        header: "Supervisor",
        filterVariant: "multi-select",
        filterSelectOptions: supervisorList,
      },
      {
        accessorFn: (row) => row.deputy_director?.name,
        id: "deputy_director.name",
        header: "Deputy Director",
        filterVariant: "multi-select",
        filterSelectOptions: deputyList,
      },
      {
        accessorFn: (row) => row.permission?.id,
        header: "Permission Level",
        filterVariant: "multi-select",
        filterSelectOptions: permissionList,
      },
      {
        accessorFn: (row) => (row.is_active ? "Active" : "Inactive"),
        header: "Status",
        Cell: ({ row }) => {
          return (
            <Chip
              label={row.original.is_active ? "Active" : "Inactive"}
              style={{
                backgroundColor: row.original.is_active
                  ? BCDesignTokens.supportSurfaceColorSuccess
                  : BCDesignTokens.surfaceColorPrimaryButtonDisabled,
              }}
              variant="outlined"
              size="small"
            />
          );
        },
        filterVariant: "multi-select",
        filterSelectOptions: ["Active", "Inactive"],
      },
    ],
    [deputyList, permissionList, positionList, supervisorList]
  );
  return (
    <>
      <MasterDataTable
        columns={columns}
        data={staffUsersList ?? []}
        initialState={{
          sorting: [
            {
              id: "name",
              desc: false,
            },
          ],
          columnFilters: [
            {
              id: "Status",
              value: ["Active"],
            },
          ],
        }}
        state={{
          isLoading: isLoading,
          showGlobalFilter: true,
        }}
        enableRowActions={true}
        renderRowActions={({ row }) => (
          <Box gap={".25rem"} display={"flex"}>
            <IconButton
              aria-label="edit"
              onClick={() => handleEdit(row.original)}
            >
              <EditOutlined />
            </IconButton>
            <IconButton
              aria-label="delete"
              onClick={() => handleDelete(row.original.id)}
            >
              <DeleteOutlineRounded />
            </IconButton>
          </Box>
        )}
        titleToolbarProps={{
          tableTitle: "Staff",
          tableAddRecordButtonText: "Staff Member",
          tableAddRecordFunction: () => handleAddStaffModal(),
          tableAddRecordButtonVisibility: true,
        }}
      />
    </>
  );
}
