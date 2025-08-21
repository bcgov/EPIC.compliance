import ModalActions from "@/components/Shared/Modals/ModalActions";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import {
  useAddStaff,
  useAuthUsersData,
  usePermissionsData,
  usePositionsData,
  useUpdateStaff,
} from "@/hooks/useStaff";
import { AuthUser } from "@/models/AuthUser";
import { Permission } from "@/models/Permission";
import { Position } from "@/models/Position";
import { StaffAPIData, StaffFormData, StaffUser } from "@/models/Staff";
import { yupResolver } from "@hookform/resolvers/yup";
import { DialogContent } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import StaffForm from "./StaffForm";

type StaffModalProps = {
  onSubmit: (submitMsg: string) => void;
  staff?: StaffUser;
};

const staffFormSchema = yup.object().shape({
  name: yup.object<AuthUser>().nullable().required("Name is required"),
  position: yup.object<Position>().nullable().required("Position is required"),
  deputyDirector: yup.object<StaffUser>().nullable(),
  supervisor: yup.object<StaffUser>().nullable(),
  permission: yup
    .object<Permission>()
    .nullable()
    .required("Permission is required"),
  isActive: yup.bool().required()
});

type StaffSchemaType = yup.InferType<typeof staffFormSchema>;

const initFormData: StaffFormData = {
  name: undefined,
  position: undefined,
  deputyDirector: undefined,
  supervisor: undefined,
  permission: undefined,
  isActive: true,
};

const StaffModal: React.FC<StaffModalProps> = ({ onSubmit, staff }) => {
  const queryClient = useQueryClient();

  const { data: usersList } = useAuthUsersData();
  const { data: positionsList } = usePositionsData();
  const { data: permissionsList } = usePermissionsData();
  const staffUsersList: StaffUser[] | undefined = queryClient.getQueryData([
    "staff-users",
  ]);

  const defaultValues = useMemo<StaffFormData>(() => {
    if (staff) {
      return {
        name:
          usersList?.find((item) => item.username === staff.auth_user_guid) ||
          undefined,
        position: staff.position || undefined,
        permission:
          permissionsList?.find((item) => item.id === staff.permission?.id) ||
          undefined,
        deputyDirector:
          staffUsersList?.find(
            (item) => item.id === staff.deputy_director_id
          ) || undefined,
        supervisor:
          staffUsersList?.find((item) => item.id === staff.supervisor_id) ||
          undefined,
        isActive: staff.is_active
      };
    }
    return initFormData;
  }, [staff, usersList, permissionsList, staffUsersList]);

  const methods = useForm<StaffSchemaType>({
    resolver: yupResolver(staffFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    if (staff) {
      reset(defaultValues);
    }
  }, [defaultValues, reset, staff]);

  const onSuccess = () => {
    onSubmit(staff ? "Successfully updated!" : "Successfully added!");
  };

  const { mutate: addStaff, isPending: isPendingAddStaff } = useAddStaff(onSuccess);
  const { mutate: updateStaff, isPending: isPendingUpdateStaff } = useUpdateStaff(onSuccess);

  const onSubmitHandler = (data: StaffSchemaType) => {
    const staffData: StaffAPIData = {
      auth_user_guid: (data.name as AuthUser)?.username ?? "",
      permission: (data.permission as Permission)?.id ?? "",
      position_id: (data.position as Position)?.id ?? "",
      deputy_director_id: (data.deputyDirector as StaffUser)?.id,
      supervisor_id: (data.supervisor as StaffUser)?.id,
      is_active: data.isActive
    };
    if (staff) {
      updateStaff({ id: staff.id, staff: staffData });
    } else {
      addStaff(staffData);
    }
    queryClient.invalidateQueries({
      queryKey: ["staff-users"],
    });
  };

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmitHandler)}>
          <ModalTitleBar
            title={staff ? (staff.name ?? "") : "Add Staff Member"}
          />
          <DialogContent dividers>
            <StaffForm
              existingStaff={staff}
              authUsersList={usersList}
              positionsList={positionsList}
              permissionsList={permissionsList}
              staffUsersList={staffUsersList}
            />
          </DialogContent>
          <ModalActions
            primaryActionButtonText={staff ? "Save" : "Add"}
            isLoading={isPendingAddStaff || isPendingUpdateStaff}
          />
        </form>
      </FormProvider>
    </>
  );
};

export default StaffModal;
