import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledSwitch from "@/components/Shared/Controlled/ControlledSwitch";
import { AuthUser } from "@/models/AuthUser";
import { Permission } from "@/models/Permission";
import { Position } from "@/models/Position";
import { StaffUser } from "@/models/Staff";
import { STAFF_USER_POSITION } from "@/utils/constants";
import { Stack } from "@mui/material";
import React, { useMemo } from "react";

type StaffFormProps = {
  existingStaff?: StaffUser;
  authUsersList?: AuthUser[];
  positionsList?: Position[];
  permissionsList?: Permission[];
  staffUsersList?: StaffUser[];
};

const StaffForm: React.FC<StaffFormProps> = ({
  existingStaff,
  permissionsList,
  positionsList,
  authUsersList,
  staffUsersList,
}) => {
  const deputyDirectors = useMemo(
    () =>
      staffUsersList?.filter((p) => p.position_id == STAFF_USER_POSITION.DEPUTY_DIRECTOR),
    [staffUsersList]
  );
  return (
    <>
      <ControlledAutoComplete
        name="name"
        label="Name"
        placeholder="Search for a Name"
        options={authUsersList ?? []}
        getOptionLabel={(option) => `${option.first_name} ${option.last_name}`}
        getOptionKey={(option) => option.id}
        isOptionEqualToValue={(option, value) => option.id === value.id}
        disabled={!!existingStaff}
        isRequired={true}
      />
      <ControlledAutoComplete
        name="position"
        label="Position"
        options={positionsList ?? []}
        getOptionLabel={(option) => option.name}
        getOptionKey={(option) => option.id}
        isOptionEqualToValue={(option, value) => option.id === value.id}
        isRequired={true}
      />
      <Stack direction="row" spacing={1}>
        <ControlledAutoComplete
          name="deputyDirector"
          label="Deputy Director"
          placeholder="Search for a Name"
          options={deputyDirectors ?? []}
          getOptionLabel={(option) => option.name}
          getOptionKey={(option) => option.id}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          fullWidth
        />
        <ControlledAutoComplete
          name="supervisor"
          label="Supervisor"
          placeholder="Search for a Name"
          options={staffUsersList ?? []}
          getOptionLabel={(option) => option.name}
          getOptionKey={(option) => option.id}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          fullWidth
        />
      </Stack>
      <ControlledAutoComplete
        name="permission"
        label="Permission"
        options={permissionsList ?? []}
        getOptionLabel={(option) => option.name}
        getOptionKey={(option) => option.id}
        isOptionEqualToValue={(option, value) => option.id === value.id}
        isRequired={true}
      />
      <ControlledSwitch name="isActive" label="Active" />
    </>
  );
};

export default StaffForm;
